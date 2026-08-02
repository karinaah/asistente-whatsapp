from app.models.recommendation import (
    DecisionContext,
    RecommendationReason,
    RecommendationReasonCode,
)
from app.models.schedule import ScheduledTask
from app.services.decision_scoring import DecisionRuleWeights

from .base_rule import DecisionRule


class ContextRule(DecisionRule):
    def evaluate(
        self,
        scheduled_task: ScheduledTask,
        context: DecisionContext,
    ) -> list[RecommendationReason]:
        if context.context is None:
            return []

        if scheduled_task.task.context != context.context:
            return []

        return [
            RecommendationReason(
                code=RecommendationReasonCode.context_match,
                message=(
                    "La tarea coincide con el contexto "
                    "que tienes activo."
                ),
                score=DecisionRuleWeights.CONTEXT_MATCH,
            )
        ]