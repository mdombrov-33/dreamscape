from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.db.models.dream import Dream


class Analysis(Base):
    """AI analysis of a dream."""

    __tablename__ = "analyses"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)

    # Which dream is this analyzing?
    dream_id: Mapped[int] = mapped_column(
        ForeignKey("dreams.id", ondelete="CASCADE"), nullable=False
    )

    # Which agent did this analysis?
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # The analysis content
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationship: Analysis belongs to one dream
    dream: Mapped["Dream"] = relationship(back_populates="analyses")
