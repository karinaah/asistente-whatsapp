from datetime import date, datetime

from app.models.schedule import PlanningRequest
from app.models.time_block import BlockType
from app.services.planner_service import PlannerService
from tests.factories.task_factory import make_task
from tests.factories.time_block_factory import make_time_block
from app.models.task import TaskContext
from datetime import date, time

from app.models.planning_reason import (
    PlanningReasonCode,
)
from app.models.task import Task

def test_single_task_is_scheduled_at_day_start():
    planner = PlannerService()

    request = PlanningRequest(
        tasks=[
            make_task(
                title="Estudiar IA",
                estimated_minutes=60,
            )
        ],
        plan_date=date(2025, 7, 20),
        day_start_hour=8,
        day_end_hour=20,
        break_minutes=15,
        busy_blocks=[],
    )

    response = planner.create_plan(request)

    assert len(response.scheduled_tasks) == 1
    assert len(response.unscheduled_tasks) == 0

    scheduled = response.scheduled_tasks[0]

    assert scheduled.task.title == "Estudiar IA"
    assert scheduled.start_time.hour == 8
    assert scheduled.start_time.minute == 0
    assert scheduled.end_time.hour == 9
    assert scheduled.end_time.minute == 0




def test_task_is_scheduled_after_busy_block_and_break():
    planner = PlannerService()

    busy_block = make_time_block(
        start="08:00",
        end="09:00",
        title="Reunión",
        block_type=BlockType.EVENT,
    )

    request = PlanningRequest(
        tasks=[
            make_task(
                title="Estudiar IA",
                estimated_minutes=60,
            )
        ],
        plan_date=date(2025, 7, 20),
        day_start_hour=8,
        day_end_hour=20,
        break_minutes=15,
        busy_blocks=[busy_block],
    )

    response = planner.create_plan(request)

    assert len(response.scheduled_tasks) == 1
    assert len(response.unscheduled_tasks) == 0

    scheduled = response.scheduled_tasks[0]

    assert scheduled.start_time.hour == 9
    assert scheduled.start_time.minute == 15
    assert scheduled.end_time.hour == 10
    assert scheduled.end_time.minute == 15    

def test_task_is_unscheduled_when_it_does_not_fit_in_the_day():
    planner = PlannerService()

    request = PlanningRequest(
        tasks=[
            make_task(
                title="Tarea demasiado larga",
                estimated_minutes=180,
            )
        ],
        plan_date=date(2025, 7, 20),
        day_start_hour=8,
        day_end_hour=10,
        break_minutes=15,
        busy_blocks=[],
    )

    response = planner.create_plan(request)

    assert len(response.scheduled_tasks) == 0
    assert len(response.unscheduled_tasks) == 1
    assert response.unscheduled_tasks[0].title == "Tarea demasiado larga"    

def test_two_tasks_are_scheduled_sequentially():
    planner = PlannerService()

    request = PlanningRequest(
        tasks=[
            make_task(
                title="Primera",
                estimated_minutes=60,
                priority="alta",
            ),
            make_task(
                title="Segunda",
                estimated_minutes=30,
                priority="media",
            ),
        ],
        plan_date=date(2025, 7, 20),
        day_start_hour=8,
        day_end_hour=20,
        break_minutes=15,
        busy_blocks=[],
    )

    response = planner.create_plan(request)

    assert len(response.scheduled_tasks) == 2

    first = response.scheduled_tasks[0]
    second = response.scheduled_tasks[1]

    assert first.task.title == "Primera"
    assert first.start_time.hour == 8
    assert first.end_time.hour == 9

    assert second.task.title == "Segunda"
    assert second.start_time.hour == 9
    assert second.start_time.minute == 15
    assert second.end_time.hour == 9
    assert second.end_time.minute == 45    

def test_high_priority_task_is_scheduled_before_medium_priority_task():
    planner = PlannerService()

    request = PlanningRequest(
        tasks=[
            make_task(
                title="Media",
                estimated_minutes=60,
                priority="media",
            ),
            make_task(
                title="Alta",
                estimated_minutes=60,
                priority="alta",
            ),
        ],
        plan_date=date(2025, 7, 20),
        day_start_hour=8,
        day_end_hour=20,
        break_minutes=15,
        busy_blocks=[],
    )

    response = planner.create_plan(request)

    assert len(response.scheduled_tasks) == 2

    assert response.scheduled_tasks[0].task.title == "Alta"
    assert response.scheduled_tasks[1].task.title == "Media"    

