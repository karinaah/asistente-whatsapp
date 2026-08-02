from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from app.models.schedule import (
    PlanningResponse,
    ScheduledTask,
)
from app.models.task import Task, TaskContext

class RecommendationReasonCode(str, Enum):
    high_priority = "high_priority"
    deadline_soon = "deadline_soon"
    fits_available_time = "fits_available_time"
    preferred_time_match = "preferred_time_match"
    earliest_available = "earliest_available"
    context_match = "context_match"
    overdue = "overdue"

class RecommendationReason(BaseModel):
    code: RecommendationReasonCode
    message: str = Field(min_length=1)
    score: float

class DecisionContext(BaseModel):
    current_time: datetime
    plan: PlanningResponse
    context: TaskContext | None = None
    available_minutes: int | None = Field(
        default=None,
        ge=0,
    )

class Recommendation(BaseModel):
    task: Task
    scheduled_task: ScheduledTask | None = None
    score: float
    reasons: list[RecommendationReason] = Field(
        default_factory=list
    )