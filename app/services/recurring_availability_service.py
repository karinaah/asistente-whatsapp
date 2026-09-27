from datetime import date, datetime

from sqlalchemy.orm import Session

from app.models.recurring_availability import (
    RecurringAvailability,
)
from app.models.recurring_availability_db import (
    RecurringAvailabilityDB,
)
from app.models.time_block import (
    BlockType,
    TimeBlock,
)
from app.repositories.recurring_availability_repository import (
    RecurringAvailabilityRepository,
)


class RecurringAvailabilityService:
    def __init__(
        self,
        repository: RecurringAvailabilityRepository | None = None,
    ):
        self.repository = (
            repository
            or RecurringAvailabilityRepository()
        )

    def create(
        self,
        db: Session,
        availability: RecurringAvailability,
    ) -> RecurringAvailabilityDB:
        return self.repository.create(
            db,
            availability,
        )

    def get_for_user(
        self,
        db: Session,
        user_id: int,
    ) -> list[RecurringAvailabilityDB]:
        return self.repository.get_by_user_id(
            db,
            user_id,
        )

    def get_active_for_date(
        self,
        db: Session,
        user_id: int,
        target_date: date,
    ) -> list[RecurringAvailabilityDB]:
        weekday = target_date.weekday()

        return [
            availability
            for availability
            in self.repository.get_active_by_user_id(
                db,
                user_id,
            )
            if availability.weekday == weekday
        ]

    def resolve_day_hours(
        self,
        db: Session,
        user_id: int,
        target_date: date,
        fallback_start_hour: int,
        fallback_end_hour: int,
    ) -> tuple[int, int]:
        availabilities = self.get_active_for_date(
            db,
            user_id=user_id,
            target_date=target_date,
        )

        if not availabilities:
            return (
                fallback_start_hour,
                fallback_end_hour,
            )

        start_hour = min(
            availability.start_time.hour
            for availability in availabilities
        )

        end_hour = max(
            availability.end_time.hour
            for availability in availabilities
        )

        return start_hour, end_hour

    def build_unavailable_blocks(
        self,
        db: Session,
        user_id: int,
        target_date: date,
    ) -> list[TimeBlock]:
        availabilities = self.get_active_for_date(
            db,
            user_id=user_id,
            target_date=target_date,
        )

        if len(availabilities) < 2:
            return []

        availabilities = sorted(
            availabilities,
            key=lambda availability: (
                availability.start_time
            ),
        )

        blocks = []

        for current, next_availability in zip(
            availabilities,
            availabilities[1:],
        ):
            if (
                next_availability.start_time
                <= current.end_time
            ):
                continue

            blocks.append(
                TimeBlock(
                    start_time=datetime.combine(
                        target_date,
                        current.end_time,
                    ),
                    end_time=datetime.combine(
                        target_date,
                        next_availability.start_time,
                    ),
                    title="No disponible",
                    block_type=BlockType.BREAK,
                )
            )

        return blocks