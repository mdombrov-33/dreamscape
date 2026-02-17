import asyncio
import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.emotion_specialist import EmotionSpecialist
from app.agents.generalist_agent import GeneralistAgent
from app.agents.rating_agent import RatingAgent
from app.agents.symbol_specialist import SymbolSpecialist
from app.agents.synthesizer_agent import SynthesizerAgent
from app.agents.theme_specialist import ThemeSpecialist
from app.core.database import AsyncSessionLocal, get_db
from app.core.models_config import DEFAULT_MODEL
from app.schemas.dream import DreamCreate, DreamRead, DreamUpdate
from app.services.analysis_service import AnalysisService
from app.services.dream_service import DreamService
from app.workflows.dream_analysis import run_dream_analysis

router = APIRouter()


@router.post("/dreams", response_model=DreamRead, status_code=status.HTTP_201_CREATED)
async def create_dream(
    dream: DreamCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new dream (no analysis)."""
    service = DreamService(db)
    created = await service.create_dream(content=dream.content, dream_date=dream.dream_date)
    return await service.get_dream_with_analyses(created.id)


@router.post("/dreams/{dream_id}/stream-generalist")
async def stream_generalist(
    dream_id: int,
    db: AsyncSession = Depends(get_db),
    model: str = Query(default=DEFAULT_MODEL),
):
    """Stream generalist analysis token by token. Saves to DB when complete."""
    dream = await DreamService(db).get_dream_by_id(dream_id)
    if not dream:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Dream {dream_id} not found")

    dream_content = dream.content

    async def generate():
        agent = GeneralistAgent(model=model)
        full_output = ""
        async for chunk in agent.analyze_stream(dream_content):
            full_output += chunk
            yield chunk

        async with AsyncSessionLocal() as save_db:
            await AnalysisService(save_db).create_analysis(
                dream_id=dream_id,
                agent_name=agent.name,
                agent_type=agent.agent_type,
                model_used=agent.model,
                content=full_output,
            )

    return StreamingResponse(generate(), media_type="text/plain")


@router.post("/dreams/{dream_id}/stream-analyze")
async def stream_analyze(
    dream_id: int,
    db: AsyncSession = Depends(get_db),
    model: str = Query(default=DEFAULT_MODEL),
):
    """Stream specialists + rating + synthesizer via SSE.

    Events:
      {"agent": "<name>", "token": "<chunk>"}   — token from a streaming agent
      {"event": "scores", "data": {...}}         — rating scores after specialists finish
      {"event": "done"}                          — pipeline complete
    """
    dream = await DreamService(db).get_dream_by_id(dream_id)
    if not dream:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Dream {dream_id} not found")

    analyses = await AnalysisService(db).get_analyses_for_dream(dream_id)
    generalist_row = next((a for a in analyses if a.agent_name == "generalist"), None)
    generalist_output = generalist_row.content if generalist_row else ""
    dream_content = dream.content

    async def generate():
        queue: asyncio.Queue = asyncio.Queue()

        async def stream_specialist(agent, context: str) -> str:
            full = ""
            async for chunk in agent.analyze_stream(dream_content, context=context):
                full += chunk
                await queue.put({"agent": agent.name, "token": chunk})
            await queue.put({"_done": agent.name, "content": full})
            return full

        symbol_agent = SymbolSpecialist(model=model)
        emotion_agent = EmotionSpecialist(model=model)
        theme_agent = ThemeSpecialist(model=model)

        tasks = [
            asyncio.create_task(stream_specialist(symbol_agent, generalist_output)),
            asyncio.create_task(stream_specialist(emotion_agent, generalist_output)),
            asyncio.create_task(stream_specialist(theme_agent, generalist_output)),
        ]

        # Drain queue until all three specialists signal done
        results: dict[str, str] = {}
        while len(results) < 3:
            event = await queue.get()
            if "_done" in event:
                results[event["_done"]] = event["content"]
            else:
                yield f"data: {json.dumps({'agent': event['agent'], 'token': event['token']})}\n\n"

        await asyncio.gather(*tasks)

        # Save specialists to DB
        async with AsyncSessionLocal() as save_db:
            service = AnalysisService(save_db)
            symbol_row = await service.create_analysis(
                dream_id=dream_id,
                agent_name=symbol_agent.name,
                agent_type=symbol_agent.agent_type,
                model_used=symbol_agent.model,
                content=results[symbol_agent.name],
            )
            emotion_row = await service.create_analysis(
                dream_id=dream_id,
                agent_name=emotion_agent.name,
                agent_type=emotion_agent.agent_type,
                model_used=emotion_agent.model,
                content=results[emotion_agent.name],
            )
            theme_row = await service.create_analysis(
                dream_id=dream_id,
                agent_name=theme_agent.name,
                agent_type=theme_agent.agent_type,
                model_used=theme_agent.model,
                content=results[theme_agent.name],
            )

        # Rate all three in parallel
        judge = RatingAgent(model=model)
        s_raw, e_raw, t_raw = await asyncio.gather(
            judge.analyze(dream_content, context=results[symbol_agent.name]),
            judge.analyze(dream_content, context=results[emotion_agent.name]),
            judge.analyze(dream_content, context=results[theme_agent.name]),
        )
        scores = {
            "symbol": judge.average_score(judge.parse_scores(s_raw)),
            "emotion": judge.average_score(judge.parse_scores(e_raw)),
            "theme": judge.average_score(judge.parse_scores(t_raw)),
        }

        async with AsyncSessionLocal() as score_db:
            service = AnalysisService(score_db)
            await service.update_analysis_score(symbol_row.id, scores["symbol"])
            await service.update_analysis_score(emotion_row.id, scores["emotion"])
            await service.update_analysis_score(theme_row.id, scores["theme"])

        yield f"data: {json.dumps({'event': 'scores', 'data': scores})}\n\n"

        # Stream synthesizer
        synth = SynthesizerAgent(model=model)
        context = (
            f"First-pass analysis:\n{generalist_output}\n\n"
            f"Symbol analysis:\n{results[symbol_agent.name]}\n\n"
            f"Emotion analysis:\n{results[emotion_agent.name]}\n\n"
            f"Theme analysis:\n{results[theme_agent.name]}"
        )
        synth_output = ""
        async for chunk in synth.analyze_stream(dream_content, context=context):
            synth_output += chunk
            yield f"data: {json.dumps({'agent': 'synthesizer', 'token': chunk})}\n\n"

        async with AsyncSessionLocal() as synth_db:
            await AnalysisService(synth_db).create_analysis(
                dream_id=dream_id,
                agent_name=synth.name,
                agent_type=synth.agent_type,
                model_used=synth.model,
                content=synth_output,
            )

        yield f"data: {json.dumps({'event': 'done'})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/dreams/{dream_id}/analyze", response_model=DreamRead)
async def analyze_dream(
    dream_id: int,
    db: AsyncSession = Depends(get_db),
    model: str = Query(default=DEFAULT_MODEL),
):
    """Non-streaming pipeline. Expects generalist already saved via stream-generalist."""
    dream_service = DreamService(db)
    dream = await dream_service.get_dream_by_id(dream_id)
    if not dream:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Dream {dream_id} not found")

    analyses = await AnalysisService(db).get_analyses_for_dream(dream_id)
    generalist_row = next((a for a in analyses if a.agent_name == "generalist"), None)
    generalist_output = generalist_row.content if generalist_row else ""

    await run_dream_analysis(
        dream_id=dream_id,
        dream=dream.content,
        model=model,
        generalist_output=generalist_output,
    )

    db.expire_all()
    return await dream_service.get_dream_with_analyses(dream_id)


@router.get("/dreams", response_model=list[DreamRead])
async def get_dreams(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
    db: AsyncSession = Depends(get_db),
):
    return await DreamService(db).get_all_dreams(skip=skip, limit=limit)


@router.get("/dreams/{dream_id}", response_model=DreamRead)
async def get_dream(
    dream_id: int,
    db: AsyncSession = Depends(get_db),
):
    dream = await DreamService(db).get_dream_by_id(dream_id)
    if not dream:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Dream {dream_id} not found")
    return dream


@router.put("/dreams/{dream_id}", response_model=DreamRead)
async def update_dream(
    dream_id: int,
    dream_update: DreamUpdate,
    db: AsyncSession = Depends(get_db),
):
    updated = await DreamService(db).update_dream(
        dream_id=dream_id,
        content=dream_update.content,
        dream_date=dream_update.dream_date,
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Dream {dream_id} not found")
    return updated


@router.delete("/dreams/{dream_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dream(
    dream_id: int,
    db: AsyncSession = Depends(get_db),
):
    success = await DreamService(db).delete_dream(dream_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Dream {dream_id} not found")
    return None
