"""
Pydantic schemas for Dream API.

- DreamCreate: What clients send when creating a dream
- DreamRead: What we return when reading a dream
- DreamUpdate: What clients send when updating a dream
"""

from datetime import datetime

from pydantic import BaseModel, Field


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


class DreamRead(BaseModel):
    """Schema for reading a dream (response)."""

    id: int
    content: str
    dream_date: datetime
    created_at: datetime
    updated_at: datetime

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
