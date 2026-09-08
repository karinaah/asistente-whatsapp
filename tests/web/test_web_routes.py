from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_web_home_returns_200():
    response = client.get("/web")

    assert response.status_code == 200

def test_web_tasks_returns_200():
    response = client.get("/web/tasks")

    assert response.status_code == 200    

def test_web_chat_returns_200():
    response = client.get("/web/chat")

    assert response.status_code == 200    

def test_web_chat_creates_session_cookie():
    client.cookies.clear()

    response = client.get("/web/chat")

    assert response.status_code == 200
    assert "aura_session_id" in response.cookies

    session_id = response.cookies.get(
        "aura_session_id"
    )

    assert session_id is not None
    assert session_id != ""    

def test_web_chat_reuses_session_cookie():
    client.cookies.clear()

    get_response = client.get("/web/chat")

    session_id = get_response.cookies.get(
        "aura_session_id"
    )

    post_response = client.post(
        "/web/chat",
        data={
            "message": "Hola",
        },
    )

    assert post_response.status_code == 200

    assert (
        client.cookies.get("aura_session_id")
        == session_id
    )    

def test_web_chat_persists_memory_with_cookie_session():
    client.cookies.clear()

    get_response = client.get("/web/chat")

    session_id = get_response.cookies.get(
        "aura_session_id"
    )

    post_response = client.post(
        "/web/chat",
        data={
            "message": "¿Qué hago ahora?",
        },
    )

    assert post_response.status_code == 200

    from app.config.database import SessionLocal
    from app.repositories.conversation_memory_repository import (
        ConversationMemoryRepository,
    )
    from app.models.assistant_intent import AssistantIntent

    db = SessionLocal()

    try:
        repository = ConversationMemoryRepository()

        context = repository.get(
            db,
            session_id=session_id,
        )

        assert (
            context.last_intent
            == AssistantIntent.recommendation
        )

    finally:
        db.close()    