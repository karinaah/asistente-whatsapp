from datetime import date, datetime, time

from app.integrations.google_calendar_client import (
    GoogleCalendarClient,
)
from app.models.calendar_event import CalendarEvent
from app.models.time_block import BlockType, TimeBlock


class CalendarService:
    def __init__(
        self,
        calendar_client: GoogleCalendarClient | None = None,
    ):
        self.calendar_client = (
            calendar_client or GoogleCalendarClient()
        )

    def event_to_time_block(
        self,
        event: CalendarEvent,
    ) -> TimeBlock:
        return TimeBlock(
            start_time=event.start_time,
            end_time=event.end_time,
            title=event.title,
            block_type=BlockType.EVENT,
        )

    def events_to_time_blocks(
        self,
        events: list[CalendarEvent],
    ) -> list[TimeBlock]:
        return [
            self.event_to_time_block(event)
            for event in events
        ]

    def get_busy_blocks(
        self,
        target_date: date,
    ) -> list[TimeBlock]:
        start_time = datetime.combine(
            target_date,
            time.min,
        )

        end_time = datetime.combine(
            target_date,
            time.max,
        )



        try:
            events = self.calendar_client.get_events(
                start_time=start_time,
                end_time=end_time,
            )
        except Exception:
            return []

        return self.events_to_time_blocks(
            events
        )