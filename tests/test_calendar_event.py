from datetime import datetime

from app.models.calendar_event import CalendarEvent


def test_creates_calendar_event():
    event = CalendarEvent(
        external_id="google-event-123",
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

    assert event.external_id == "google-event-123"
    assert event.title == "Reunión de equipo"
    assert event.start_time.hour == 10
    assert event.end_time.hour == 11
    assert event.all_day is False


def test_creates_all_day_calendar_event():
    event = CalendarEvent(
        title="Feriado",
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
            29,
            0,
            0,
        ),
        all_day=True,
    )

    assert event.all_day is True