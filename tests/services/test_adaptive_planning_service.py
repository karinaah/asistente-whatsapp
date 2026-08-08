from datetime import date, datetime

from app.models.human_state import HumanState
from app.models.schedule import PlanningRequest
from app.models.task import Task
from app.models.task_execution import TaskExecution
from app.services.adaptive_planning_service import (
    AdaptivePlanningService,
)


def test_adaptive_planning_uses_historical_execution_data(
    monkeypatch,
):
    service = AdaptivePlanningService()

    executions = [
        TaskExecution(
            task_id=1,
            estimated_minutes=60,
            actual_minutes=72,
            started_at=datetime.fromisoformat(
                "2026-08-01T09:00:00"
            ),
            finished_at=datetime.fromisoformat(
                "2026-08-01T10:12:00"
            ),
            category="trabajo",
            context="trabajo",
            human_state=HumanState(
                energy="alta",
                focus="alto",
                stress="bajo",
            ),
        ),
        TaskExecution(
            task_id=2,
            estimated_minutes=60,
            actual_minutes=72,
            started_at=datetime.fromisoformat(
                "2026-08-02T09:00:00"
            ),
            finished_at=datetime.fromisoformat(
                "2026-08-02T10:12:00"
            ),
            category="trabajo",
            context="trabajo",
        ),
        TaskExecution(
            task_id=3,
            estimated_minutes=60,
            actual_minutes=72,
            started_at=datetime.fromisoformat(
                "2026-08-03T09:00:00"
            ),
            finished_at=datetime.fromisoformat(
                "2026-08-03T10:12:00"
            ),
            category="trabajo",
            context="trabajo",
        ),
    ]

    monkeypatch.setattr(
        service.task_execution_service,
        "get_all_for_learning",
        lambda db: executions,
    )

    task = Task(
        title="Preparar presentación",
        estimated_minutes=60,
        category="trabajo",
        context="trabajo",
    )

    request = PlanningRequest(
        tasks=[task],
        plan_date=date.fromisoformat("2026-08-10"),
        day_start_hour=8,
        day_end_hour=20,
        break_minutes=0,
        busy_blocks=[],
        context="trabajo",
    )

    plan = service.create_plan(
        db=None,
        request=request,
    )

    assert len(plan.scheduled_tasks) == 1

    scheduled = plan.scheduled_tasks[0]

    duration_minutes = int(
        (
            scheduled.end_time
            - scheduled.start_time
        ).total_seconds()
        / 60
    )

    assert duration_minutes == 72
    assert task.estimated_minutes == 60