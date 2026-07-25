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

    def test_smaller_leftover_time_gets_better_score():
        engine = ScoringEngine()
        task = make_task(
            estimated_minutes=50,
            preferred_time_of_day=None,
            deadline=None,
        )

        tighter_slot = make_slot("09:00", "10:00")
        larger_slot = make_slot("09:00", "11:00")

        available_slots = [tighter_slot, larger_slot]

        earliest_start = datetime.fromisoformat(
            "2025-07-20T09:00:00"
        )

        tighter_score = engine.score(
            slot=tighter_slot,
            task=task,
            earliest_start=earliest_start,
            available_slots=available_slots,
        )

        larger_score = engine.score(
            slot=larger_slot,
            task=task,
            earliest_start=earliest_start,
            available_slots=available_slots,
        )

        assert tighter_score > larger_score    

    def test_preferred_time_of_day_gets_better_score():
        engine = ScoringEngine()
        task = make_task(
            estimated_minutes=50,
            preferred_time_of_day="morning",
            deadline=None,
        )

        morning_slot = make_slot("09:00", "10:00")
        afternoon_slot = make_slot("15:00", "16:00")

        available_slots = [morning_slot, afternoon_slot]

        earliest_start = datetime.fromisoformat(
            "2025-07-20T09:00:00"
        )

        morning_score = engine.score(
            slot=morning_slot,
            task=task,
            earliest_start=earliest_start,
            available_slots=available_slots,
        )

        afternoon_score = engine.score(
            slot=afternoon_slot,
            task=task,
            earliest_start=earliest_start,
            available_slots=available_slots,
        )

        assert morning_score > afternoon_score        

    def test_earlier_slot_gets_better_score_when_deadline_is_today():
        engine = ScoringEngine()

        task = make_task(
            estimated_minutes=50,
            preferred_time_of_day=None,
            deadline=datetime.fromisoformat("2025-07-20T23:59:00"),
        )

        early_slot = make_slot("09:00", "10:00")
        late_slot = make_slot("17:00", "18:00")

        available_slots = [early_slot, late_slot]

        earliest_start = datetime.fromisoformat(
            "2025-07-20T09:00:00"
        )

        early_score = engine.score(
            slot=early_slot,
            task=task,
            earliest_start=earliest_start,
            available_slots=available_slots,
        )

        late_score = engine.score(
            slot=late_slot,
            task=task,
            earliest_start=earliest_start,
            available_slots=available_slots,
        )

        assert early_score > late_score        

    def test_preferred_start_time_gets_better_score():
        engine = ScoringEngine()

        task = make_task(
            estimated_minutes=50,
            preferred_time_of_day=None,
            preferred_start_time="11:00",
            deadline=None,
        )

        preferred_slot = make_slot("11:00", "12:00")
        other_slot = make_slot("09:00", "10:00")

        available_slots = [other_slot, preferred_slot]

        earliest_start = datetime.fromisoformat(
            "2025-07-20T09:00:00"
        )

        preferred_score = engine.score(
            slot=preferred_slot,
            task=task,
            earliest_start=earliest_start,
            available_slots=available_slots,
        )

        other_score = engine.score(
            slot=other_slot,
            task=task,
            earliest_start=earliest_start,
            available_slots=available_slots,
        )

        assert preferred_score > other_score        