from datetime import date, time

from pydantic import BaseModel, Field

from app.models.time_block import TimeBlock


class ReplanningRequest(BaseModel):
    plan_date: date = Field(default_factory=date.today)

    planning_start_time: time

    active_task_id: int | None = None

    remaining_minutes: int | None = Field(
        default=None,
        gt=0,
        le=1440,
    )

    day_end_hour: int = Field(
        default=20,
        ge=1,
        le=24,
    )

    break_minutes: int = Field(
        default=15,
        ge=0,
        le=120,
    )

    busy_blocks: list[TimeBlock] = Field(
        default_factory=list,
    )