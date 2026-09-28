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
import pytest

@pytest.fixture(autouse=True)
def disable_real_calendar_calls(
    monkeypatch,
):
    monkeypatch.setattr(
        "app.services.calendar_service."
        "CalendarService.get_busy_blocks",
        lambda self, target_date: [],
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
        lambda db, user_id=None: [task],
    )

    monkeypatch.setattr(
        service.adaptive_profile_service,
        "get",
        lambda db, user_id=None: None,
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
        lambda db, user_id=None: [
            work_task,
            personal_task,
        ],
    )

    monkeypatch.setattr(
        service.adaptive_profile_service,
        "get",
        lambda db, user_id=None: None,
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
        lambda db, user_id=None: [
            today_task,
            undated_task,
            tomorrow_task,
        ],
    )

    monkeypatch.setattr(
        service.adaptive_profile_service,
        "get",
        lambda db, user_id=None: None,
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
        lambda db, user_id=None: [
            today_task,
            tomorrow_task,
        ],
    )

    monkeypatch.setattr(
        service.adaptive_profile_service,
        "get",
        lambda db, user_id=None: None,
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

def test_create_plan_uses_user_adaptive_profile(
    monkeypatch,
):
    service = PlanningWorkflowService()

    monkeypatch.setattr(
        service.recurring_availability_service,
        "resolve_day_hours",
        lambda db,
        user_id,
        target_date,
        fallback_start_hour,
        fallback_end_hour: (
            fallback_start_hour,
            fallback_end_hour,
        ),
    )
    monkeypatch.setattr(
        service.recurring_availability_service,
        "build_unavailable_blocks",
        lambda db, user_id, target_date: [],
    )
    monkeypatch.setattr(
        service.routine_occurrence_service,
        "generate_for_user",
        lambda db, user_id, target_date: [],
    )

    task = Task(
        title="Preparar informe",
        estimated_minutes=60,
        category="trabajo",
        context="trabajo",
    )

    monkeypatch.setattr(
        service.task_service,
        "get_plannable",
        lambda db, user_id=None: [task],
    )

    received_user_ids = []

    def get_profile(
        db,
        user_id=None,
    ):
        received_user_ids.append(user_id)

        from app.models.adaptive_profile import (
            AdaptiveProfile,
        )

        return AdaptiveProfile(
            generated_from_executions=5,
            work_duration_multiplier=1.25,
            confidence=0.25,
        )

    monkeypatch.setattr(
        service.adaptive_profile_service,
        "get",
        get_profile,
    )

    request = PlanningFromDBRequest(
        plan_date=date.fromisoformat(
            "2026-08-10"
        ),
        day_start_hour=8,
        day_end_hour=20,
        break_minutes=0,
        busy_blocks=[],
        context="trabajo",
    )

    plan = service.create_plan_from_db(
        db=None,
        request=request,
        user_id=123,
    )

    assert received_user_ids == [123]

    assert len(plan.scheduled_tasks) == 1

    scheduled = plan.scheduled_tasks[0]

    duration_minutes = int(
        (
            scheduled.end_time
            - scheduled.start_time
        ).total_seconds()
        / 60
    )

    assert duration_minutes == 75

    # La estimación original no debe modificarse.
    assert task.estimated_minutes == 60   

def test_create_plan_generates_routines_before_loading_tasks(
    monkeypatch,
):
    service = PlanningWorkflowService()

    monkeypatch.setattr(
        service.recurring_availability_service,
        "resolve_day_hours",
        lambda db,
        user_id,
        target_date,
        fallback_start_hour,
        fallback_end_hour: (
            fallback_start_hour,
            fallback_end_hour,
        ),
    )
    monkeypatch.setattr(
        service.recurring_availability_service,
        "build_unavailable_blocks",
        lambda db, user_id, target_date: [],
    )
    call_order = []

    def generate_for_user(
        db,
        user_id,
        target_date,
    ):
        call_order.append(
            (
                "routines",
                user_id,
                target_date,
            )
        )

        return []

    def get_plannable(
        db,
        user_id=None,
    ):
        call_order.append(
            (
                "tasks",
                user_id,
            )
        )

        return []

    monkeypatch.setattr(
        service.routine_occurrence_service,
        "generate_for_user",
        generate_for_user,
    )

    monkeypatch.setattr(
        service.task_service,
        "get_plannable",
        get_plannable,
    )

    monkeypatch.setattr(
        service.adaptive_profile_service,
        "get",
        lambda db, user_id=None: None,
    )

    request = PlanningFromDBRequest(
        plan_date=date(2026, 9, 28),
        day_start_hour=8,
        day_end_hour=20,
        break_minutes=0,
        busy_blocks=[],
    )

    service.create_plan_from_db(
        db=None,
        request=request,
        user_id=123,
    )

    assert call_order == [
        (
            "routines",
            123,
            date(2026, 9, 28),
        ),
        (
            "tasks",
            123,
        ),
    ]


def test_explain_plan_generates_routines_and_scopes_tasks_by_user(
    monkeypatch,
):
    service = PlanningWorkflowService()

    monkeypatch.setattr(
        service.recurring_availability_service,
        "resolve_day_hours",
        lambda db,
        user_id,
        target_date,
        fallback_start_hour,
        fallback_end_hour: (
            fallback_start_hour,
            fallback_end_hour,
        ),
    )
    monkeypatch.setattr(
        service.recurring_availability_service,
        "build_unavailable_blocks",
        lambda db, user_id, target_date: [],
    )
    call_order = []

    def generate_for_user(
        db,
        user_id,
        target_date,
    ):
        call_order.append(
            (
                "routines",
                user_id,
                target_date,
            )
        )

        return []

    def get_plannable(
        db,
        user_id=None,
    ):
        call_order.append(
            (
                "tasks",
                user_id,
            )
        )

        return []

    monkeypatch.setattr(
        service.routine_occurrence_service,
        "generate_for_user",
        generate_for_user,
    )

    monkeypatch.setattr(
        service.task_service,
        "get_plannable",
        get_plannable,
    )

    monkeypatch.setattr(
        service.adaptive_profile_service,
        "get",
        lambda db, user_id=None: None,
    )

    request = PlanningFromDBRequest(
        plan_date=date(2026, 9, 28),
        day_start_hour=8,
        day_end_hour=20,
        break_minutes=0,
        busy_blocks=[],
    )

    service.explain_plan_from_db(
        db=None,
        request=request,
        user_id=123,
    )

    assert call_order == [
        (
            "routines",
            123,
            date(2026, 9, 28),
        ),
        (
            "tasks",
            123,
        ),
    ]

def test_create_plan_with_decisions_generates_routines_and_scopes_tasks_by_user(
    monkeypatch,
):
    service = PlanningWorkflowService()

    monkeypatch.setattr(
        service.recurring_availability_service,
        "resolve_day_hours",
        lambda db,
        user_id,
        target_date,
        fallback_start_hour,
        fallback_end_hour: (
            fallback_start_hour,
            fallback_end_hour,
        ),
    )
    monkeypatch.setattr(
        service.recurring_availability_service,
        "build_unavailable_blocks",
        lambda db, user_id, target_date: [],
    )
    call_order = []

    def generate_for_user(
        db,
        user_id,
        target_date,
    ):
        call_order.append(
            (
                "routines",
                user_id,
                target_date,
            )
        )

        return []

    def get_plannable(
        db,
        user_id=None,
    ):
        call_order.append(
            (
                "tasks",
                user_id,
            )
        )

        return []

    monkeypatch.setattr(
        service.routine_occurrence_service,
        "generate_for_user",
        generate_for_user,
    )

    monkeypatch.setattr(
        service.task_service,
        "get_plannable",
        get_plannable,
    )

    monkeypatch.setattr(
        service.adaptive_profile_service,
        "get",
        lambda db, user_id=None: None,
    )

    request = PlanningFromDBRequest(
        plan_date=date(2026, 9, 28),
        day_start_hour=8,
        day_end_hour=20,
        break_minutes=0,
        busy_blocks=[],
    )

    service.create_plan_with_decisions_from_db(
        db=None,
        request=request,
        user_id=123,
    )

    assert call_order == [
        (
            "routines",
            123,
            date(2026, 9, 28),
        ),
        (
            "tasks",
            123,
        ),
    ]

def test_create_plan_uses_recurring_availability(
    monkeypatch,
):
    service = PlanningWorkflowService()

    task = Task(
        title="Preparar informe",
        estimated_minutes=60,
    )

    monkeypatch.setattr(
        service.routine_occurrence_service,
        "generate_for_user",
        lambda db, user_id, target_date: [],
    )

    monkeypatch.setattr(
        service.task_service,
        "get_plannable",
        lambda db, user_id=None: [task],
    )

    monkeypatch.setattr(
        service.adaptive_profile_service,
        "get",
        lambda db, user_id=None: None,
    )

    received_arguments = []

    def resolve_day_hours(
        db,
        user_id,
        target_date,
        fallback_start_hour,
        fallback_end_hour,
    ):
        received_arguments.append(
            (
                user_id,
                target_date,
                fallback_start_hour,
                fallback_end_hour,
            )
        )

        return 9, 17

    monkeypatch.setattr(
        service.recurring_availability_service,
        "resolve_day_hours",
        resolve_day_hours,
    )
    monkeypatch.setattr(
        service.recurring_availability_service,
        "build_unavailable_blocks",
        lambda db, user_id, target_date: [],
    )
    request = PlanningFromDBRequest(
        plan_date=date(2026, 9, 28),
        day_start_hour=8,
        day_end_hour=20,
        break_minutes=0,
        busy_blocks=[],
    )

    plan = service.create_plan_from_db(
        db=None,
        request=request,
        user_id=123,
    )

    assert received_arguments == [
        (
            123,
            date(2026, 9, 28),
            8,
            20,
        )
    ]

    assert len(plan.scheduled_tasks) == 1

    scheduled = plan.scheduled_tasks[0]

    assert scheduled.start_time == datetime(
        2026,
        9,
        28,
        9,
        0,
    )

    assert scheduled.end_time == datetime(
        2026,
        9,
        28,
        10,
        0,
    )    

def test_create_plan_respects_gap_between_availability_intervals(
    monkeypatch,
):
    service = PlanningWorkflowService()

    task_1 = Task(
        title="Tarea 1",
        estimated_minutes=60,
    )

    task_2 = Task(
        title="Tarea 2",
        estimated_minutes=60,
    )

    monkeypatch.setattr(
        service.routine_occurrence_service,
        "generate_for_user",
        lambda db, user_id, target_date: [],
    )

    monkeypatch.setattr(
        service.task_service,
        "get_plannable",
        lambda db, user_id=None: [
            task_1,
            task_2,
        ],
    )

    monkeypatch.setattr(
        service.adaptive_profile_service,
        "get",
        lambda db, user_id=None: None,
    )

    monkeypatch.setattr(
        service.recurring_availability_service,
        "resolve_day_hours",
        lambda db,
        user_id,
        target_date,
        fallback_start_hour,
        fallback_end_hour: (
            8,
            18,
        ),
    )

    unavailable_block = TimeBlock(
        start_time=datetime(
            2026,
            9,
            28,
            13,
            0,
        ),
        end_time=datetime(
            2026,
            9,
            28,
            14,
            0,
        ),
        title="No disponible",
        block_type=BlockType.BREAK,
    )

    monkeypatch.setattr(
        service.recurring_availability_service,
        "build_unavailable_blocks",
        lambda db, user_id, target_date: [
            unavailable_block
        ],
    )

    request = PlanningFromDBRequest(
        plan_date=date(2026, 9, 28),
        day_start_hour=8,
        planning_start_time=datetime(
            2026,
            9,
            28,
            12,
            0,
        ).time(),
        day_end_hour=20,
        break_minutes=0,
        busy_blocks=[],
    )

    plan = service.create_plan_from_db(
        db=None,
        request=request,
        user_id=123,
    )

    assert len(plan.scheduled_tasks) == 2

    first = plan.scheduled_tasks[0]
    second = plan.scheduled_tasks[1]

    assert first.start_time == datetime(
        2026,
        9,
        28,
        12,
        0,
    )
    assert first.end_time == datetime(
        2026,
        9,
        28,
        13,
        0,
    )

    assert second.start_time == datetime(
        2026,
        9,
        28,
        14,
        0,
    )
    assert second.end_time == datetime(
        2026,
        9,
        28,
        15,
        0,
    )    

def test_build_planning_request_includes_calendar_blocks(
    monkeypatch,
):
    service = PlanningWorkflowService()

    task = Task(
        title="Preparar informe",
        estimated_minutes=60,
    )

    manual_block = TimeBlock(
        start_time=datetime(
            2026,
            9,
            28,
            9,
            0,
        ),
        end_time=datetime(
            2026,
            9,
            28,
            10,
            0,
        ),
        title="Bloque manual",
        block_type=BlockType.EVENT,
    )

    availability_block = TimeBlock(
        start_time=datetime(
            2026,
            9,
            28,
            13,
            0,
        ),
        end_time=datetime(
            2026,
            9,
            28,
            14,
            0,
        ),
        title="No disponible",
        block_type=BlockType.BREAK,
    )

    calendar_block = TimeBlock(
        start_time=datetime(
            2026,
            9,
            28,
            16,
            0,
        ),
        end_time=datetime(
            2026,
            9,
            28,
            17,
            0,
        ),
        title="Evento Google",
        block_type=BlockType.EVENT,
    )

    monkeypatch.setattr(
        service.recurring_availability_service,
        "resolve_day_hours",
        lambda db,
        user_id,
        target_date,
        fallback_start_hour,
        fallback_end_hour: (
            fallback_start_hour,
            fallback_end_hour,
        ),
    )

    monkeypatch.setattr(
        service.recurring_availability_service,
        "build_unavailable_blocks",
        lambda db, user_id, target_date: [
            availability_block
        ],
    )

    monkeypatch.setattr(
        service.calendar_service,
        "get_busy_blocks",
        lambda target_date: [
            calendar_block
        ],
    )

    request = PlanningFromDBRequest(
        plan_date=date(2026, 9, 28),
        day_start_hour=8,
        day_end_hour=20,
        break_minutes=0,
        busy_blocks=[
            manual_block
        ],
    )

    planning_request = (
        service.build_planning_request(
            db=None,
            tasks=[task],
            request=request,
            user_id=123,
        )
    )

    assert planning_request.busy_blocks == [
        manual_block,
        availability_block,
        calendar_block,
    ]    