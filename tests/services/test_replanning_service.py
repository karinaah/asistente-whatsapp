from datetime import date, datetime, time

from app.models.schedule import PlanningResponse, ScheduledTask
from app.models.task import Task
from app.services.replanning_service import ReplanningService
from app.models.replanning import ReplanningRequest


def test_replan_from_time_starts_at_requested_time(
    monkeypatch,
):
    service = ReplanningService()

    task = Task(
        title="Tarea pendiente",
        estimated_minutes=60,
    )

    monkeypatch.setattr(
        service.planning_workflow_service.task_service,
        "get_plannable",
        lambda db: [task],
    )

    monkeypatch.setattr(
        service.planning_workflow_service.adaptive_profile_service,
        "get",
        lambda db: None,
    )

    result = service.replan_from_time(
        db=None,
        plan_date=date.fromisoformat("2026-08-22"),
        planning_start_time=time.fromisoformat("14:37"),
        day_end_hour=20,
        break_minutes=0,
    )

    assert len(result.scheduled_tasks) == 1

    assert (
        result.scheduled_tasks[0].start_time
        == datetime.fromisoformat(
            "2026-08-22T14:37:00"
        )
    )

def test_replan_from_time_does_not_schedule_tasks_before_now(
    monkeypatch,
):
    service = ReplanningService()

    task = Task(
        title="Tarea pendiente",
        estimated_minutes=60,
    )

    monkeypatch.setattr(
        service.planning_workflow_service.task_service,
        "get_plannable",
        lambda db: [task],
    )

    monkeypatch.setattr(
        service.planning_workflow_service.adaptive_profile_service,
        "get",
        lambda db: None,
    )

    result = service.replan_from_time(
        db=None,
        plan_date=date.fromisoformat("2026-08-22"),
        planning_start_time=time.fromisoformat("14:37"),
        day_end_hour=20,
        break_minutes=0,
    )

    assert len(result.scheduled_tasks) == 1

    assert (
        result.scheduled_tasks[0].start_time
        >= datetime.fromisoformat(
            "2026-08-22T14:37:00"
        )
    )    

def test_replan_excludes_completed_tasks(
    monkeypatch,
):
    service = ReplanningService()

    pending_task = Task(
        title="Tarea pendiente",
        estimated_minutes=60,
        status="pendiente",
    )

    completed_task = Task(
        title="Tarea completada",
        estimated_minutes=60,
        status="completada",
    )

    monkeypatch.setattr(
        service.planning_workflow_service.task_service,
        "get_all",
        lambda db: [
            pending_task,
            completed_task,
        ],
    )

    monkeypatch.setattr(
        service.planning_workflow_service.adaptive_profile_service,
        "get",
        lambda db: None,
    )

    result = service.replan_from_time(
        db=None,
        plan_date=date.fromisoformat("2026-08-22"),
        planning_start_time=time.fromisoformat("14:37"),
        day_end_hour=20,
        break_minutes=0,
    )

    scheduled_titles = {
        scheduled.task.title
        for scheduled in result.scheduled_tasks
    }

    assert "Tarea pendiente" in scheduled_titles
    assert "Tarea completada" not in scheduled_titles    

def test_replan_prioritizes_new_high_priority_task(
    monkeypatch,
):
    service = ReplanningService()

    existing_task = Task(
        title="Tarea pendiente normal",
        estimated_minutes=60,
        priority="media",
    )

    urgent_task = Task(
        title="Tarea urgente nueva",
        estimated_minutes=30,
        priority="alta",
    )

    monkeypatch.setattr(
        service.planning_workflow_service.task_service,
        "get_all",
        lambda db: [
            existing_task,
            urgent_task,
        ],
    )

    monkeypatch.setattr(
        service.planning_workflow_service.adaptive_profile_service,
        "get",
        lambda db: None,
    )

    result = service.replan_from_time(
        db=None,
        plan_date=date.fromisoformat("2026-08-22"),
        planning_start_time=time.fromisoformat("14:37"),
        day_end_hour=20,
        break_minutes=0,
    )

    assert len(result.scheduled_tasks) == 2

    assert (
        result.scheduled_tasks[0].task.title
        == "Tarea urgente nueva"
    )

    assert (
        result.scheduled_tasks[0].start_time
        == datetime.fromisoformat(
            "2026-08-22T14:37:00"
        )
    )

    assert (
        result.scheduled_tasks[1].task.title
        == "Tarea pendiente normal"
    )    

def test_replan_respects_fixed_task_when_urgent_task_appears(
    monkeypatch,
):
    service = ReplanningService()

    urgent_task = Task(
        title="Resolver incidencia urgente",
        estimated_minutes=60,
        priority="alta",
    )

    fixed_task = Task(
        title="Reunión fija",
        estimated_minutes=60,
        priority="media",
        preferred_date=date.fromisoformat("2026-08-22"),
        preferred_start_time=time.fromisoformat("16:00"),
        flexibility="fixed",
    )

    monkeypatch.setattr(
        service.planning_workflow_service.task_service,
        "get_all",
        lambda db: [
            urgent_task,
            fixed_task,
        ],
    )

    monkeypatch.setattr(
        service.planning_workflow_service.adaptive_profile_service,
        "get",
        lambda db: None,
    )

    result = service.replan_from_time(
        db=None,
        plan_date=date.fromisoformat("2026-08-22"),
        planning_start_time=time.fromisoformat("14:37"),
        day_end_hour=20,
        break_minutes=0,
    )

    assert len(result.scheduled_tasks) == 2

    fixed_scheduled = next(
        scheduled
        for scheduled in result.scheduled_tasks
        if scheduled.task.title == "Reunión fija"
    )

    urgent_scheduled = next(
        scheduled
        for scheduled in result.scheduled_tasks
        if scheduled.task.title
        == "Resolver incidencia urgente"
    )

    assert (
        fixed_scheduled.start_time
        == datetime.fromisoformat(
            "2026-08-22T16:00:00"
        )
    )

    assert (
        urgent_scheduled.end_time
        <= fixed_scheduled.start_time
        or urgent_scheduled.start_time
        >= fixed_scheduled.end_time
    )    

