from app.models.recommendation import (
    RecommendationReason,
    RecommendationReasonCode,
)
from app.models.schedule import ScheduledTask
from app.services.decision_scoring import DecisionRuleWeights

from .base_rule import DecisionRule


class PreferredTimeRule(DecisionRule):
    def evaluate(
        self,
        scheduled_task: ScheduledTask,
    ) -> list[RecommendationReason]:
        preferred_time = (
            scheduled_task.task.preferred_time_of_day
        )

        if preferred_time is None:
            return []

        slot_hour = scheduled_task.start_time.hour

        preferred_ranges = {
            "mañana": range(5, 12),
            "tarde": range(12, 18),
            "noche": range(18, 24),
        }

        preferred_hours = preferred_ranges.get(
            preferred_time.value
        )

        if (
            preferred_hours is None
            or slot_hour not in preferred_hours
        ):
            return []

        return [
            RecommendationReason(
                code=(
                    RecommendationReasonCode
                    .preferred_time_match
                ),
                message=(
                    "La tarea coincide con tu horario "
                    "preferido."
                ),
                score=(
                    DecisionRuleWeights
                    .PREFERRED_TIME_MATCH
                ),
            )
        ]