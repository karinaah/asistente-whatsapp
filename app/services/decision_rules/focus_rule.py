from app.models.human_state import FocusLevel
from app.models.recommendation import (
    DecisionContext,
    RecommendationReason,
    RecommendationReasonCode,
)
from app.models.schedule import ScheduledTask
from app.models.task import TaskFocusDemand
from app.services.decision_scoring import DecisionRuleWeights

from .base_rule import DecisionRule


class FocusRule(DecisionRule):
    def evaluate(
        self,
        scheduled_task: ScheduledTask,
        context: DecisionContext,
    ) -> list[RecommendationReason]:
        human_state = context.human_state

        if human_state is None or human_state.focus is None:
            return []

        focus = human_state.focus
        focus_demand = scheduled_task.task.focus_demand

        high_focus_match = (
            focus == FocusLevel.high
            and focus_demand == TaskFocusDemand.high
        )

        low_focus_match = (
            focus == FocusLevel.low
            and focus_demand == TaskFocusDemand.low
        )

        if not high_focus_match and not low_focus_match:
            return []

        return [
            RecommendationReason(
                code=RecommendationReasonCode.focus_match,
                message=(
                    "La exigencia de concentración de la tarea "
                    "coincide con tu nivel de enfoque actual."
                ),
                score=DecisionRuleWeights.FOCUS_MATCH,
            )
        ]