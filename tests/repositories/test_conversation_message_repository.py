from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.conversation_message_db import ConversationMessageDB
from app.models.user_db import UserDB
from app.repositories.conversation_message_repository import (
    ConversationMessageRepository,
)


def create_test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    return TestingSessionLocal()


def test_get_by_session_isolates_conversation_messages():
    db = create_test_db()

    try:
        user = UserDB(name="Test User")
        db.add(user)
        db.commit()
        db.refresh(user)

        repository = ConversationMessageRepository()

        repository.add(
            db=db,
            session_id="session-one",
            user_id=user.id,
            role="user",
            content="Mensaje de sesión uno",
        )

        repository.add(
            db=db,
            session_id="session-one",
            user_id=user.id,
            role="assistant",
            content="Respuesta de sesión uno",
        )

        repository.add(
            db=db,
            session_id="session-two",
            user_id=user.id,
            role="user",
            content="Mensaje de sesión dos",
        )

        messages = repository.get_by_session(
            db=db,
            session_id="session-one",
            user_id=user.id,
        )

        assert len(messages) == 2

        assert messages[0].role == "user"
        assert messages[0].content == "Mensaje de sesión uno"

        assert messages[1].role == "assistant"
        assert messages[1].content == "Respuesta de sesión uno"

    finally:
        db.close()

def test_get_by_session_without_user_does_not_expose_private_messages():
    db = create_test_db()

    try:
        user = UserDB(name="Usuario privado")
        db.add(user)
        db.commit()
        db.refresh(user)

        repository = ConversationMessageRepository()

        repository.add(
            db=db,
            session_id="private-session",
            user_id=user.id,
            role="user",
            content="Mensaje privado",
        )

        messages = repository.get_by_session(
            db=db,
            session_id="private-session",
        )

        assert messages == []

    finally:
        db.close()

def test_get_by_session_isolates_messages_between_users():
    db = create_test_db()

    try:
        user_one = UserDB(name="Usuario uno")
        user_two = UserDB(name="Usuario dos")

        db.add_all([user_one, user_two])
        db.commit()
        db.refresh(user_one)
        db.refresh(user_two)

        repository = ConversationMessageRepository()

        repository.add(
            db=db,
            session_id="shared-session",
            user_id=user_one.id,
            role="user",
            content="Mensaje privado usuario uno",
        )

        repository.add(
            db=db,
            session_id="shared-session",
            user_id=user_two.id,
            role="user",
            content="Mensaje privado usuario dos",
        )

        messages_one = repository.get_by_session(
            db=db,
            session_id="shared-session",
            user_id=user_one.id,
        )

        messages_two = repository.get_by_session(
            db=db,
            session_id="shared-session",
            user_id=user_two.id,
        )

        assert len(messages_one) == 1
        assert messages_one[0].content == "Mensaje privado usuario uno"

        assert len(messages_two) == 1
        assert messages_two[0].content == "Mensaje privado usuario dos"

    finally:
        db.close()        