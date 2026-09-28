from datetime import datetime

from googleapiclient.discovery import build

from app.integrations.google_auth import GoogleAuthService
from app.integrations.google_calendar import GoogleCalendarAdapter
from app.models.calendar_event import CalendarEvent


class GoogleCalendarClient:
    def __init__(
        self,
        auth_service: GoogleAuthService | None = None,
        adapter: GoogleCalendarAdapter | None = None,
    ):
        self.auth_service = (
            auth_service or GoogleAuthService()
        )
        self.adapter = (
            adapter or GoogleCalendarAdapter()
        )

    def get_events(
        self,
        start_time: datetime,
        end_time: datetime,
        calendar_id: str = "primary",
    ) -> list[CalendarEvent]:
        if start_time.tzinfo is None:
            local_timezone = (
                datetime.now()
                .astimezone()
                .tzinfo
            )

            start_time = start_time.replace(
                tzinfo=local_timezone
            )

        if end_time.tzinfo is None:
            local_timezone = (
                datetime.now()
                .astimezone()
                .tzinfo
            )

            end_time = end_time.replace(
                tzinfo=local_timezone
            )
        
        credentials = (
            self.auth_service.get_credentials()
        )

        service = build(
            "calendar",
            "v3",
            credentials=credentials,
        )

        response = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=start_time.isoformat(),
                timeMax=end_time.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        google_events = response.get(
            "items",
            [],
        )

        return self.adapter.parse_events(
            google_events
        )