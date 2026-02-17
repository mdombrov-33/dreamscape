import asyncio

from loguru import logger

from app.agents.emotion_specialist import EmotionSpecialist
from app.agents.generalist_agent import GeneralistAgent
from app.agents.rating_agent import RatingAgent
from app.agents.symbol_specialist import SymbolSpecialist
from app.agents.synthesizer_agent import SynthesizerAgent
from app.agents.theme_specialist import ThemeSpecialist
from app.core.database import AsyncSessionLocal
from app.services.analysis_service import AnalysisService
from app.workflows.state import DreamAnalysisState


async def generalist_node(state: DreamAnalysisState) -> dict:
    agent = GeneralistAgent(model=state["model"])
    output = await agent.analyze(state["dream"])

    async with AsyncSessionLocal() as db:
        await AnalysisService(db).create_analysis(
            dream_id=state["dream_id"],
            agent_name=agent.name,
            agent_type=agent.agent_type,
            model_used=agent.model,
            content=output,
        )

    logger.info("Generalist done")
    return {"generalist": output}


async def specialists_node(state: DreamAnalysisState) -> dict:
    model = state["model"]
    context = state["generalist"]
    dream = state["dream"]

    symbol_agent = SymbolSpecialist(model=model)
    emotion_agent = EmotionSpecialist(model=model)
    theme_agent = ThemeSpecialist(model=model)

    logger.info(f"Running 3 specialists in parallel with {model}")
    symbol_out, emotion_out, theme_out = await asyncio.gather(
        symbol_agent.analyze(dream, context=context),
        emotion_agent.analyze(dream, context=context),
        theme_agent.analyze(dream, context=context),
    )

    async with AsyncSessionLocal() as db:
        service = AnalysisService(db)
        symbol_row = await service.create_analysis(
            dream_id=state["dream_id"],
            agent_name=symbol_agent.name,
            agent_type=symbol_agent.agent_type,
            model_used=symbol_agent.model,
            content=symbol_out,
        )
        emotion_row = await service.create_analysis(
            dream_id=state["dream_id"],
            agent_name=emotion_agent.name,
            agent_type=emotion_agent.agent_type,
            model_used=emotion_agent.model,
            content=emotion_out,
        )
        theme_row = await service.create_analysis(
            dream_id=state["dream_id"],
            agent_name=theme_agent.name,
            agent_type=theme_agent.agent_type,
            model_used=theme_agent.model,
            content=theme_out,
        )

    logger.info("Specialists done")
    return {
        "symbol": symbol_out,
        "emotion": emotion_out,
        "theme": theme_out,
        "symbol_analysis_id": symbol_row.id,
        "emotion_analysis_id": emotion_row.id,
        "theme_analysis_id": theme_row.id,
    }


async def rating_node(state: DreamAnalysisState) -> dict:
    judge = RatingAgent(model=state["model"])
    dream = state["dream"]

    logger.info("Rating specialist outputs")
    symbol_raw, emotion_raw, theme_raw = await asyncio.gather(
        judge.analyze(dream, context=state["symbol"]),
        judge.analyze(dream, context=state["emotion"]),
        judge.analyze(dream, context=state["theme"]),
    )

    scores = {
        "symbol": judge.average_score(judge.parse_scores(symbol_raw)),
        "emotion": judge.average_score(judge.parse_scores(emotion_raw)),
        "theme": judge.average_score(judge.parse_scores(theme_raw)),
    }
    logger.info(f"Scores: {scores}")

    async with AsyncSessionLocal() as db:
        service = AnalysisService(db)
        await service.update_analysis_score(state["symbol_analysis_id"], scores["symbol"])
        await service.update_analysis_score(state["emotion_analysis_id"], scores["emotion"])
        await service.update_analysis_score(state["theme_analysis_id"], scores["theme"])

    return {"scores": scores}


async def synthesizer_node(state: DreamAnalysisState) -> dict:
    agent = SynthesizerAgent(model=state["model"])

    context = (
        f"First-pass analysis:\n{state['generalist']}\n\n"
        f"Symbol analysis:\n{state['symbol']}\n\n"
        f"Emotion analysis:\n{state['emotion']}\n\n"
        f"Theme analysis:\n{state['theme']}"
    )

    output = await agent.analyze(state["dream"], context=context)

    async with AsyncSessionLocal() as db:
        await AnalysisService(db).create_analysis(
            dream_id=state["dream_id"],
            agent_name=agent.name,
            agent_type=agent.agent_type,
            model_used=agent.model,
            content=output,
        )

    logger.info("Synthesizer done")
    return {"synthesis": output}
