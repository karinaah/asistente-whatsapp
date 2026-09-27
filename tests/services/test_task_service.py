from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.routine_db import RoutineDB
from app.models.task import Task
from app.models.task_db import TaskDB
from app.models.user_db import UserDB
from app.services.task_service import TaskService


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


def test_get_plannable_filters_tasks_by_user():
    db = create_test_db()

    try:
        user_1 = UserDB(name="User 1")
        user_2 = UserDB(name="User 2")

        db.add_all([user_1, user_2])
        db.commit()
        db.refresh(user_1)
        db.refresh(user_2)

        service = TaskService()

        service.create(
            db,
            Task(
                user_id=user_1.id,
                title="Tarea usuario 1",
                estimated_minutes=30,
            ),
        )

        service.create(
            db,
            Task(
                user_id=user_2.id,
                title="Tarea usuario 2",
                estimated_minutes=30,
            ),
        )

        service.create(
            db,
            Task(
                title="Tarea legacy",
                estimated_minutes=30,
            ),
        )

        tasks = service.get_plannable(
            db,
            user_id=user_1.id,
        )

        titles = {
            task.title
            for task in tasks
        }

        assert "Tarea usuario 1" in titles
        assert "Tarea legacy" in titles
        assert "Tarea usuario 2" not in titles

    finally:
        db.close()