from datetime import time

import pytest
from pydantic import ValidationError

from app.models.routine import Routine, Weekday
from app.models.task import (
    ActivityType,
    TaskCategory,
    TaskContext,
    TaskWorkspace,
)


def test_routine_creates_recurring_activity():
    routine = Routine(
        user_id=1,
        title="Yoga",
        weekdays=[
            Weekday.monday,
            Weekday.wednesday,
            Weekday.friday,
        ],
        preferred_start_time=time(19, 0),
        estimated_minutes=90,
        category=TaskCategory.health,
    )

    assert routine.user_id == 1
    assert routine.title == "Yoga"
    assert routine.weekdays == [
        Weekday.monday,
        Weekday.wednesday,
        Weekday.friday,
    ]
    assert routine.preferred_start_time == time(19, 0)
    assert routine.estimated_minutes == 90
    assert routine.category == TaskCategory.health
    assert routine.context == TaskContext.personal
    assert routine.workspace == TaskWorkspace.personal
    assert routine.activity_type == ActivityType.routine
    assert routine.active is True


def test_routine_requires_at_least_one_weekday():
    with pytest.raises(ValidationError):
        Routine(
            user_id=1,
            title="Yoga",
            weekdays=[],
            estimated_minutes=90,
        )