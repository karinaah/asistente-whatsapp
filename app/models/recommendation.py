from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from app.models.schedule import (
    PlanningResponse,
    ScheduledTask,
)
from app.models.task import Task, TaskContext
from app.models.human_state import HumanState

class RecommendationReasonCode(str, Enum):
    high_priority = "high_priority"
    deadline_soon = "deadline_soon"
    fits_available_time = "fits_available_time"
    preferred_time_match = "preferred_time_match"
    earliest_available = "earliest_available"
    context_match = "context_match"
    overdue = "overdue"
    energy_match = "energy_match"
    focus_match = "focus_match"
    high_stress_penalty = "high_stress_penalty"

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
    human_state: HumanState | None = None   

class Recommendation(BaseModel):
    task: Task
    scheduled_task: ScheduledTask | None = None
    score: float
    summary: str | None = None
    reasons: list[RecommendationReason] = Field(
        default_factory=list
    )