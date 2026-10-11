from datetime import datetime

from app.models.schedule import PlanningResponse, ScheduledTask
from app.models.task import Task
from app.services.daily_replanning_service import DailyReplanningService
from app.models.time_block import BlockType
from app.models.time_block import TimeBlock

def test_separate_protected_and_pending_tasks():
    service = DailyReplanningService()

    now = datetime(2026, 10, 11, 16, 0)

    def make_scheduled_task(task_id, title, start_hour, end_hour):
        task = Task(
            id=task_id,
            user_id=1,
            title=title,
            estimated_minutes=(end_hour - start_hour) * 60,
        )

        return ScheduledTask(
            task=task,
            start_time=datetime(2026, 10, 11, start_hour, 0),
            end_time=datetime(2026, 10, 11, end_hour, 0),
        )

    completed = make_scheduled_task(
        1, "Código tesis", 10, 12
    )

    already_started = make_scheduled_task(
        2, "Proyectos personales", 14, 17
    )

    future_pending = make_scheduled_task(
        3, "Cocinar", 18, 19
    )

    plan = PlanningResponse(
        scheduled_tasks=[
            completed,
            already_started,
            future_pending,
        ],
        unscheduled_tasks=[],
        timeline=[],
    )

    protected, pending = service.separate_tasks(
        plan=plan,
        completed_task_ids={1},
        now=now,
    )

    assert {item.task.id for item in protected} == {1, 2}
    assert {item.task.id for item in pending} == {3}

def test_protected_task_blocks_remaining_time():
    service = DailyReplanningService()

    now = datetime(2026, 10, 11, 16, 0)

    task = Task(
        id=1,
        user_id=1,
        title="Proyectos personales",
        estimated_minutes=180,
    )

    scheduled = ScheduledTask(
        task=task,
        start_time=datetime(2026, 10, 11, 14, 0),
        end_time=datetime(2026, 10, 11, 17, 0),
    )

    blocks = service.build_protected_blocks(
        protected_tasks=[scheduled],
        now=now,
    )

    assert len(blocks) == 1
    assert blocks[0].start_time == now
    assert blocks[0].end_time == datetime(2026, 10, 11, 17, 0)
    assert blocks[0].block_type == BlockType.TASK

def test_replanning_preserves_future_events():
    service = DailyReplanningService()

    now = datetime(2026, 10, 11, 16, 0)

    event = TimeBlock(
        start_time=datetime(2026, 10, 11, 17, 30),
        end_time=datetime(2026, 10, 11, 18, 30),
        title="Reunión",
        block_type=BlockType.EVENT,
    )

    plan = PlanningResponse(
        scheduled_tasks=[],
        unscheduled_tasks=[],
        timeline=[event],
    )

    blocks = service.build_event_blocks(
        plan=plan,
        now=now,
    )

    assert len(blocks) == 1
    assert blocks[0].title == "Reunión"
    assert blocks[0].start_time == event.start_time
    assert blocks[0].end_time == event.end_time
    assert blocks[0].block_type == BlockType.EVENT

def test_collect_pending_tasks_includes_unscheduled():
    service = DailyReplanningService()

    cooking = Task(
        id=1,
        user_id=1,
        title="Cocinar",
        estimated_minutes=60,
    )

    cleaning = Task(
        id=2,
        user_id=1,
        title="Aseo",
        estimated_minutes=45,
    )

    completed = Task(
        id=3,
        user_id=1,
        title="Código tesis",
        estimated_minutes=120,
    )

    scheduled_cooking = ScheduledTask(
        task=cooking,
        start_time=datetime(2026, 10, 11, 17, 0),
        end_time=datetime(2026, 10, 11, 18, 0),
    )

    plan = PlanningResponse(
        scheduled_tasks=[scheduled_cooking],
        unscheduled_tasks=[cleaning, completed, cooking],
        timeline=[],
    )

    pending = service.collect_pending_tasks(
        plan=plan,
        pending_scheduled_tasks=[scheduled_cooking],
        completed_task_ids={3},
    )

    assert {task.id for task in pending} == {1, 2}
    assert len(pending) == 2

def test_build_replanning_request():
    service = DailyReplanningService()

    now = datetime(2026, 10, 11, 16, 0)

    completed = Task(
        id=1,
        user_id=1,
        title="Código tesis",
        estimated_minutes=120,
    )

    pending = Task(
        id=2,
        user_id=1,
        title="Cocinar",
        estimated_minutes=60,
    )

    cleaning = Task(
        id=3,
        user_id=1,
        title="Aseo",
        estimated_minutes=45,
    )

    plan = PlanningResponse(
        scheduled_tasks=[
            ScheduledTask(
                task=completed,
                start_time=datetime(2026, 10, 11, 10, 0),
                end_time=datetime(2026, 10, 11, 12, 0),
            ),
            ScheduledTask(
                task=pending,
                start_time=datetime(2026, 10, 11, 18, 0),
                end_time=datetime(2026, 10, 11, 19, 0),
            ),
        ],
        unscheduled_tasks=[cleaning],
        timeline=[
            TimeBlock(
                start_time=datetime(2026, 10, 11, 17, 0),
                end_time=datetime(2026, 10, 11, 18, 0),
                title="Reunión",
                block_type=BlockType.EVENT,
            ),
        ],
    )

    request = service.build_replanning_request(
        plan=plan,
        completed_task_ids={1},
        now=now,
    )

    assert request.planning_start_time == now.time()
    assert {task.id for task in request.tasks} == {2, 3}
    assert len(request.busy_blocks) == 1
    assert request.busy_blocks[0].title == "Reunión"

