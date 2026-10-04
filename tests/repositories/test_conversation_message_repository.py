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