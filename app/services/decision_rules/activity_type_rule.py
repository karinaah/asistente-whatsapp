from app.models.human_state import (
    EnergyLevel,
    FocusLevel,
    StressLevel,
)
from app.models.recommendation import (
    DecisionContext,
    RecommendationReason,
    RecommendationReasonCode,
)
from app.models.schedule import ScheduledTask
from app.models.task import ActivityType
from app.services.decision_scoring import DecisionRuleWeights

from .base_rule import DecisionRule


class ActivityTypeRule(DecisionRule):
    def evaluate(
        self,
        scheduled_task: ScheduledTask,
        context: DecisionContext,
    ) -> list[RecommendationReason]:
        human_state = context.human_state

        if human_state is None:
            return []

        activity_type = scheduled_task.task.activity_type

        matches = {
            ActivityType.deep_work: (
                human_state.focus == FocusLevel.high
            ),
            ActivityType.administrative: (
                human_state.focus == FocusLevel.low
            ),
            ActivityType.rest: (
                human_state.stress == StressLevel.high
                or human_state.energy
                in {
                    EnergyLevel.low,
                    EnergyLevel.very_low,
                }
            ),
            ActivityType.exercise: (
                human_state.energy
                in {
                    EnergyLevel.medium,
                    EnergyLevel.high,
                    EnergyLevel.very_high,
                }
            ),
            ActivityType.study: (
                human_state.focus
                in {
                    FocusLevel.medium,
                    FocusLevel.high,
                }
            ),
            ActivityType.routine: (
                human_state.focus
                in {
                    FocusLevel.low,
                    FocusLevel.medium,
                }
            ),
        }

        if not matches.get(activity_type, False):
            return []

        return [
            RecommendationReason(
                code=(
                    RecommendationReasonCode
                    .activity_type_match
                ),
                message=(
                    "El tipo de actividad coincide "
                    "con tu estado actual."
                ),
                score=(
                    DecisionRuleWeights
                    .ACTIVITY_TYPE_MATCH
                ),
            )
        ]