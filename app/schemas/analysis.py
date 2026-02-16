from datetime import datetime

from pydantic import BaseModel


class AnalysisRead(BaseModel):
    """Schema for reading an analysis (response)."""

    id: int
    dream_id: int
    agent_name: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
