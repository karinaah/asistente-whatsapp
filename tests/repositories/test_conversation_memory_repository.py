from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.conversation_context import ConversationContext
from app.models.conversation_context_db import ConversationContextDB
from app.repositories.conversation_memory_repository import (
    ConversationMemoryRepository,
)


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