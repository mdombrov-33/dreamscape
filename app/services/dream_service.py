from collections.abc import Sequence
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.dream import Dream

if TYPE_CHECKING:
    from app.db.models.analysis import Analysis  # noqa: F401


class DreamService:
    """Service for managing dreams."""

    def __init__(self, db: AsyncSession):
        """Initialize service with database session."""
        self.db = db

    async def create_dream(
        self,
        content: str,
        dream_date: datetime | None = None,
    ) -> Dream:
        """
        Create a new dream.

        Args:
            content: The dream content/description
            dream_date: When the dream occurred (defaults to now)

        Returns:
            The created Dream object with id and timestamps
        """
        dream = Dream(
            content=content,
            dream_date=dream_date or datetime.now(),
        )

        self.db.add(dream)
        await self.db.commit()
        await self.db.refresh(dream)  # Get the generated id and timestamps

        return dream

    async def get_all_dreams(self, skip: int = 0, limit: int = 100) -> Sequence[Dream]:
        """
        Get all dreams with pagination.

        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            List of Dream objects
        """
        result = await self.db.execute(
            select(Dream)
            .offset(skip)
            .limit(limit)
            .order_by(Dream.created_at.desc())
            .options(selectinload(Dream.analyses))
        )
        return result.scalars().all()

    async def get_dream_by_id(self, dream_id: int) -> Dream | None:
        """
        Get a dream by its ID.

        Args:
            dream_id: The dream ID to fetch

        Returns:
            Dream object if found, None otherwise
        """
        result = await self.db.execute(
            select(Dream).where(Dream.id == dream_id).options(selectinload(Dream.analyses))
        )
        return result.scalar_one_or_none()

    async def get_dream_with_analyses(self, dream_id: int) -> Dream | None:
        """
        Get a dream by ID with all its analyses eagerly loaded.

        Args:
            dream_id: The dream ID to fetch

        Returns:
            Dream object with analyses relationship loaded, or None if not found
        """
        result = await self.db.execute(
            select(Dream)
            .where(Dream.id == dream_id)
            .options(selectinload(Dream.analyses))  # Eagerly load analyses
        )
        return result.scalar_one_or_none()

    async def update_dream(
        self,
        dream_id: int,
        content: str | None = None,
        dream_date: datetime | None = None,
    ) -> Dream | None:
        """
        Update a dream.

        Args:
            dream_id: ID of dream to update
            content: New content (if provided)
            dream_date: New dream date (if provided)

        Returns:
            Updated Dream object, or None if not found
        """
        dream = await self.get_dream_by_id(dream_id)

        if not dream:
            return None

        # Update only provided fields
        if content is not None:
            dream.content = content

        if dream_date is not None:
            dream.dream_date = dream_date

        await self.db.commit()
        await self.db.refresh(dream)

        return dream

    async def delete_dream(self, dream_id: int) -> bool:
        """
        Delete a dream by ID.

        Args:
            dream_id: ID of dream to delete

        Returns:
            True if deleted, False if not found
        """
        dream = await self.get_dream_by_id(dream_id)

        if not dream:
            return False

        await self.db.delete(dream)
        await self.db.commit()

        return True
