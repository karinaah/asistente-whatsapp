from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_assistant_chat_accepts_session_id():
    response = client.post(
        "/assistant/chat",
        json={
            "message": "Hola",
            "session_id": "work",
        },
    )

    assert response.status_code == 200


def test_assistant_chat_sessions_are_isolated():
    work_response = client.post(
        "/assistant/chat",
        json={
            "message": "Planifica mi día",
            "session_id": "work",
        },
    )

    personal_response = client.post(
        "/assistant/chat",
        json={
            "message": "¿Qué hago ahora?",
            "session_id": "personal",
        },
    )

    assert work_response.status_code == 200
    assert personal_response.status_code == 200

    from app.config.database import SessionLocal
    from app.repositories.conversation_memory_repository import (
        ConversationMemoryRepository,
    )
    from app.models.assistant_intent import AssistantIntent

    db = SessionLocal()

    try:
        repository = ConversationMemoryRepository()

        work_context = repository.get(
            db,
            session_id="work",
        )

        personal_context = repository.get(
            db,
            session_id="personal",
        )

        assert (
            work_context.last_intent
            == AssistantIntent.planning
        )

        assert (
            personal_context.last_intent
            == AssistantIntent.recommendation
        )

    finally:
        db.close()    