def test_earlier_deadline_is_scheduled_first_when_priorities_are_equal():
    planner = PlannerService()

    request = PlanningRequest(
        tasks=[
            make_task(
                title="Deadline lejano",
                estimated_minutes=60,
                priority="media",
                deadline=datetime(2025, 7, 25, 18, 0),
            ),
            make_task(
                title="Deadline cercano",
                estimated_minutes=60,
                priority="media",
                deadline=datetime(2025, 7, 20, 18, 0),
            ),
        ],
        plan_date=date(2025, 7, 20),
        day_start_hour=8,
        day_end_hour=20,
        break_minutes=15,
        busy_blocks=[],
    )

    response = planner.create_plan(request)

    assert len(response.scheduled_tasks) == 2
    assert response.scheduled_tasks[0].task.title == "Deadline cercano"
    assert response.scheduled_tasks[1].task.title == "Deadline lejano"  

def test_longer_task_is_scheduled_first_when_priority_and_deadline_are_equal():
    planner = PlannerService()

    shared_deadline = datetime(2025, 7, 20, 18, 0)

    request = PlanningRequest(
        tasks=[
            make_task(
                title="Tarea corta",
                estimated_minutes=30,
                priority="media",
                deadline=shared_deadline,
            ),
            make_task(
                title="Tarea larga",
                estimated_minutes=90,
                priority="media",
                deadline=shared_deadline,
            ),
        ],
        plan_date=date(2025, 7, 20),
        day_start_hour=8,
        day_end_hour=20,
        break_minutes=15,
        busy_blocks=[],
    )

    response = planner.create_plan(request)

    assert len(response.scheduled_tasks) == 2
    assert response.scheduled_tasks[0].task.title == "Tarea larga"
    assert response.scheduled_tasks[1].task.title == "Tarea corta"      


def test_timeline_contains_tasks_and_break_in_order():
    planner = PlannerService()

    request = PlanningRequest(
        tasks=[
            make_task(
                title="Primera",
                estimated_minutes=60,
                priority="alta",
            ),
            make_task(
                title="Segunda",
                estimated_minutes=30,
                priority="media",
            ),
        ],
        plan_date=date(2025, 7, 20),
        day_start_hour=8,
        day_end_hour=20,
        break_minutes=15,
        busy_blocks=[],
    )

    response = planner.create_plan(request)

    assert len(response.timeline) == 3

    first_task = response.timeline[0]
    break_block = response.timeline[1]
    second_task = response.timeline[2]

    assert first_task.block_type == BlockType.TASK
    assert first_task.title == "Primera"

    assert break_block.block_type == BlockType.BREAK
    assert break_block.start_time.hour == 9
    assert break_block.start_time.minute == 0
    assert break_block.end_time.hour == 9
    assert break_block.end_time.minute == 15

    assert second_task.block_type == BlockType.TASK
    assert second_task.title == "Segunda"    

def test_timeline_contains_busy_block_break_and_task_in_order():
    planner = PlannerService()

    busy_block = make_time_block(
        start="08:00",
        end="09:00",
        title="Reunión",
        block_type=BlockType.EVENT,
    )

    request = PlanningRequest(
        tasks=[
            make_task(
                title="Estudiar IA",
                estimated_minutes=60,
            )
        ],
        plan_date=date(2025, 7, 20),
        day_start_hour=8,
        day_end_hour=20,
        break_minutes=15,
        busy_blocks=[busy_block],
    )

    response = planner.create_plan(request)

    assert len(response.timeline) == 3

    event_block = response.timeline[0]
    break_block = response.timeline[1]
    task_block = response.timeline[2]

    assert event_block.block_type == BlockType.EVENT
    assert event_block.title == "Reunión"

    assert break_block.block_type == BlockType.BREAK
    assert break_block.start_time.hour == 9
    assert break_block.start_time.minute == 0
    assert break_block.end_time.hour == 9
    assert break_block.end_time.minute == 15

    assert task_block.block_type == BlockType.TASK
    assert task_block.title == "Estudiar IA"
    assert task_block.start_time.hour == 9
    assert task_block.start_time.minute == 15    

