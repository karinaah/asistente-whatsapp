from app.models.recommendation import (
    DecisionContext,
    RecommendationReason,
    RecommendationReasonCode,
)
from app.models.schedule import ScheduledTask
from app.services.decision_scoring import DecisionRuleWeights

from .base_rule import DecisionRule


class AvailableTimeRule(DecisionRule):
    def evaluate(
        self,
        scheduled_task: ScheduledTask,
        context: DecisionContext,
    ) -> list[RecommendationReason]:
        if context.available_minutes is None:
            return []

        if (
            scheduled_task.task.estimated_minutes
            > context.available_minutes
        ):
            return []

        return [
            RecommendationReason(
                code=RecommendationReasonCode.fits_available_time,
                message=(
                    "La tarea cabe en el tiempo "
                    "que tienes disponible."
                ),
                score=DecisionRuleWeights.FITS_AVAILABLE_TIME,
            )
        ]