from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseAgent
from app.db.models.analysis import Analysis


class AnalysisService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_analysis(
        self,
        dream_id: int,
        agent_name: str,
        agent_type: str,
        model_used: str,
        content: str,
    ) -> Analysis:
        analysis = Analysis(
            dream_id=dream_id,
            agent_name=agent_name,
            agent_type=agent_type,
            model_used=model_used,
            content=content,
        )
        self.db.add(analysis)
        await self.db.commit()
        await self.db.refresh(analysis)
        return analysis

    async def run_agent(
        self,
        agent: BaseAgent,
        dream_id: int,
        dream_content: str,
        context: str | None = None,
    ) -> Analysis:
        """Run any agent and save result to DB."""
        content = await agent.analyze(dream_content, context=context)
        return await self.create_analysis(
            dream_id=dream_id,
            agent_name=agent.name,
            agent_type=agent.agent_type,
            model_used=agent.model,
            content=content,
        )

    async def update_analysis_score(self, analysis_id: int, score: int) -> None:
        result = await self.db.execute(select(Analysis).where(Analysis.id == analysis_id))
        analysis = result.scalar_one_or_none()
        if analysis:
            analysis.score = score
            await self.db.commit()

    async def get_analyses_for_dream(self, dream_id: int) -> list[Analysis]:
        result = await self.db.execute(
            select(Analysis)
            .where(Analysis.dream_id == dream_id)
            .order_by(Analysis.created_at.asc())
        )
        return list(result.scalars().all())
