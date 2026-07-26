from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.task import Task, TaskContext
from app.models.time_block import TimeBlock

class ScheduledTask(BaseModel):
    task: Task
    start_time: datetime
    end_time: datetime


class PlanningRequest(BaseModel):
    tasks: list[Task]
    plan_date: date = Field(default_factory=date.today)
    day_start_hour: int = Field(default=8, ge=0, le=23)
    day_end_hour: int = Field(default=20, ge=1, le=24)
    break_minutes: int = Field(default=15, ge=0, le=120)
    busy_blocks: list[TimeBlock] = Field(default_factory=list)
    context: TaskContext | None = None

class PlanningResponse(BaseModel):
    scheduled_tasks: list[ScheduledTask]
    unscheduled_tasks: list[Task]
    timeline: list[TimeBlock]

class PlanningFromDBRequest(BaseModel):
    plan_date: date = Field(default_factory=date.today)
    day_start_hour: int = Field(default=8, ge=0, le=23)
    day_end_hour: int = Field(default=20, ge=1, le=24)
    break_minutes: int = Field(default=15, ge=0, le=120)
    busy_blocks: list[TimeBlock] = Field(default_factory=list)
    context: TaskContext | None = None
