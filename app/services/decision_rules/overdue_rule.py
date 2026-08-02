from app.models.recommendation import (
    DecisionContext,
    RecommendationReason,
    RecommendationReasonCode,
)
from app.models.schedule import ScheduledTask
from app.services.decision_scoring import DecisionRuleWeights

from .base_rule import DecisionRule


class OverdueRule(DecisionRule):
    def evaluate(
        self,
        scheduled_task: ScheduledTask,
        context: DecisionContext,
    ) -> list[RecommendationReason]:
        deadline = scheduled_task.task.deadline

        if deadline is None:
            return []

        if deadline >= context.current_time:
            return []

        return [
            RecommendationReason(
                code=RecommendationReasonCode.overdue,
                message="La tarea está vencida.",
                score=DecisionRuleWeights.OVERDUE,
            )
        ]