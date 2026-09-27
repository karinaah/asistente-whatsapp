from datetime import datetime, time

from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.models.routine import Weekday


class RecurringAvailability(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    user_id: int

    weekday: Weekday
    start_time: time
    end_time: time

    active: bool = True

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @model_validator(mode="after")
    def validate_time_range(self):
        if self.end_time <= self.start_time:
            raise ValueError(
                "end_time must be after start_time"
            )

        return self    