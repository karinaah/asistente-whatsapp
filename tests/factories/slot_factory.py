from datetime import datetime

from app.services.planner_service import AvailableSlot


def make_slot(
    start: str,
    end: str,
    *,
    date: str = "2025-07-20",
) -> AvailableSlot:
    return AvailableSlot(
        start_time=datetime.fromisoformat(
            f"{date}T{start}:00"
        ),
        end_time=datetime.fromisoformat(
            f"{date}T{end}:00"
        ),
    )