from app.integrations.google_calendar import (
    GoogleCalendarAdapter,
)


def test_parses_google_calendar_timed_event():
    adapter = GoogleCalendarAdapter()

    google_event = {
        "id": "abc123",
        "summary": "Reunión de equipo",
        "start": {
            "dateTime": (
                "2026-09-28T10:00:00-03:00"
            ),
        },
        "end": {
            "dateTime": (
                "2026-09-28T11:00:00-03:00"
            ),
        },
    }

    event = adapter.parse_event(
        google_event
    )

    assert event.external_id == "abc123"
    assert event.title == "Reunión de equipo"
    assert event.start_time.hour == 10
    assert event.end_time.hour == 11
    assert event.all_day is False


def test_parses_google_calendar_all_day_event():
    adapter = GoogleCalendarAdapter()

    google_event = {
        "id": "all-day-123",
        "summary": "Feriado",
        "start": {
            "date": "2026-09-28",
        },
        "end": {
            "date": "2026-09-29",
        },
    }

    event = adapter.parse_event(
        google_event
    )

    assert event.external_id == "all-day-123"
    assert event.title == "Feriado"
    assert event.start_time.hour == 0
    assert event.end_time.hour == 0
    assert event.all_day is True


def test_parses_multiple_google_calendar_events():
    adapter = GoogleCalendarAdapter()

    google_events = [
        {
            "id": "event-1",
            "summary": "Reunión",
            "start": {
                "dateTime": (
                    "2026-09-28T10:00:00-03:00"
                ),
            },
            "end": {
                "dateTime": (
                    "2026-09-28T11:00:00-03:00"
                ),
            },
        },
        {
            "id": "event-2",
            "summary": "Dentista",
            "start": {
                "dateTime": (
                    "2026-09-28T15:00:00-03:00"
                ),
            },
            "end": {
                "dateTime": (
                    "2026-09-28T16:00:00-03:00"
                ),
            },
        },
    ]

    events = adapter.parse_events(
        google_events
    )

    assert len(events) == 2
    assert events[0].title == "Reunión"
    assert events[1].title == "Dentista"