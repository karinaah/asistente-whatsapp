from datetime import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.recurring_availability_db import (
    RecurringAvailabilityDB,
)
from app.models.user_db import UserDB


def test_persists_recurring_availability():
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

    db = TestingSessionLocal()

    try:
        user = UserDB(name="Test User")
        db.add(user)
        db.commit()
        db.refresh(user)

        availability = RecurringAvailabilityDB(
            user_id=user.id,
            weekday=0,
            start_time=time(8, 0),
            end_time=time(18, 0),
            active=True,
        )

        db.add(availability)
        db.commit()
        db.refresh(availability)

        assert availability.id is not None
        assert availability.user_id == user.id
        assert availability.weekday == 0
        assert availability.start_time == time(8, 0)
        assert availability.end_time == time(18, 0)
        assert availability.active is True

    finally:
        db.close()