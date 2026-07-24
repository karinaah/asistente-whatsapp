from datetime import datetime


class ScoringEngine:
    FRAGMENTATION_WEIGHT = 1.0
    PREFERRED_TIME_WEIGHT = 1.0
    DEADLINE_WEIGHT = 1.0
    EARLIEST_START_WEIGHT = 1.0
    SAME_DAY_DEADLINE_EARLY_WEIGHT = 0.6
    PREFERRED_TIME_BONUS = 150.0
    EARLIEST_TIE_BREAKER_DIVISOR = 10_000

    def score(
        self,
        slot,
        task,
        earliest_start,
        available_slots,
    ) -> float:
        score = 0.0

        score += (
            self.FRAGMENTATION_WEIGHT
            * self._score_fragmentation(
                slot=slot,
                task=task,
                available_slots=available_slots,
            )
        )

        score += (
            self.PREFERRED_TIME_WEIGHT
            * self._score_preferred_time_of_day(
                slot=slot,
                task=task,
            )
        )

        score += (
            self.DEADLINE_WEIGHT
            * self._score_deadline(
                slot=slot,
                task=task,
                earliest_start=earliest_start,
            )
        )

        score += (
            self.EARLIEST_START_WEIGHT
            * self._score_earliest_start(
                slot=slot,
                earliest_start=earliest_start,
            )
        )

        return score

    def _score_fragmentation(
        self,
        slot,
        task,
        available_slots,
    ) -> float:
        """
        Normalized fragmentation score.

        Returns:
        - 0.0 for the slot with the smallest unused remainder.
        - -1.0 for the slot with the largest unused remainder.
        - A proportional value between both extremes.
        """

        def remaining_minutes(candidate) -> float:
            slot_duration = (
                candidate.end_time
                - candidate.start_time
            ).total_seconds() / 60

            return (
                slot_duration
                - task.estimated_minutes
            )

        remainders = [
            remaining_minutes(candidate)
            for candidate in available_slots
        ]

        current_remainder = remaining_minutes(slot)
        minimum_remainder = min(remainders)
        maximum_remainder = max(remainders)

        if maximum_remainder == minimum_remainder:
            return 0.0

        normalized = (
            current_remainder
            - minimum_remainder
        ) / (
            maximum_remainder
            - minimum_remainder
        )

        return -normalized

    def _score_preferred_time_of_day(
        self,
        slot,
        task,
    ) -> float:
        preferred_time = task.preferred_time_of_day

        if preferred_time is None:
            return 0.0

        if hasattr(preferred_time, "value"):
            preferred_time = preferred_time.value

        preferred_time = str(preferred_time).strip().lower()

        slot_hour = slot.start_time.hour

        preferred_ranges = {
            "mañana": range(5, 12),
            "tarde": range(12, 18),
            "noche": range(18, 24),
        }

        preferred_hours = preferred_ranges.get(
            preferred_time
        )

        if preferred_hours is None:
            return 0.0

        if slot_hour in preferred_hours:
            return self.PREFERRED_TIME_BONUS

        return 0.0

    def _score_earliest_start(
        self,
        slot,
        earliest_start: datetime,
    ) -> float:
        minutes_after = (
            slot.start_time - earliest_start
        ).total_seconds() / 60

        return (
            -minutes_after
            / self.EARLIEST_TIE_BREAKER_DIVISOR
        )

    def _score_deadline(
        self,
        slot,
        task,
        earliest_start: datetime,
    ) -> float:
        if task.deadline is None:
            return 0.0

        deadline = task.deadline

        if hasattr(deadline, "date"):
            deadline_date = deadline.date()
        else:
            deadline_date = deadline

        if deadline_date != slot.start_time.date():
            return 0.0

        minutes_after_earliest = (
            slot.start_time - earliest_start
        ).total_seconds() / 60

        return (
            -minutes_after_earliest
            * self.SAME_DAY_DEADLINE_EARLY_WEIGHT
        )