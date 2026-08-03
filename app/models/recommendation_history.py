from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RecommendationHistory(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    task_id: int | None = None
    task_title: str
    score: float
    summary: str | None = None
    reasons_json: str
    energy: str | None = None
    focus: str | None = None
    stress: str | None = None
    available_minutes: int | None = None
    created_at: datetime