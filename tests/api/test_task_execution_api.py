from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app
from app.models.task_execution_db import TaskExecutionDB
from app.models.user_db import UserDB


client = TestClient(app)


def test_create_task_execution_persists_user_id():
    from app.config.database import SessionLocal

    db = SessionLocal()

    try:
        user = UserDB(
            name="Task Execution User",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        started_at = datetime.now()
        finished_at = started_at + timedelta(
            minutes=75
        )

        response = client.post(
            f"/task-executions?user_id={user.id}",
            json={
                "task_id": 1,
                "estimated_minutes": 60,
                "actual_minutes": 75,
                "started_at": started_at.isoformat(),
                "finished_at": finished_at.isoformat(),
                "category": "trabajo",
                "context": "trabajo",
            },
        )

        assert response.status_code == 201

        execution_db = (
            db.query(TaskExecutionDB)
            .filter(
                TaskExecutionDB.user_id
                == user.id
            )
            .order_by(
                TaskExecutionDB.id.desc()
            )
            .first()
        )

        assert execution_db is not None
        assert execution_db.user_id == user.id
        assert execution_db.estimated_minutes == 60
        assert execution_db.actual_minutes == 75

    finally:
        db.close()

def test_create_task_execution_without_user_id():
    started_at = datetime.now()
    finished_at = started_at + timedelta(
        minutes=45
    )

    response = client.post(
        "/task-executions",
        json={
            "task_id": 2,
            "estimated_minutes": 45,
            "actual_minutes": 45,
            "started_at": started_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "category": "trabajo",
            "context": "trabajo",
        },
    )

    assert response.status_code == 201        