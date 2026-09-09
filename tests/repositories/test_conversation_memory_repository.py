from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.conversation_context import ConversationContext
from app.models.conversation_context_db import ConversationContextDB
from app.models.user_db import UserDB
from app.repositories.conversation_memory_repository import (
    ConversationMemoryRepository,
)
from app.models.assistant_intent import AssistantIntent

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


def test_get_returns_empty_context_when_none_exists():
    db = create_test_db()

    try:
        repository = ConversationMemoryRepository()

        context = repository.get(db)

        assert context == ConversationContext()

    finally:
        db.close()


def test_save_persists_pending_followup_state():
    db = create_test_db()

    try:
        repository = ConversationMemoryRepository()

        context = ConversationContext(
            awaiting_remaining_minutes=True,
            pending_active_task_id=42,
        )

        repository.save(db, context)

        stored_context = repository.get(db)

        assert stored_context.awaiting_remaining_minutes is True
        assert stored_context.pending_active_task_id == 42

    finally:
        db.close()


def test_clear_removes_persisted_context():
    db = create_test_db()

    try:
        repository = ConversationMemoryRepository()

        context = ConversationContext(
            awaiting_remaining_minutes=True,
            pending_active_task_id=42,
        )

        repository.save(db, context)
        repository.clear(db)

        stored_context = repository.get(db)

        assert stored_context == ConversationContext()

    finally:
        db.close()

def test_sessions_keep_independent_contexts():
    db = create_test_db()

    try:
        repository = ConversationMemoryRepository()

        work_context = ConversationContext(
            last_intent=AssistantIntent.planning,
        )

        personal_context = ConversationContext(
            last_intent=AssistantIntent.recommendation,
        )

        repository.save(
            db,
            work_context,
            session_id="work",
        )

        repository.save(
            db,
            personal_context,
            session_id="personal",
        )

        stored_work = repository.get(
            db,
            session_id="work",
        )

        stored_personal = repository.get(
            db,
            session_id="personal",
        )

        assert (
            stored_work.last_intent
            == AssistantIntent.planning
        )

        assert (
            stored_personal.last_intent
            == AssistantIntent.recommendation
        )

    finally:
        db.close()        


def test_conversation_context_can_be_associated_with_user():
    db = create_test_db()

    try:
        user = UserDB(
            name="Cinthia",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        context_db = ConversationContextDB(
            session_id="user-session",
            user_id=user.id,
        )

        db.add(context_db)
        db.commit()
        db.refresh(context_db)

        assert context_db.user_id == user.id

    finally:
        db.close()        

def test_save_associates_context_with_user():
    db = create_test_db()

    try:
        user = UserDB(
            name="Cinthia",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        repository = ConversationMemoryRepository()

        context = ConversationContext(
            last_intent=AssistantIntent.planning,
        )

        stored_context = repository.save(
            db,
            context,
            session_id="work-user-session",
            user_id=user.id,
        )

        assert stored_context.user_id == user.id

    finally:
        db.close()        

def test_save_without_user_id_preserves_existing_user():
    db = create_test_db()

    try:
        user = UserDB(
            name="Cinthia",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        repository = ConversationMemoryRepository()

        context = ConversationContext(
            last_intent=AssistantIntent.planning,
        )

        repository.save(
            db,
            context,
            session_id="preserve-user-session",
            user_id=user.id,
        )

        updated_context = ConversationContext(
            last_intent=AssistantIntent.recommendation,
        )

        stored_context = repository.save(
            db,
            updated_context,
            session_id="preserve-user-session",
        )

        assert stored_context.user_id == user.id

    finally:
        db.close()        