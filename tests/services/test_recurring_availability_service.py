from datetime import date, datetime, time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.recurring_availability import (
    RecurringAvailability,
)
from app.models.recurring_availability_db import (
    RecurringAvailabilityDB,
)
from app.models.routine import Weekday
from app.models.user_db import UserDB
from app.services.recurring_availability_service import (
    RecurringAvailabilityService,
)
from app.models.time_block import BlockType

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


def test_get_active_for_date_returns_matching_weekday():
    db = create_test_db()

    try:
        user = UserDB(name="Test User")
        db.add(user)
        db.commit()
        db.refresh(user)

        service = RecurringAvailabilityService()

        service.create(
            db,
            RecurringAvailability(
                user_id=user.id,
                weekday=Weekday.monday,
                start_time=time(8, 0),
                end_time=time(18, 0),
            ),
        )

        service.create(
            db,
            RecurringAvailability(
                user_id=user.id,
                weekday=Weekday.tuesday,
                start_time=time(10, 0),
                end_time=time(20, 0),
            ),
        )

        availabilities = service.get_active_for_date(
            db,
            user_id=user.id,
            target_date=date(2026, 9, 28),
        )

        assert len(availabilities) == 1
        assert availabilities[0].weekday == Weekday.monday
        assert availabilities[0].start_time == time(8, 0)
        assert availabilities[0].end_time == time(18, 0)

    finally:
        db.close()

def test_resolve_day_hours_uses_recurring_availability():
    db = create_test_db()

    try:
        user = UserDB(name="Test User")
        db.add(user)
        db.commit()
        db.refresh(user)

        service = RecurringAvailabilityService()

        service.create(
            db,
            RecurringAvailability(
                user_id=user.id,
                weekday=Weekday.monday,
                start_time=time(9, 0),
                end_time=time(17, 0),
            ),
        )

        start_hour, end_hour = service.resolve_day_hours(
            db,
            user_id=user.id,
            target_date=date(2026, 9, 28),
            fallback_start_hour=8,
            fallback_end_hour=20,
        )

        assert start_hour == 9
        assert end_hour == 17
    finally:
        db.close()        

def test_get_active_for_date_supports_multiple_intervals():
    db = create_test_db()

    try:
        user = UserDB(name="Test User")
        db.add(user)
        db.commit()
        db.refresh(user)

        service = RecurringAvailabilityService()

        service.create(
            db,
            RecurringAvailability(
                user_id=user.id,
                weekday=Weekday.monday,
                start_time=time(8, 0),
                end_time=time(13, 0),
            ),
        )

        service.create(
            db,
            RecurringAvailability(
                user_id=user.id,
                weekday=Weekday.monday,
                start_time=time(14, 0),
                end_time=time(18, 0),
            ),
        )

        availabilities = service.get_active_for_date(
            db,
            user_id=user.id,
            target_date=date(2026, 9, 28),
        )

        assert len(availabilities) == 2

        assert availabilities[0].start_time == time(8, 0)
        assert availabilities[0].end_time == time(13, 0)

        assert availabilities[1].start_time == time(14, 0)
        assert availabilities[1].end_time == time(18, 0)

    finally:
        db.close() 

def test_build_unavailable_blocks_between_intervals():
    db = create_test_db()

    try:
        user = UserDB(name="Test User")
        db.add(user)
        db.commit()
        db.refresh(user)

        service = RecurringAvailabilityService()

        service.create(
            db,
            RecurringAvailability(
                user_id=user.id,
                weekday=Weekday.monday,
                start_time=time(8, 0),
                end_time=time(13, 0),
            ),
        )

        service.create(
            db,
            RecurringAvailability(
                user_id=user.id,
                weekday=Weekday.monday,
                start_time=time(14, 0),
                end_time=time(18, 0),
            ),
        )

        blocks = service.build_unavailable_blocks(
            db,
            user_id=user.id,
            target_date=date(2026, 9, 28),
        )

        assert len(blocks) == 1

        block = blocks[0]

        assert block.start_time == datetime(
            2026,
            9,
            28,
            13,
            0,
        )

        assert block.end_time == datetime(
            2026,
            9,
            28,
            14,
            0,
        )

        assert block.title == "No disponible"
        assert block.block_type == BlockType.BREAK

    finally:
        db.close()               