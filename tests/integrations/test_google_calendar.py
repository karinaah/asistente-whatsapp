from app.integrations.google_calendar import (
    GoogleCalendarAdapter,
)
from datetime import datetime

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

def test_parse_event_normalizes_datetime_to_naive_local_time():
    adapter = GoogleCalendarAdapter()

    google_event = {
        "id": "event-1",
        "summary": "Reunión",
        "start": {
            "dateTime": "2026-09-28T10:00:00-03:00",
        },
        "end": {
            "dateTime": "2026-09-28T11:00:00-03:00",
        },
    }

    event = adapter.parse_event(google_event)

    assert event.start_time == datetime(
        2026,
        9,
        28,
        10,
        0,
    )
    assert event.end_time == datetime(
        2026,
        9,
        28,
        11,
        0,
    )

    assert event.start_time.tzinfo is None
    assert event.end_time.tzinfo is None    


def test_parse_events_ignores_cancelled_and_transparent_events():
    adapter = GoogleCalendarAdapter()

    google_events = [
        {
            "id": "confirmed-event",
            "summary": "Reunión",
            "status": "confirmed",
            "start": {
                "dateTime": "2026-09-28T10:00:00-03:00",
            },
            "end": {
                "dateTime": "2026-09-28T11:00:00-03:00",
            },
        },
        {
            "id": "cancelled-event",
            "summary": "Reunión cancelada",
            "status": "cancelled",
            "start": {
                "dateTime": "2026-09-28T12:00:00-03:00",
            },
            "end": {
                "dateTime": "2026-09-28T13:00:00-03:00",
            },
        },
        {
            "id": "transparent-event",
            "summary": "Disponible",
            "status": "confirmed",
            "transparency": "transparent",
            "start": {
                "dateTime": "2026-09-28T14:00:00-03:00",
            },
            "end": {
                "dateTime": "2026-09-28T15:00:00-03:00",
            },
        },
    ]

    events = adapter.parse_events(
        google_events
    )

    assert len(events) == 1
    assert events[0].external_id == "confirmed-event"
    assert events[0].title == "Reunión"    

def test_parse_events_ignores_all_day_events():
    adapter = GoogleCalendarAdapter()

    google_events = [
        {
            "id": "all-day-event",
            "summary": "Feriado",
            "start": {
                "date": "2026-09-28",
            },
            "end": {
                "date": "2026-09-29",
            },
        },
        {
            "id": "timed-event",
            "summary": "Reunión",
            "start": {
                "dateTime": "2026-09-28T10:00:00-03:00",
            },
            "end": {
                "dateTime": "2026-09-28T11:00:00-03:00",
            },
        },
    ]

    events = adapter.parse_events(
        google_events
    )

    assert len(events) == 1
    assert events[0].external_id == "timed-event"
    assert events[0].title == "Reunión"    

def test_parse_event_uses_default_title_when_summary_is_empty():
    adapter = GoogleCalendarAdapter()

    google_event = {
        "id": "event-without-title",
        "summary": "",
        "start": {
            "dateTime": "2026-09-28T10:00:00-03:00",
        },
        "end": {
            "dateTime": "2026-09-28T11:00:00-03:00",
        },
    }

    event = adapter.parse_event(
        google_event
    )

    assert event.title == "Evento"    