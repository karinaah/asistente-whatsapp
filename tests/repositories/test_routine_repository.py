from datetime import date, time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.routine import Routine, Weekday
from app.models.routine_db import RoutineDB
from app.models.user_db import UserDB
from app.repositories.routine_repository import (
    RoutineRepository,
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


def test_create_routine():
    db = create_test_db()

    try:
        user = UserDB(
            name="Routine User",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        repository = RoutineRepository()

        routine = Routine(
            user_id=user.id,
            title="Yoga",
            weekdays=[
                Weekday.monday,
                Weekday.wednesday,
                Weekday.friday,
            ],
            preferred_start_time=time(19, 0),
            estimated_minutes=90,
            category="salud",
        )

        stored = repository.create(
            db,
            routine=routine,
        )

        assert stored.id is not None
        assert stored.user_id == user.id
        assert stored.title == "Yoga"
        assert stored.weekdays == [0, 2, 4]
        assert stored.preferred_start_time == time(19, 0)
        assert stored.estimated_minutes == 90
        assert stored.category == "salud"
        assert stored.active is True

    finally:
        db.close()


def test_get_routines_by_user():
    db = create_test_db()

    try:
        user_one = UserDB(name="User One")
        user_two = UserDB(name="User Two")

        db.add_all([
            user_one,
            user_two,
        ])
        db.commit()
        db.refresh(user_one)
        db.refresh(user_two)

        repository = RoutineRepository()

        repository.create(
            db,
            Routine(
                user_id=user_one.id,
                title="Yoga",
                weekdays=[Weekday.monday],
                estimated_minutes=60,
            ),
        )

        repository.create(
            db,
            Routine(
                user_id=user_two.id,
                title="Study",
                weekdays=[Weekday.tuesday],
                estimated_minutes=60,
            ),
        )

        routines = repository.get_by_user_id(
            db,
            user_id=user_one.id,
        )

        assert len(routines) == 1
        assert routines[0].title == "Yoga"
        assert routines[0].user_id == user_one.id

    finally:
        db.close()


def test_get_active_routines_by_user():
    db = create_test_db()

    try:
        user = UserDB(
            name="Routine User",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        repository = RoutineRepository()

        active_routine = repository.create(
            db,
            Routine(
                user_id=user.id,
                title="Yoga",
                weekdays=[Weekday.monday],
                estimated_minutes=60,
            ),
        )

        inactive_routine = repository.create(
            db,
            Routine(
                user_id=user.id,
                title="Old Routine",
                weekdays=[Weekday.friday],
                estimated_minutes=30,
            ),
        )

        inactive_routine.active = False
        db.commit()

        routines = repository.get_active_by_user_id(
            db,
            user_id=user.id,
        )

        assert len(routines) == 1
        assert routines[0].id == active_routine.id
        assert routines[0].title == "Yoga"
        assert routines[0].active is True

    finally:
        db.close()

def test_task_repository_persists_routine_id():
    from app.models.task import Task
    from app.models.task_db import TaskDB
    from app.repositories.task_repository import TaskRepository

    db = create_test_db()

    try:
        user = UserDB(
            name="Routine User",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        routine_repository = RoutineRepository()

        routine = routine_repository.create(
            db,
            Routine(
                user_id=user.id,
                title="Yoga",
                weekdays=[Weekday.monday],
                estimated_minutes=90,
            ),
        )

        task_repository = TaskRepository()

        task = Task(
            user_id=user.id,
            routine_id=routine.id,
            title="Yoga",
            estimated_minutes=90,
            preferred_date=date(2026, 9, 28),
            activity_type="routine",
        )

        stored = task_repository.save(
            db,
            task,
        )
        assert stored.user_id == user.id
        assert stored.routine_id == routine.id

        persisted = (
            db.query(TaskDB)
            .filter(TaskDB.id == stored.id)
            .first()
        )

        assert persisted is not None
        assert persisted.user_id == user.id
        assert persisted.routine_id == routine.id

    finally:
        db.close()        

def test_task_repository_finds_existing_routine_occurrence():
    from app.models.task import Task
    from app.repositories.task_repository import TaskRepository

    db = create_test_db()

    try:
        user = UserDB(
            name="Routine User",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        routine_repository = RoutineRepository()

        routine = routine_repository.create(
            db,
            Routine(
                user_id=user.id,
                title="Yoga",
                weekdays=[Weekday.monday],
                estimated_minutes=90,
            ),
        )

        task_repository = TaskRepository()

        task_repository.save(
            db,
            Task(
                routine_id=routine.id,
                title="Yoga",
                estimated_minutes=90,
                preferred_date=date(2026, 9, 28),
                activity_type="routine",
            ),
        )

        occurrence = (
            task_repository.get_by_routine_and_date(
                db,
                routine_id=routine.id,
                preferred_date=date(2026, 9, 28),
            )
        )

        assert occurrence is not None
        assert occurrence.routine_id == routine.id
        assert occurrence.preferred_date == date(
            2026,
            9,
            28,
        )

        other_date = (
            task_repository.get_by_routine_and_date(
                db,
                routine_id=routine.id,
                preferred_date=date(2026, 9, 29),
            )
        )

        assert other_date is None

    finally:
        db.close()        