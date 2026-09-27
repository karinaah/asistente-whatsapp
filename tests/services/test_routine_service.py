from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.routine import Routine, Weekday
from app.models.routine_db import RoutineDB
from app.models.user_db import UserDB
from app.services.routine_service import RoutineService


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


def test_routine_service_creates_routine():
    db = create_test_db()

    try:
        user = UserDB(
            name="Routine User",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        service = RoutineService()

        stored = service.create(
            db,
            Routine(
                user_id=user.id,
                title="Yoga",
                weekdays=[
                    Weekday.monday,
                    Weekday.wednesday,
                    Weekday.friday,
                ],
                estimated_minutes=90,
                category="salud",
            ),
        )

        assert stored.id is not None
        assert stored.user_id == user.id
        assert stored.title == "Yoga"
        assert stored.weekdays == [0, 2, 4]

    finally:
        db.close()


def test_routine_service_gets_user_routines():
    db = create_test_db()

    try:
        user = UserDB(
            name="Routine User",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        service = RoutineService()

        service.create(
            db,
            Routine(
                user_id=user.id,
                title="Yoga",
                weekdays=[Weekday.monday],
                estimated_minutes=90,
            ),
        )

        routines = service.get_for_user(
            db,
            user_id=user.id,
        )

        assert len(routines) == 1
        assert routines[0].title == "Yoga"

    finally:
        db.close()


def test_routine_service_gets_only_active_routines():
    db = create_test_db()

    try:
        user = UserDB(
            name="Routine User",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        service = RoutineService()

        active = service.create(
            db,
            Routine(
                user_id=user.id,
                title="Yoga",
                weekdays=[Weekday.monday],
                estimated_minutes=90,
            ),
        )

        inactive = service.create(
            db,
            Routine(
                user_id=user.id,
                title="Old Routine",
                weekdays=[Weekday.friday],
                estimated_minutes=30,
            ),
        )

        inactive.active = False
        db.commit()

        routines = service.get_active_for_user(
            db,
            user_id=user.id,
        )

        assert len(routines) == 1
        assert routines[0].id == active.id
        assert routines[0].active is True

    finally:
        db.close()