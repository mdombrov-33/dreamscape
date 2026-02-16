from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.db.models.analysis import Analysis


class Dream(Base):
    """User's dream entry."""

    __tablename__ = "dreams"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)

    # Dream content (can be long, use Text not String)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # When was this dream from?
    dream_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),  # Default to current time
    )

    # For semantic search (we'll add embeddings later in Phase 4)
    # embedding: Mapped[Vector] = mapped_column(Vector(1536), nullable=True)

    # Timestamps (automatically managed)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),  # Updates automatically on change
    )


# Relationship: One dream has many analyses
analyses: Mapped[list["Analysis"]] = relationship(
    back_populates="dream",
    cascade="all, delete-orphan",  # Delete analyses if dream is deleted
)
