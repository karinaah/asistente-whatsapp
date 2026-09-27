from sqlalchemy.orm import Session

from app.models.recurring_availability import (
    RecurringAvailability,
)
from app.models.recurring_availability_db import (
    RecurringAvailabilityDB,
)


class RecurringAvailabilityRepository:
    def create(
        self,
        db: Session,
        availability: RecurringAvailability,
    ) -> RecurringAvailabilityDB:
        db_availability = RecurringAvailabilityDB(
            user_id=availability.user_id,
            weekday=int(availability.weekday),
            start_time=availability.start_time,
            end_time=availability.end_time,
            active=availability.active,
            created_at=availability.created_at,
            updated_at=availability.updated_at,
        )

        db.add(db_availability)
        db.commit()
        db.refresh(db_availability)

        return db_availability

    def get_by_user_id(
        self,
        db: Session,
        user_id: int,
    ) -> list[RecurringAvailabilityDB]:
        return (
            db.query(RecurringAvailabilityDB)
            .filter(
                RecurringAvailabilityDB.user_id
                == user_id
            )
            .order_by(
                RecurringAvailabilityDB.weekday,
                RecurringAvailabilityDB.start_time,
            )
            .all()
        )

    def get_active_by_user_id(
        self,
        db: Session,
        user_id: int,
    ) -> list[RecurringAvailabilityDB]:
        return (
            db.query(RecurringAvailabilityDB)
            .filter(
                RecurringAvailabilityDB.user_id
                == user_id,
                RecurringAvailabilityDB.active.is_(True),
            )
            .order_by(
                RecurringAvailabilityDB.weekday,
                RecurringAvailabilityDB.start_time,
            )
            .all()
        )