def test_generate_proposal_preserves_completed_tasks():
    service = DailyReplanningService()

    now = datetime(2026, 10, 11, 16, 0)

    completed = Task(
        id=1,
        user_id=1,
        title="Código tesis",
        estimated_minutes=120,
    )

    pending = Task(
        id=2,
        user_id=1,
        title="Cocinar",
        estimated_minutes=60,
    )

    original = PlanningResponse(
        scheduled_tasks=[
            ScheduledTask(
                task=completed,
                start_time=datetime(2026, 10, 11, 10, 0),
                end_time=datetime(2026, 10, 11, 12, 0),
            ),
            ScheduledTask(
                task=pending,
                start_time=datetime(2026, 10, 11, 18, 0),
                end_time=datetime(2026, 10, 11, 19, 0),
            ),
        ],
        unscheduled_tasks=[],
        timeline=[
            TimeBlock(
                start_time=datetime(2026, 10, 11, 10, 0),
                end_time=datetime(2026, 10, 11, 12, 0),
                title="Código tesis",
                block_type=BlockType.TASK,
            ),
        ],
    )

    proposal = service.generate_proposal(
        plan=original,
        completed_task_ids={1},
        now=now,
    )

    completed_in_proposal = [
        item
        for item in proposal.scheduled_tasks
        if item.task.id == 1
    ]

    assert len(completed_in_proposal) == 1
    assert completed_in_proposal[0].start_time == datetime(
        2026, 10, 11, 10, 0
    )
    assert completed_in_proposal[0].end_time == datetime(
        2026, 10, 11, 12, 0
    )

    # La agenda confirmada no se modifica.
    assert original.scheduled_tasks[1].start_time == datetime(
        2026, 10, 11, 18, 0
    )

def test_generate_proposal_preserves_ongoing_event():
    service = DailyReplanningService()

    now = datetime(2026, 10, 11, 16, 0)

    event = TimeBlock(
        start_time=datetime(2026, 10, 11, 15, 30),
        end_time=datetime(2026, 10, 11, 16, 30),
        title="Reunión",
        block_type=BlockType.EVENT,
    )

    pending = Task(
        id=2,
        user_id=1,
        title="Cocinar",
        estimated_minutes=60,
    )

    original = PlanningResponse(
        scheduled_tasks=[],
        unscheduled_tasks=[pending],
        timeline=[event],
    )

    proposal = service.generate_proposal(
        plan=original,
        completed_task_ids=set(),
        now=now,
    )

    meetings = [
        block
        for block in proposal.timeline
        if block.title == "Reunión"
        and block.block_type == BlockType.EVENT
    ]

    assert len(meetings) == 1
    assert meetings[0].start_time == event.start_time
    assert meetings[0].end_time == event.end_time

    # Ninguna tarea puede superponerse con la reunión.
    for scheduled in proposal.scheduled_tasks:
        assert (
            scheduled.end_time <= event.start_time
            or scheduled.start_time >= event.end_time
        )

def test_generate_proposal_does_not_duplicate_breaks():
    service = DailyReplanningService()

    now = datetime(2026, 10, 11, 16, 0)

    completed = Task(
        id=1,
        user_id=1,
        title="Código tesis",
        estimated_minutes=120,
    )

    pending = Task(
        id=2,
        user_id=1,
        title="Cocinar",
        estimated_minutes=60,
    )

    original_break = TimeBlock(
        start_time=datetime(2026, 10, 11, 12, 0),
        end_time=datetime(2026, 10, 11, 12, 15),
        title="Descanso",
        block_type=BlockType.BREAK,
    )

    original = PlanningResponse(
        scheduled_tasks=[
            ScheduledTask(
                task=completed,
                start_time=datetime(2026, 10, 11, 10, 0),
                end_time=datetime(2026, 10, 11, 12, 0),
            )
        ],
        unscheduled_tasks=[pending],
        timeline=[
            TimeBlock(
                start_time=datetime(2026, 10, 11, 10, 0),
                end_time=datetime(2026, 10, 11, 12, 0),
                title="Código tesis",
                block_type=BlockType.TASK,
            ),
            original_break,
        ],
    )

    proposal = service.generate_proposal(
        plan=original,
        completed_task_ids={1},
        now=now,
    )

    breaks = [
        block
        for block in proposal.timeline
        if block.block_type == BlockType.BREAK
    ]

    for index, first in enumerate(breaks):
        for second in breaks[index + 1:]:
            assert (
                first.end_time <= second.start_time
                or second.end_time <= first.start_time
            ) 