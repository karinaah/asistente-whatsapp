from app.models.conversation_context import (
    ConversationContext,
)
from app.models.assistant_intent import (
    AssistantIntent,
)
from app.models.recommendation import Recommendation
from app.models.schedule import PlanningResponse


class ConversationMemoryService:
    def __init__(self) -> None:
        self._context = ConversationContext()

    def get_context(self) -> ConversationContext:
        return self._context

    def clear(self) -> None:
        self._context = ConversationContext()

    def set_last_intent(
        self,
        intent: AssistantIntent,
    ) -> None:
        self._context.last_intent = intent

    def set_last_recommendation(
        self,
        recommendation: Recommendation,
    ) -> None:
        self._context.last_recommendation = (
            recommendation
        )

    def set_last_plan(
        self,
        plan: PlanningResponse,
    ) -> None:
        self._context.last_plan = plan