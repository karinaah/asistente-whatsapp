from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.human_state import HumanState
from app.models.task import TaskCategory, TaskContext


class TaskExecution(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: int

    estimated_minutes: int = Field(
        gt=0,
        le=1440,
    )

    actual_minutes: int = Field(
        gt=0,
        le=1440,
    )

    started_at: datetime
    finished_at: datetime

    category: TaskCategory
    context: TaskContext

    human_state: HumanState | None = None

    @model_validator(mode="after")
    def validate_times(self):
        if self.finished_at <= self.started_at:
            raise ValueError(
                "finished_at debe ser posterior a started_at"
            )

        return self