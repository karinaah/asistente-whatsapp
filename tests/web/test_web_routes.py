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


def test_web_chat_creates_user_cookie():
    client.cookies.clear()

    response = client.get("/web/chat")

    assert response.status_code == 200
    assert "aura_user_id" in response.cookies

    user_id = response.cookies.get(
        "aura_user_id"
    )

    assert user_id is not None
    assert user_id != ""
    assert int(user_id) >= 1

def test_web_chat_reuses_user_cookie():
    client.cookies.clear()

    first_response = client.get("/web/chat")

    user_id = first_response.cookies.get(
        "aura_user_id"
    )

    second_response = client.get("/web/chat")

    assert second_response.status_code == 200

    assert (
        client.cookies.get("aura_user_id")
        == user_id
    )

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

        assert context is not None
        assert (
            context.last_intent
            == AssistantIntent.recommendation
        )

    finally:
        db.close()


def test_web_chat_persists_memory_with_cookie_user():
    client.cookies.clear()

    get_response = client.get("/web/chat")

    session_id = get_response.cookies.get(
        "aura_session_id"
    )
    user_id = get_response.cookies.get(
        "aura_user_id"
    )

    assert session_id is not None
    assert user_id is not None

    post_response = client.post(
        "/web/chat",
        data={
            "message": "Planifica mi día",
        },
    )

    assert post_response.status_code == 200

    from app.config.database import SessionLocal
    from app.models.conversation_context_db import (
        ConversationContextDB,
    )

    db = SessionLocal()

    try:
        context_db = (
            db.query(ConversationContextDB)
            .filter(
                ConversationContextDB.session_id
                == session_id
            )
            .first()
        )

        assert context_db is not None
        assert context_db.user_id == int(user_id)

    finally:
        db.close()  