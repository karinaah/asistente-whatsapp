from datetime import date

from app.models.schedule import PlanningFromDBRequest
from app.models.task import Task
from app.services.planning_workflow_service import (
    PlanningWorkflowService,
)


def test_create_plan_from_db_uses_plannable_tasks(
    monkeypatch,
):
    service = PlanningWorkflowService()

    task = Task(
        title="Preparar presentación",
        estimated_minutes=60,
        category="trabajo",
        context="trabajo",
    )

    monkeypatch.setattr(
        service.task_service,
        "get_plannable",
        lambda db: [task],
    )

    monkeypatch.setattr(
        service.adaptive_profile_service,
        "get",
        lambda db: None,
    )

    request = PlanningFromDBRequest(
        plan_date=date.fromisoformat("2026-08-10"),
        day_start_hour=8,
        day_end_hour=20,
        break_minutes=0,
        busy_blocks=[],
        context="trabajo",
    )

    plan = service.create_plan_from_db(
        db=None,
        request=request,
    )

    assert len(plan.scheduled_tasks) == 1
    assert (
        plan.scheduled_tasks[0].task.title
        == "Preparar presentación"
    )