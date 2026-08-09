from app.models.human_state import EnergyLevel
from app.models.recommendation import (
    DecisionContext,
    RecommendationReason,
    RecommendationReasonCode,
)
from app.models.schedule import ScheduledTask
from app.services.decision_scoring import DecisionRuleWeights

from .base_rule import DecisionRule


class AdaptiveEnergyRule(DecisionRule):
    def evaluate(
        self,
        scheduled_task: ScheduledTask,
        context: DecisionContext,
    ) -> list[RecommendationReason]:
        profile = context.adaptive_profile

        if profile is None:
            return []

        if not profile.prefers_short_tasks_when_low_energy:
            return []

        if (
            context.human_state is None
            or context.human_state.energy
            not in {
                EnergyLevel.low,
                EnergyLevel.very_low,
            }
        ):
            return []

        if scheduled_task.task.estimated_minutes <= 45:
            return []

        return [
            RecommendationReason(
                code=(
                    RecommendationReasonCode
                    .adaptive_low_energy_penalty
                ),
                message=(
                    "Según tu historial, con baja energía "
                    "te convienen tareas más cortas."
                ),
                score=(
                    DecisionRuleWeights
                    .ADAPTIVE_LOW_ENERGY_PENALTY
                ),
            )
        ]