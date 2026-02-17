from datetime import datetime

from pydantic import BaseModel, Field

from app.core.models_config import DEFAULT_MODEL
from app.schemas.analysis import AnalysisRead


class DreamCreate(BaseModel):
    """Schema for creating a new dream."""

    content: str = Field(
        ...,  # ... means required
        min_length=1,
        max_length=10000,
        description="The dream content/description",
    )

    dream_date: datetime | None = Field(
        default=None,
        description="When the dream occurred (defaults to now if not provided)",
    )

    model: str = Field(
        default=DEFAULT_MODEL,
        description="LiteLLM model string to use for analysis",
    )


class DreamRead(BaseModel):
    """Schema for reading a dream (response)."""

    id: int
    content: str
    dream_date: datetime
    created_at: datetime
    updated_at: datetime
    analyses: list[AnalysisRead] = []  # Include analyses if loaded

    # Tell Pydantic to convert SQLAlchemy models to this schema
    model_config = {"from_attributes": True}


class DreamUpdate(BaseModel):
    """Schema for updating a dream."""

    content: str | None = Field(
        default=None,
        min_length=1,
        max_length=10000,
    )

    dream_date: datetime | None = None
