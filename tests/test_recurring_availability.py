from datetime import time

from app.models.recurring_availability import (
    RecurringAvailability,
)
from app.models.routine import Weekday
import pytest
from pydantic import ValidationError

def test_creates_recurring_availability():
    availability = RecurringAvailability(
        user_id=1,
        weekday=Weekday.monday,
        start_time=time(8, 0),
        end_time=time(18, 0),
    )

    assert availability.user_id == 1
    assert availability.weekday == Weekday.monday
    assert availability.start_time == time(8, 0)
    assert availability.end_time == time(18, 0)
    assert availability.active is True

def test_recurring_availability_requires_end_after_start():
    with pytest.raises(
        ValidationError,
        match="end_time must be after start_time",
    ):
        RecurringAvailability(
            user_id=1,
            weekday=Weekday.monday,
            start_time=time(18, 0),
            end_time=time(8, 0),
        )    