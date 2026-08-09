from datetime import datetime

from app.models.explanation import (
    ExplanationType,
)
from app.models.planning_decision import (
    PlanningDecision,
)
from app.models.planning_reason import (
    PlanningReason,
    PlanningReasonCode,
)
from app.models.schedule import ScheduledTask
from app.models.task import Task
from app.services.planning_explanation_service import (
    PlanningExplanationService,
)


def test_build_planning_explanation():
    service = PlanningExplanationService()

    task = Task(
        title="Preparar presentación",
        estimated_minutes=60,
        category="trabajo",
        context="trabajo",
    )

    scheduled_task = ScheduledTask(
        task=task,
        start_time=datetime.fromisoformat(
            "2026-08-10T21:00:00"
        ),
        end_time=datetime.fromisoformat(
            "2026-08-10T22:00:00"
        ),
    )

    decision = PlanningDecision(
        scheduled_task=scheduled_task,
        reasons=[
            PlanningReason(
                code=(
                    PlanningReasonCode
                    .preferred_start_time
                ),
                message=(
                    "La tarea fue programada en "
                    "su horario preferido."
                ),
            ),
            PlanningReason(
                code=(
                    PlanningReasonCode
                    .adaptive_duration
                ),
                message=(
                    "La duración fue ajustada "
                    "según tu historial."
                ),
            ),
        ],
    )

    explanation = service.build(decision)

    assert (
        explanation.type
        == ExplanationType.planning
    )

    assert (
        "Preparar presentación"
        in explanation.title
    )

    assert (
        "21:00"
        in explanation.summary
    )

    assert len(explanation.details) == 2

    assert (
        "horario preferido"
        in explanation.details[0]
    )

    assert (
        "historial"
        in explanation.details[1]
    )