from datetime import date, datetime

from app.models.schedule import PlanningFromDBRequest
from app.models.task import (
    Task,
    TaskWorkspace,
)
from app.services.planning_workflow_service import (
    PlanningWorkflowService,
)
from app.models.time_block import (
    BlockType,
    TimeBlock,
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

def test_global_availability_combines_work_and_personal_tasks(
    monkeypatch,
):
    service = PlanningWorkflowService()

    work_task = Task(
        title="Preparar informe cliente",
        estimated_minutes=60,
        category="trabajo",
        context="trabajo",
        workspace=TaskWorkspace.work,
    )

    personal_task = Task(
        title="Ir al gimnasio",
        estimated_minutes=60,
        category="salud",
        context="personal",
        workspace=TaskWorkspace.personal,
    )

    monkeypatch.setattr(
        service.task_service,
        "get_plannable",
        lambda db: [
            work_task,
            personal_task,
        ],
    )

    monkeypatch.setattr(
        service.adaptive_profile_service,
        "get",
        lambda db: None,
    )

    busy_block = TimeBlock(
        start_time=datetime.fromisoformat(
            "2026-08-10T09:00:00"
        ),
        end_time=datetime.fromisoformat(
            "2026-08-10T10:00:00"
        ),
        title="Reunión",
        block_type=BlockType.EVENT,
    )

    request = PlanningFromDBRequest(
        plan_date=date.fromisoformat("2026-08-10"),
        day_start_hour=8,
        day_end_hour=12,
        break_minutes=0,
        busy_blocks=[busy_block],
        context=None,
    )

    plan = service.create_plan_from_db(
        db=None,
        request=request,
    )

    assert len(plan.scheduled_tasks) == 2

    scheduled_workspaces = {
        scheduled.task.workspace
        for scheduled in plan.scheduled_tasks
    }

    assert scheduled_workspaces == {
        TaskWorkspace.work,
        TaskWorkspace.personal,
    }

    for scheduled in plan.scheduled_tasks:
        overlaps_busy_block = (
            scheduled.start_time < busy_block.end_time
            and scheduled.end_time > busy_block.start_time
        )

        assert not overlaps_busy_block    

def test_create_plan_from_db_excludes_future_tasks(
    monkeypatch,
):
    service = PlanningWorkflowService()

    today_task = Task(
        title="Tarea de hoy",
        estimated_minutes=60,
        preferred_date=date.fromisoformat(
            "2026-08-10"
        ),
    )

    undated_task = Task(
        title="Tarea sin fecha",
        estimated_minutes=60,
    )

    tomorrow_task = Task(
        title="Tarea de mañana",
        estimated_minutes=60,
        preferred_date=date.fromisoformat(
            "2026-08-11"
        ),
    )

    monkeypatch.setattr(
        service.task_service,
        "get_plannable",
        lambda db: [
            today_task,
            undated_task,
            tomorrow_task,
        ],
    )

    monkeypatch.setattr(
        service.adaptive_profile_service,
        "get",
        lambda db: None,
    )

    request = PlanningFromDBRequest(
        plan_date=date.fromisoformat(
            "2026-08-10"
        ),
        day_start_hour=8,
        day_end_hour=20,
        break_minutes=0,
        busy_blocks=[],
    )

    plan = service.create_plan_from_db(
        db=None,
        request=request,
    )

    scheduled_titles = {
        scheduled.task.title
        for scheduled in plan.scheduled_tasks
    }

    assert "Tarea de hoy" in scheduled_titles
    assert "Tarea sin fecha" in scheduled_titles
    assert "Tarea de mañana" not in scheduled_titles        

def test_create_plan_with_decisions_excludes_future_tasks(
    monkeypatch,
):
    service = PlanningWorkflowService()

    today_task = Task(
        title="Tarea de hoy",
        estimated_minutes=60,
        preferred_date=date.fromisoformat(
            "2026-08-10"
        ),
    )

    tomorrow_task = Task(
        title="Tarea de mañana",
        estimated_minutes=60,
        preferred_date=date.fromisoformat(
            "2026-08-11"
        ),
    )

    monkeypatch.setattr(
        service.task_service,
        "get_plannable",
        lambda db: [
            today_task,
            tomorrow_task,
        ],
    )

    monkeypatch.setattr(
        service.adaptive_profile_service,
        "get",
        lambda db: None,
    )

    request = PlanningFromDBRequest(
        plan_date=date.fromisoformat(
            "2026-08-10"
        ),
        day_start_hour=8,
        day_end_hour=20,
        break_minutes=0,
        busy_blocks=[],
    )

    result = (
        service.create_plan_with_decisions_from_db(
            db=None,
            request=request,
        )
    )

    scheduled_titles = {
        scheduled.task.title
        for scheduled in result.response.scheduled_tasks
    }

    assert "Tarea de hoy" in scheduled_titles
    assert "Tarea de mañana" not in scheduled_titles    