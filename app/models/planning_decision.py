from pydantic import BaseModel

from app.models.planning_reason import PlanningReason
from app.models.schedule import ScheduledTask


class PlanningDecision(BaseModel):
    scheduled_task: ScheduledTask
    reasons: list[PlanningReason]