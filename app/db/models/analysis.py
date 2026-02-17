from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
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

    # Agent type for workflow organization
    agent_type: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="specialist"
    )  # "generalist" | "specialist" | "synthesizer"

    # Model used for this analysis (e.g., "gpt-4o-mini", "qwen2.5:7b")
    model_used: Mapped[str] = mapped_column(
        String(100), nullable=False, server_default="qwen2.5:7b"
    )  # noqa: E501

    # The analysis content
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Score from rating agent (1-5 avg). Only set on specialist analyses.
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationship: Analysis belongs to one dream
    dream: Mapped["Dream"] = relationship(back_populates="analyses")
