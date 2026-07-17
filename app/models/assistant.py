from datetime import date

from pydantic import BaseModel, Field

from app.models.time_block import TimeBlock


class AssistantRequest(BaseModel):
    text: str = Field(min_length=1)
    plan_date: date = Field(default_factory=date.today)
    day_start_hour: int = Field(default=8, ge=0, le=23)
    day_end_hour: int = Field(default=20, ge=1, le=24)
    break_minutes: int = Field(default=15, ge=0, le=120)
    busy_blocks: list[TimeBlock] = Field(default_factory=list)