def test_replan_accepts_structured_request(
    monkeypatch,
):
    service = ReplanningService()

    expected_plan = PlanningResponse(
        scheduled_tasks=[],
        unscheduled_tasks=[],
        timeline=[],
    )

    def fake_replan_from_time(
        db,
        plan_date,
        planning_start_time,
        day_end_hour,
        break_minutes,
        busy_blocks,
    ):
        assert plan_date == date.fromisoformat(
            "2026-08-22"
        )
        assert (
            planning_start_time
            == time.fromisoformat("14:37")
        )
        assert day_end_hour == 20
        assert break_minutes == 15
        assert busy_blocks == []

        return expected_plan

    monkeypatch.setattr(
        service,
        "replan_from_time",
        fake_replan_from_time,
    )

    request = ReplanningRequest(
        plan_date=date.fromisoformat("2026-08-22"),
        planning_start_time=time.fromisoformat("14:37"),
    )

    result = service.replan(
        db=None,
        request=request,
    )

    assert result == expected_plan    


def test_replan_uses_remaining_minutes_for_active_task(
    monkeypatch,
):
    service = ReplanningService()

    active_task = Task(
        id=12,
        title="Tarea en progreso",
        estimated_minutes=90,
        status="en_progreso",
    )

    pending_task = Task(
        id=13,
        title="Tarea pendiente",
        estimated_minutes=60,
        status="pendiente",
    )

    monkeypatch.setattr(
        service.planning_workflow_service.task_service,
        "get_all",
        lambda db: [
            active_task,
            pending_task,
        ],
    )

    monkeypatch.setattr(
        service.planning_workflow_service.adaptive_profile_service,
        "get",
        lambda db: None,
    )

    request = ReplanningRequest(
        plan_date=date.fromisoformat("2026-08-22"),
        planning_start_time=time.fromisoformat("14:37"),
        active_task_id=12,
        remaining_minutes=45,
        day_end_hour=20,
        break_minutes=0,
    )

    result = service.replan(
        db=None,
        request=request,
    )

    active_scheduled = next(
        scheduled
        for scheduled in result.scheduled_tasks
        if scheduled.task.id == 12
    )

    assert (
        active_scheduled.end_time
        - active_scheduled.start_time
    ).total_seconds() == 45 * 60

    assert active_task.estimated_minutes == 90    

def test_replan_excludes_tasks_for_future_dates(
    monkeypatch,
):
    service = ReplanningService()

    today_task = Task(
        id=20,
        title="Tarea de hoy",
        estimated_minutes=60,
        preferred_date=date.fromisoformat(
            "2026-08-22"
        ),
    )

    tomorrow_task = Task(
        id=21,
        title="Tarea de mañana",
        estimated_minutes=60,
        preferred_date=date.fromisoformat(
            "2026-08-23"
        ),
    )

    monkeypatch.setattr(
        service.planning_workflow_service.task_service,
        "get_all",
        lambda db: [
            today_task,
            tomorrow_task,
        ],
    )

    monkeypatch.setattr(
        service.planning_workflow_service.adaptive_profile_service,
        "get",
        lambda db: None,
    )

    result = service.replan_from_time(
        db=None,
        plan_date=date.fromisoformat(
            "2026-08-22"
        ),
        planning_start_time=time.fromisoformat(
            "10:59"
        ),
        day_end_hour=20,
        break_minutes=0,
    )

    scheduled_titles = {
        scheduled.task.title
        for scheduled in result.scheduled_tasks
    }

    assert "Tarea de hoy" in scheduled_titles
    assert "Tarea de mañana" not in scheduled_titles    

def test_active_task_replan_excludes_future_tasks(
    monkeypatch,
):
    service = ReplanningService()

    active_task = Task(
        id=30,
        title="Tarea activa",
        estimated_minutes=60,
        status="en_progreso",
        preferred_date=date.fromisoformat(
            "2026-08-23"
        ),
    )

    tomorrow_task = Task(
        id=31,
        title="Tarea de mañana",
        estimated_minutes=60,
        status="pendiente",
        preferred_date=date.fromisoformat(
            "2026-08-24"
        ),
    )

    monkeypatch.setattr(
        service.planning_workflow_service.task_service,
        "get_all",
        lambda db: [
            active_task,
            tomorrow_task,
        ],
    )

    monkeypatch.setattr(
        service.planning_workflow_service.adaptive_profile_service,
        "get",
        lambda db: None,
    )

    request = ReplanningRequest(
        plan_date=date.fromisoformat(
            "2026-08-23"
        ),
        planning_start_time=time.fromisoformat(
            "14:19"
        ),
        active_task_id=30,
        remaining_minutes=30,
        day_end_hour=20,
        break_minutes=0,
    )

    result = service.replan(
        db=None,
        request=request,
    )

    scheduled_titles = {
        scheduled.task.title
        for scheduled in result.scheduled_tasks
    }

    assert "Tarea activa" in scheduled_titles
    assert "Tarea de mañana" not in scheduled_titles    