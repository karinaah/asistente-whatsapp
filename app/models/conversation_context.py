from pydantic import BaseModel

from app.models.assistant_intent import AssistantIntent
from app.models.recommendation import Recommendation
from app.models.schedule import PlanningResponse


class ConversationContext(BaseModel):
    last_intent: AssistantIntent | None = None
    last_recommendation: Recommendation | None = None
    last_plan: PlanningResponse | None = None
    awaiting_remaining_minutes: bool = False
    pending_active_task_id: int | None = None    