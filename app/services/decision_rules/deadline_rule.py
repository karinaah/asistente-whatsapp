from app.models.recommendation import (
    RecommendationReason,
    RecommendationReasonCode,
)
from app.models.schedule import ScheduledTask
from app.services.decision_scoring import DecisionRuleWeights

from .base_rule import DecisionRule

class DeadlineRule(DecisionRule):
    def evaluate(
        self,
        scheduled_task: ScheduledTask,
    ) -> list[RecommendationReason]:

        deadline = scheduled_task.task.deadline

        if deadline is None:
            return []

        if deadline.date() != scheduled_task.start_time.date():
            return []

        return [
            RecommendationReason(
                code=RecommendationReasonCode.deadline_soon,
                message="La tarea vence hoy.",
                score=DecisionRuleWeights.DEADLINE_TODAY,
            )
        ]