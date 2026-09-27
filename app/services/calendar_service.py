from app.models.calendar_event import CalendarEvent
from app.models.time_block import BlockType, TimeBlock


class CalendarService:
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