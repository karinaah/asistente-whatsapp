from datetime import datetime

from app.services.scoring_engine import ScoringEngine
from tests.factories.slot_factory import make_slot
from tests.factories.task_factory import make_task


def test_earliest_slot_wins_when_scores_are_equal():
    engine = ScoringEngine()
    task = make_task(
        estimated_minutes=50,
        preferred_time_of_day=None,
        deadline=None,
    )

    first_slot = make_slot("09:00", "10:00")
    second_slot = make_slot("11:00", "12:00")
    available_slots = [first_slot, second_slot]

    earliest_start = datetime.fromisoformat(
        "2025-07-20T09:00:00"
    )

    first_score = engine.score(
        slot=first_slot,
        task=task,
        earliest_start=earliest_start,
        available_slots=available_slots,
    )

    second_score = engine.score(
        slot=second_slot,
        task=task,
        earliest_start=earliest_start,
        available_slots=available_slots,
    )

    assert first_score > second_score