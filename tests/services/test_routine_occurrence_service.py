from datetime import date, time

from app.models.routine import Routine, Weekday
from app.services.routine_occurrence_service import (
    RoutineOccurrenceService,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.routine_db import RoutineDB
from app.models.task_db import TaskDB
from app.models.user_db import UserDB

def test_routine_occurs_on_configured_weekday():
    service = RoutineOccurrenceService()

    routine = Routine(
        id=10,
        user_id=1,
        title="Yoga",
        weekdays=[
            Weekday.monday,
            Weekday.wednesday,
            Weekday.friday,
        ],
        estimated_minutes=90,
    )

    assert service.occurs_on(
        routine,
        date(2026, 9, 28),
    ) is True


def test_routine_does_not_occur_on_other_weekday():
    service = RoutineOccurrenceService()

    routine = Routine(
        user_id=1,
        title="Yoga",
        weekdays=[
            Weekday.monday,
            Weekday.wednesday,
            Weekday.friday,
        ],
        estimated_minutes=90,
    )

    assert service.occurs_on(
        routine,
        date(2026, 9, 29),
    ) is False


def test_inactive_routine_does_not_occur():
    service = RoutineOccurrenceService()

    routine = Routine(
        user_id=1,
        title="Yoga",
        weekdays=[Weekday.monday],
        estimated_minutes=90,
        active=False,
    )

    assert service.occurs_on(
        routine,
        date(2026, 9, 28),
    ) is False

def test_create_task_from_routine_occurrence():
    service = RoutineOccurrenceService()

    routine = Routine(
        id=10,
        user_id=1,
        title="Yoga",
        weekdays=[Weekday.monday],
        preferred_start_time="19:00",
        estimated_minutes=90,
        category="salud",
    )

    task = service.create_task(
        routine,
        date(2026, 9, 28),
    )

    assert task is not None
    assert task.routine_id == 10
    assert task.title == "Yoga"
    assert task.preferred_date == date(2026, 9, 28)
    assert task.preferred_start_time == time(19, 0)
    assert task.estimated_minutes == 90
    assert task.activity_type.value == "routine"
    assert task.flexibility.value == "fixed"
    assert task.status.value == "pendiente"

def test_create_task_returns_none_when_routine_does_not_occur():
    service = RoutineOccurrenceService()

    routine = Routine(
        user_id=1,
        title="Yoga",
        weekdays=[Weekday.monday],
        estimated_minutes=90,
    )

    task = service.create_task(
        routine,
        date(2026, 9, 29),
    )

    assert task is None


def test_routine_without_time_creates_flexible_task():
    service = RoutineOccurrenceService()

    routine = Routine(
        user_id=1,
        title="Leer",
        weekdays=[Weekday.monday],
        estimated_minutes=30,
    )

    task = service.create_task(
        routine,
        date(2026, 9, 28),
    )

    assert task is not None
    assert task.preferred_start_time is None
    assert task.flexibility.value == "flexible"    

def test_create_and_save_occurrence_does_not_duplicate():
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
        user = UserDB(
            name="Routine User",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        routine_db = RoutineDB(
            user_id=user.id,
            title="Yoga",
            weekdays=[0],
            preferred_start_time=time(19, 0),
            estimated_minutes=90,
            category="salud",
            context="personal",
            workspace="personal",
            activity_type="routine",
            active=True,
        )

        db.add(routine_db)
        db.commit()
        db.refresh(routine_db)

        routine = Routine.model_validate(
            routine_db
        )

        service = RoutineOccurrenceService()

        first = service.create_and_save_occurrence(
            db,
            routine,
            date(2026, 9, 28),
        )

        second = service.create_and_save_occurrence(
            db,
            routine,
            date(2026, 9, 28),
        )

        tasks = (
            db.query(TaskDB)
            .filter(
                TaskDB.routine_id == routine.id,
                TaskDB.preferred_date
                == date(2026, 9, 28),
            )
            .all()
        )

        assert first is not None
        assert second is not None
        assert first.id == second.id
        assert len(tasks) == 1
        assert tasks[0].title == "Yoga"

    finally:
        db.close()    

def test_generate_for_user_creates_only_routines_for_date():
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
        user = UserDB(
            name="Routine User",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        routines = [
            RoutineDB(
                user_id=user.id,
                title="Yoga",
                weekdays=[0, 2, 4],
                preferred_start_time=time(19, 0),
                estimated_minutes=90,
                category="salud",
                context="personal",
                workspace="personal",
                activity_type="routine",
                active=True,
            ),
            RoutineDB(
                user_id=user.id,
                title="Leer",
                weekdays=[0],
                estimated_minutes=30,
                category="personal",
                context="personal",
                workspace="personal",
                activity_type="routine",
                active=True,
            ),
            RoutineDB(
                user_id=user.id,
                title="Gimnasio",
                weekdays=[1, 3],
                estimated_minutes=60,
                category="salud",
                context="personal",
                workspace="personal",
                activity_type="routine",
                active=True,
            ),
        ]

        db.add_all(routines)
        db.commit()

        service = RoutineOccurrenceService()

        generated = service.generate_for_user(
            db,
            user_id=user.id,
            target_date=date(2026, 9, 28),
        )

        assert len(generated) == 2

        titles = {
            task.title
            for task in generated
        }

        assert titles == {
            "Yoga",
            "Leer",
        }

        stored_tasks = (
            db.query(TaskDB)
            .filter(
                TaskDB.preferred_date
                == date(2026, 9, 28)
            )
            .all()
        )

        assert len(stored_tasks) == 2

    finally:
        db.close()        