from datetime import datetime

from app.models.calendar_event import CalendarEvent


class GoogleCalendarAdapter:
    def parse_event(
        self,
        google_event: dict,
    ) -> CalendarEvent:
        start = google_event["start"]
        end = google_event["end"]

        all_day = (
            "date" in start
            and "dateTime" not in start
        )

        if all_day:
            start_time = datetime.fromisoformat(
                start["date"]
            )
            end_time = datetime.fromisoformat(
                end["date"]
            )

        else:
            start_time = datetime.fromisoformat(
                start["dateTime"]
            ).replace(tzinfo=None)

            end_time = datetime.fromisoformat(
                end["dateTime"]
            ).replace(tzinfo=None)
        return CalendarEvent(
            external_id=google_event.get("id"),
            title=google_event.get("summary") or "Evento",
            start_time=start_time,
            end_time=end_time,
            all_day=all_day,
        )

    def parse_events(
        self,
        google_events: list[dict],
    ) -> list[CalendarEvent]:
        blocking_events = [
            event
            for event in google_events
            if event.get("status") != "cancelled"
            and event.get("transparency") != "transparent"
            and "dateTime" in event.get("start", {})
        ]

        return [
            self.parse_event(event)
            for event in blocking_events
        ]