def test_task_is_scheduled_in_first_available_slot_between_busy_blocks():
    planner = PlannerService()

    first_busy_block = make_time_block(
        start="08:00",
        end="09:00",
        title="Reunión de equipo",
        block_type=BlockType.EVENT,
    )

    second_busy_block = make_time_block(
        start="10:30",
        end="11:30",
        title="Llamada con cliente",
        block_type=BlockType.EVENT,
    )

    request = PlanningRequest(
        tasks=[
            make_task(
                title="Preparar informe",
                estimated_minutes=60,
            )
        ],
        plan_date=date(2025, 7, 20),
        day_start_hour=8,
        day_end_hour=20,
        break_minutes=15,
        busy_blocks=[
            first_busy_block,
            second_busy_block,
        ],
    )

    response = planner.create_plan(request)

    assert len(response.scheduled_tasks) == 1
    assert len(response.unscheduled_tasks) == 0

    scheduled = response.scheduled_tasks[0]

    assert scheduled.start_time.hour == 9
    assert scheduled.start_time.minute == 15
    assert scheduled.end_time.hour == 10
    assert scheduled.end_time.minute == 15    

def test_plan_filters_tasks_by_work_context():
    planner = PlannerService()

    request = PlanningRequest(
        tasks=[
            make_task(
                title="Preparar informe",
                context=TaskContext.work,
                priority="alta",
            ),
            make_task(
                title="Comprar comida",
                context=TaskContext.personal,
                priority="alta",
            ),
        ],
        plan_date=date(2025, 7, 20),
        day_start_hour=8,
        day_end_hour=20,
        break_minutes=15,
        busy_blocks=[],
        context=TaskContext.work,
    )

    response = planner.create_plan(request)

    assert len(response.scheduled_tasks) == 1
    assert response.scheduled_tasks[0].task.title == "Preparar informe"  

def test_plan_filters_tasks_by_personal_context():
    planner = PlannerService()

    request = PlanningRequest(
        tasks=[
            make_task(
                title="Preparar informe",
                context=TaskContext.work,
                priority="alta",
            ),
            make_task(
                title="Comprar comida",
                context=TaskContext.personal,
                priority="alta",
            ),
        ],
        plan_date=date(2025, 7, 20),
        day_start_hour=8,
        day_end_hour=20,
        break_minutes=15,
        busy_blocks=[],
        context=TaskContext.personal,
    )

    response = planner.create_plan(request)

    assert len(response.scheduled_tasks) == 1
    assert response.scheduled_tasks[0].task.title == "Comprar comida"      

def test_plan_includes_all_tasks_when_context_is_not_provided():
    planner = PlannerService()

    request = PlanningRequest(
        tasks=[
            make_task(
                title="Preparar informe",
                context=TaskContext.work,
                priority="alta",
            ),
            make_task(
                title="Comprar comida",
                context=TaskContext.personal,
                priority="media",
            ),
        ],
        plan_date=date(2025, 7, 20),
        day_start_hour=8,
        day_end_hour=20,
        break_minutes=15,
        busy_blocks=[],
        context=None,
    )

    response = planner.create_plan(request)

    assert len(response.scheduled_tasks) == 2
    assert response.scheduled_tasks[0].task.title == "Preparar informe"
    assert response.scheduled_tasks[1].task.title == "Comprar comida"    


def test_explain_plan_returns_preferred_start_reason():
    planner = PlannerService()

    task = Task(
        title="Preparar presentación",
        estimated_minutes=60,
        category="trabajo",
        context="trabajo",
        preferred_start_time=time(hour=21),
    )

    request = PlanningRequest(
        tasks=[task],
        plan_date=date.fromisoformat("2026-08-10"),
        day_start_hour=8,
        day_end_hour=23,
        break_minutes=0,
        busy_blocks=[],
        context="trabajo",
    )

    decisions = planner.explain_plan(request)

    assert len(decisions) == 1

    reason_codes = {
        reason.code
        for reason in decisions[0].reasons
    }

    assert (
        PlanningReasonCode.preferred_start_time
        in reason_codes
    )    