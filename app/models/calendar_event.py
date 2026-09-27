from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CalendarEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    external_id: str | None = None

    title: str = Field(
        min_length=1,
        max_length=500,
    )

    start_time: datetime
    end_time: datetime

    all_day: bool = False