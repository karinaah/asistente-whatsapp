from datetime import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.routine_db import RoutineDB
from app.models.user_db import UserDB


def test_routine_db_persists_routine():
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

        routine = RoutineDB(
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
        )

        db.add(routine)
        db.commit()
        db.refresh(routine)

        stored_routine = (
            db.query(RoutineDB)
            .filter(
                RoutineDB.id == routine.id
            )
            .first()
        )

        assert stored_routine is not None
        assert stored_routine.user_id == user.id
        assert stored_routine.title == "Yoga"
        assert stored_routine.weekdays == [0, 2, 4]
        assert (
            stored_routine.preferred_start_time
            == time(19, 0)
        )
        assert stored_routine.estimated_minutes == 90
        assert stored_routine.category == "salud"
        assert stored_routine.context == "personal"
        assert stored_routine.workspace == "personal"
        assert stored_routine.activity_type == "routine"
        assert stored_routine.active is True

    finally:
        db.close()