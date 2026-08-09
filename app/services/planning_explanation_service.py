from app.models.explanation import (
    Explanation,
    ExplanationType,
)
from app.models.planning_decision import (
    PlanningDecision,
)


class PlanningExplanationService:
    def build(
        self,
        decision: PlanningDecision,
    ) -> Explanation:
        return Explanation(
            type=ExplanationType.planning,
            title=(
                f"Por qué programé "
                f"{decision.scheduled_task.task.title}"
            ),
            summary=(
                f"La tarea fue programada para "
                f"las "
                f"{decision.scheduled_task.start_time.strftime('%H:%M')}."
            ),
            details=[
                reason.message
                for reason in decision.reasons
            ],
        )