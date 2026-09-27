from datetime import datetime, time
from enum import IntEnum

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import (
    ActivityType,
    TaskCategory,
    TaskContext,
    TaskWorkspace,
)


class Weekday(IntEnum):
    monday = 0
    tuesday = 1
    wednesday = 2
    thursday = 3
    friday = 4
    saturday = 5
    sunday = 6


class Routine(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    user_id: int

    title: str = Field(
        min_length=1,
        max_length=200,
    )
    description: str | None = None

    weekdays: list[Weekday] = Field(
        min_length=1,
    )

    preferred_start_time: time | None = None
    estimated_minutes: int = Field(
        gt=0,
        le=1440,
    )

    category: TaskCategory = TaskCategory.other
    context: TaskContext = TaskContext.personal
    workspace: TaskWorkspace = TaskWorkspace.personal
    activity_type: ActivityType = ActivityType.routine

    active: bool = True

    created_at: datetime = Field(
        default_factory=datetime.now,
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
    )