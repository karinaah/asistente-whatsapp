from app.models.assistant_intent import AssistantIntent
from app.models.conversation_context import ConversationContext
from app.services.conversation_memory_service import (
    ConversationMemoryService,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.conversation_context_db import ConversationContextDB
from app.repositories.conversation_memory_repository import (
    ConversationMemoryRepository,
)
from app.models.user_db import UserDB

def test_context_starts_empty():
    service = ConversationMemoryService()

    context = service.get_context()

    assert isinstance(context, ConversationContext)
    assert context.last_intent is None
    assert context.last_recommendation is None
    assert context.last_plan is None


def test_set_last_intent():
    service = ConversationMemoryService()

    service.set_last_intent(
        AssistantIntent.recommendation
    )

    assert (
        service.get_context().last_intent
        == AssistantIntent.recommendation
    )


def test_clear_context():
    service = ConversationMemoryService()

    service.set_last_intent(
        AssistantIntent.planning
    )

    service.clear()

    context = service.get_context()

    assert context.last_intent is None
    assert context.last_recommendation is None
    assert context.last_plan is None



def test_context_can_be_persisted_in_database():
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
        service = ConversationMemoryService(
            repository=ConversationMemoryRepository()
        )

        service.set_last_intent(
            AssistantIntent.recommendation,
            db=db,
        )

        # Nueva instancia para comprobar que no depende
        # de la memoria RAM de la instancia anterior.
        new_service = ConversationMemoryService(
            repository=ConversationMemoryRepository()
        )

        context = new_service.get_context(db=db)

        assert (
            context.last_intent
            == AssistantIntent.recommendation
        )

    finally:
        db.close()  

def test_persisted_context_can_be_associated_with_user():
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
            name="Cinthia",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        service = ConversationMemoryService(
            repository=ConversationMemoryRepository()
        )

        service.set_last_intent(
            AssistantIntent.planning,
            db=db,
            session_id="work",
            user_id=user.id,
        )

        context_db = (
            db.query(ConversationContextDB)
            .filter(
                ConversationContextDB.session_id
                == "work"
            )
            .first()
        )

        assert context_db is not None
        assert context_db.user_id == user.id

    finally:
        db.close()          