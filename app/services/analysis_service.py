from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.simple_analyzer import SimpleDreamAnalyzer
from app.db.models.analysis import Analysis


class AnalysisService:
    """Service for managing dream analyses."""

    def __init__(self, db: AsyncSession):
        """Initialize service with database session."""
        self.db = db

    async def create_analysis(
        self,
        dream_id: int,
        agent_name: str,
        content: str,
    ) -> Analysis:
        """
        Create a new analysis.

        Args:
            dream_id: ID of the dream being analyzed
            agent_name: Name of the agent that created the analysis
            content: The analysis content

        Returns:
            The created Analysis object
        """
        analysis = Analysis(
            dream_id=dream_id,
            agent_name=agent_name,
            content=content,
        )

        self.db.add(analysis)
        await self.db.commit()
        await self.db.refresh(analysis)

        return analysis

    async def analyze_dream_with_agent(
        self,
        dream_id: int,
        dream_content: str,
    ) -> Analysis:
        """
        Analyze a dream using the simple analyzer agent.

        Args:
            dream_id: ID of the dream
            dream_content: The dream text to analyze

        Returns:
            The created Analysis object
        """
        agent = SimpleDreamAnalyzer()

        analysis_content = await agent.analyze(dream_content)

        return await self.create_analysis(
            dream_id=dream_id,
            agent_name=agent.name,
            content=analysis_content,
        )

    async def get_analyses_for_dream(self, dream_id: int) -> list[Analysis]:
        """
        Get all analyses for a specific dream.

        Args:
            dream_id: The dream ID

        Returns:
            List of Analysis objects
        """
        result = await self.db.execute(
            select(Analysis)
            .where(Analysis.dream_id == dream_id)
            .order_by(Analysis.created_at.desc())
        )
        return list(result.scalars().all())
