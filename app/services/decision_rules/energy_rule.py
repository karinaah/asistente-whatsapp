from app.models.human_state import EnergyLevel
from app.models.recommendation import (
    DecisionContext,
    RecommendationReason,
    RecommendationReasonCode,
)
from app.models.schedule import ScheduledTask
from app.models.task import TaskEffort
from app.services.decision_scoring import DecisionRuleWeights

from .base_rule import DecisionRule


class EnergyRule(DecisionRule):
    def evaluate(
        self,
        scheduled_task: ScheduledTask,
        context: DecisionContext,
    ) -> list[RecommendationReason]:
        human_state = context.human_state

        if human_state is None or human_state.energy is None:
            return []

        energy = human_state.energy
        effort = scheduled_task.task.effort

        high_energy_match = (
            energy in {
                EnergyLevel.high,
                EnergyLevel.very_high,
            }
            and effort == TaskEffort.high
        )

        low_energy_match = (
            energy in {
                EnergyLevel.low,
                EnergyLevel.very_low,
            }
            and effort == TaskEffort.low
        )

        if not high_energy_match and not low_energy_match:
            return []

        return [
            RecommendationReason(
                code=RecommendationReasonCode.energy_match,
                message=(
                    "La exigencia de la tarea coincide "
                    "con tu nivel de energía actual."
                ),
                score=DecisionRuleWeights.ENERGY_MATCH,
            )
        ]