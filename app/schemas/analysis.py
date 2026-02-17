from datetime import datetime

from pydantic import BaseModel


class AnalysisRead(BaseModel):
    id: int
    dream_id: int
    agent_name: str
    agent_type: str
    model_used: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
