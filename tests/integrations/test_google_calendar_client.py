from datetime import datetime
from unittest.mock import MagicMock, patch

from app.integrations.google_calendar_client import GoogleCalendarClient


def test_get_events_fetches_and_parses_google_events():
    auth_service = MagicMock()
    credentials = MagicMock()
    auth_service.get_credentials.return_value = credentials

    google_response = {
        "items": [
            {
                "id": "event-1",
                "summary": "Reunión de trabajo",
                "start": {
                    "dateTime": "2026-09-28T10:00:00-03:00",
                },
                "end": {
                    "dateTime": "2026-09-28T11:00:00-03:00",
                },
            }
        ]
    }

    events_resource = MagicMock()
    events_resource.list.return_value.execute.return_value = (
        google_response
    )

    google_service = MagicMock()
    google_service.events.return_value = events_resource

    start_time = datetime.fromisoformat(
        "2026-09-28T00:00:00-03:00"
    )
    end_time = datetime.fromisoformat(
        "2026-09-29T00:00:00-03:00"
    )

    with patch(
        "app.integrations.google_calendar_client.build",
        return_value=google_service,
    ):
        client = GoogleCalendarClient(
            auth_service=auth_service
        )

        events = client.get_events(
            start_time=start_time,
            end_time=end_time,
        )

    assert len(events) == 1

    event = events[0]

    assert event.external_id == "event-1"
    assert event.title == "Reunión de trabajo"
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
    assert event.all_day is False

    auth_service.get_credentials.assert_called_once()

    events_resource.list.assert_called_once_with(
        calendarId="primary",
        timeMin=start_time.isoformat(),
        timeMax=end_time.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    )

def test_get_events_adds_timezone_to_naive_query_datetimes():
    auth_service = MagicMock()
    auth_service.get_credentials.return_value = MagicMock()

    events_resource = MagicMock()
    events_resource.list.return_value.execute.return_value = {
        "items": []
    }

    google_service = MagicMock()
    google_service.events.return_value = events_resource

    start_time = datetime(
        2026,
        9,
        28,
        0,
        0,
    )
    end_time = datetime(
        2026,
        9,
        29,
        0,
        0,
    )

    with patch(
        "app.integrations.google_calendar_client.build",
        return_value=google_service,
    ):
        client = GoogleCalendarClient(
            auth_service=auth_service
        )

        client.get_events(
            start_time=start_time,
            end_time=end_time,
        )

    call_kwargs = (
        events_resource.list.call_args.kwargs
    )

    assert (
        datetime.fromisoformat(
            call_kwargs["timeMin"]
        ).tzinfo
        is not None
    )

    assert (
        datetime.fromisoformat(
            call_kwargs["timeMax"]
        ).tzinfo
        is not None
    )    

def test_get_events_fetches_all_pages():
    auth_service = MagicMock()
    auth_service.get_credentials.return_value = MagicMock()

    first_request = MagicMock()
    first_request.execute.return_value = {
        "items": [
            {
                "id": "event-1",
                "summary": "Primera reunión",
                "start": {
                    "dateTime": "2026-09-28T10:00:00-03:00",
                },
                "end": {
                    "dateTime": "2026-09-28T11:00:00-03:00",
                },
            }
        ],
        "nextPageToken": "page-2",
    }

    second_request = MagicMock()
    second_request.execute.return_value = {
        "items": [
            {
                "id": "event-2",
                "summary": "Segunda reunión",
                "start": {
                    "dateTime": "2026-09-28T14:00:00-03:00",
                },
                "end": {
                    "dateTime": "2026-09-28T15:00:00-03:00",
                },
            }
        ]
    }

    events_resource = MagicMock()
    events_resource.list.side_effect = [
        first_request,
        second_request,
    ]

    google_service = MagicMock()
    google_service.events.return_value = events_resource

    start_time = datetime.fromisoformat(
        "2026-09-28T00:00:00-03:00"
    )
    end_time = datetime.fromisoformat(
        "2026-09-29T00:00:00-03:00"
    )

    with patch(
        "app.integrations.google_calendar_client.build",
        return_value=google_service,
    ):
        client = GoogleCalendarClient(
            auth_service=auth_service
        )

        events = client.get_events(
            start_time=start_time,
            end_time=end_time,
        )

    assert len(events) == 2
    assert events[0].external_id == "event-1"
    assert events[1].external_id == "event-2"

    assert events_resource.list.call_count == 2

    second_call_kwargs = (
        events_resource.list.call_args_list[1].kwargs
    )

    assert (
        second_call_kwargs["pageToken"]
        == "page-2"
    )    