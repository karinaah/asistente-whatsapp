from app.models.human_state import StressLevel
from app.models.recommendation import (
    DecisionContext,
    RecommendationReason,
    RecommendationReasonCode,
)
from app.models.schedule import ScheduledTask
from app.models.task import TaskEffort, TaskFocusDemand
from app.services.decision_scoring import DecisionRuleWeights

from .base_rule import DecisionRule


class StressRule(DecisionRule):
    def evaluate(
        self,
        scheduled_task: ScheduledTask,
        context: DecisionContext,
    ) -> list[RecommendationReason]:
        human_state = context.human_state

        if human_state is None:
            return []

        if human_state.stress != StressLevel.high:
            return []

        task_is_demanding = (
            scheduled_task.task.effort == TaskEffort.high
            or scheduled_task.task.focus_demand
            == TaskFocusDemand.high
        )

        if not task_is_demanding:
            return []

        return [
            RecommendationReason(
                code=RecommendationReasonCode.high_stress_penalty,
                message=(
                    "Tu nivel de estrés es alto y esta tarea "
                    "requiere bastante esfuerzo o concentración."
                ),
                score=DecisionRuleWeights.HIGH_STRESS_PENALTY,
            )
        ]