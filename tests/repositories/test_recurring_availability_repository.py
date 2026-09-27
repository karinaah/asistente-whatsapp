from datetime import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.recurring_availability import (
    RecurringAvailability,
)
from app.models.recurring_availability_db import (
    RecurringAvailabilityDB,
)
from app.models.user_db import UserDB
from app.models.routine import Weekday
from app.repositories.recurring_availability_repository import (
    RecurringAvailabilityRepository,
)


def create_test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    return TestingSessionLocal()


def test_repository_creates_and_gets_user_availability():
    db = create_test_db()

    try:
        user = UserDB(name="Test User")
        db.add(user)
        db.commit()
        db.refresh(user)

        repository = RecurringAvailabilityRepository()

        repository.create(
            db,
            RecurringAvailability(
                user_id=user.id,
                weekday=Weekday.monday,
                start_time=time(8, 0),
                end_time=time(18, 0),
            ),
        )

        availabilities = repository.get_by_user_id(
            db,
            user.id,
        )

        assert len(availabilities) == 1

        stored = availabilities[0]

        assert stored.user_id == user.id
        assert stored.weekday == Weekday.monday
        assert stored.start_time == time(8, 0)
        assert stored.end_time == time(18, 0)
        assert stored.active is True

    finally:
        db.close()

def test_repository_isolates_availability_by_user():
    db = create_test_db()

    try:
        user_1 = UserDB(name="User 1")
        user_2 = UserDB(name="User 2")

        db.add_all([user_1, user_2])
        db.commit()
        db.refresh(user_1)
        db.refresh(user_2)

        repository = RecurringAvailabilityRepository()

        repository.create(
            db,
            RecurringAvailability(
                user_id=user_1.id,
                weekday=Weekday.monday,
                start_time=time(8, 0),
                end_time=time(18, 0),
            ),
        )

        repository.create(
            db,
            RecurringAvailability(
                user_id=user_2.id,
                weekday=Weekday.tuesday,
                start_time=time(10, 0),
                end_time=time(20, 0),
            ),
        )

        availabilities = repository.get_by_user_id(
            db,
            user_1.id,
        )

        assert len(availabilities) == 1
        assert availabilities[0].user_id == user_1.id
        assert availabilities[0].weekday == Weekday.monday

    finally:
        db.close()        