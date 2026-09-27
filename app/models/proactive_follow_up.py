from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class FollowUpType(str, Enum):
    PENDING_TASKS = "pending_tasks"
    DELAYED_DAY = "delayed_day"
    ROUTINE_PENDING = "routine_pending"


class FollowUpStatus(str, Enum):
    PENDING = "pending"
    DISMISSED = "dismissed"
    COMPLETED = "completed"


class ProactiveFollowUp(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    user_id: int

    follow_up_type: FollowUpType
    title: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=1000)

    task_id: int | None = None
    routine_id: int | None = None

    status: FollowUpStatus = FollowUpStatus.PENDING

    created_at: datetime = Field(default_factory=datetime.now)
    resolved_at: datetime | None = None