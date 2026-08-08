from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.task import TaskCategory, TaskContext


class TaskExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: int
    estimated_minutes: int
    actual_minutes: int
    started_at: datetime
    finished_at: datetime
    category: TaskCategory
    context: TaskContext

    energy: str | None = None
    focus: str | None = None
    stress: str | None = None