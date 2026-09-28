from datetime import date, datetime

from app.models.calendar_event import CalendarEvent
from app.models.time_block import BlockType
from app.services.calendar_service import CalendarService

from app.models.schedule import PlanningRequest
from app.models.task import Task
from app.services.planner_service import PlannerService
def test_converts_calendar_event_to_time_block():
    service = CalendarService()

    event = CalendarEvent(
        external_id="event-123",
        title="Reunión de equipo",
        start_time=datetime(
            2026,
            9,
            28,
            10,
            0,
        ),
        end_time=datetime(
            2026,
            9,
            28,
            11,
            0,
        ),
    )

    block = service.event_to_time_block(event)

    assert block.title == "Reunión de equipo"
    assert block.start_time == event.start_time
    assert block.end_time == event.end_time
    assert block.block_type == BlockType.EVENT


def test_converts_multiple_events_to_time_blocks():
    service = CalendarService()

    events = [
        CalendarEvent(
            title="Reunión",
            start_time=datetime(
                2026,
                9,
                28,
                10,
                0,
            ),
            end_time=datetime(
                2026,
                9,
                28,
                11,
                0,
            ),
        ),
        CalendarEvent(
            title="Dentista",
            start_time=datetime(
                2026,
                9,
                28,
                15,
                0,
            ),
            end_time=datetime(
                2026,
                9,
                28,
                16,
                0,
            ),
        ),
    ]

    blocks = service.events_to_time_blocks(events)

    assert len(blocks) == 2

    assert (
        blocks[0].block_type
        == BlockType.EVENT
    )

    assert (
        blocks[1].block_type
        == BlockType.EVENT
    )

    assert blocks[0].title == "Reunión"
    assert blocks[1].title == "Dentista"

def test_calendar_event_blocks_planner_time():
    calendar_service = CalendarService()
    planner = PlannerService()

    event = CalendarEvent(
        external_id="google-event-123",
        title="Reunión de equipo",
        start_time=datetime(
            2026,
            9,
            28,
            8,
            0,
        ),
        end_time=datetime(
            2026,
            9,
            28,
            10,
            0,
        ),
    )

    busy_blocks = (
        calendar_service.events_to_time_blocks(
            [event]
        )
    )

    task = Task(
        title="Preparar informe",
        estimated_minutes=60,
    )

    request = PlanningRequest(
        tasks=[task],
        plan_date=date(
            2026,
            9,
            28,
        ),
        day_start_hour=8,
        day_end_hour=20,
        break_minutes=15,
        busy_blocks=busy_blocks,
    )

    plan = planner.create_plan(request)

    assert len(plan.scheduled_tasks) == 1

    scheduled = plan.scheduled_tasks[0]

    assert scheduled.task.title == "Preparar informe"

    assert scheduled.start_time == datetime(
        2026,
        9,
        28,
        10,
        15,
    )

    assert scheduled.end_time == datetime(
        2026,
        9,
        28,
        11,
        15,
    )    

def test_get_busy_blocks_fetches_events_for_target_date():
    from datetime import date
    from unittest.mock import MagicMock

    from app.models.calendar_event import CalendarEvent

    calendar_client = MagicMock()

    calendar_client.get_events.return_value = [
        CalendarEvent(
            external_id="event-1",
            title="Vacuna",
            start_time=datetime(
                2026,
                9,
                28,
                8,
                0,
            ),
            end_time=datetime(
                2026,
                9,
                28,
                9,
                0,
            ),
        )
    ]

    service = CalendarService(
        calendar_client=calendar_client
    )

    blocks = service.get_busy_blocks(
        date(2026, 9, 28)
    )

    assert len(blocks) == 1

    block = blocks[0]

    assert block.start_time == datetime(
        2026,
        9,
        28,
        8,
        0,
    )
    assert block.end_time == datetime(
        2026,
        9,
        28,
        9,
        0,
    )
    assert block.title == "Vacuna"
    assert block.block_type == BlockType.EVENT

    calendar_client.get_events.assert_called_once_with(
        start_time=datetime(
            2026,
            9,
            28,
            0,
            0,
        ),
        end_time=datetime(
            2026,
            9,
            28,
            23,
            59,
            59,
            999999,
        ),
    )    