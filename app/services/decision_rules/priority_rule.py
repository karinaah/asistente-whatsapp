from app.models.recommendation import (
    RecommendationReason,
    RecommendationReasonCode,
)
from app.models.schedule import ScheduledTask

from .base_rule import DecisionRule
from app.services.decision_scoring import DecisionRuleWeights

class PriorityRule(DecisionRule):
    def evaluate(
        self,
        scheduled_task: ScheduledTask,
    ) -> list[RecommendationReason]:

        if scheduled_task.task.priority.value != "alta":
            return []

        return [
            RecommendationReason(
                code=RecommendationReasonCode.high_priority,
                message="La tarea tiene prioridad alta.",
                score=DecisionRuleWeights.HIGH_PRIORITY,
            )
        ]