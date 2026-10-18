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
import pytest

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
        user = UserDB(name="Usuario privado")
        db.add(user)
        db.commit()
        db.refresh(user)

        repository = ConversationMemoryRepository()

        original_context = ConversationContext(
            last_intent=AssistantIntent.planning,
        )

        repository.save(
            db,
            original_context,
            session_id="preserve-user-session",
            user_id=user.id,
        )

        updated_context = ConversationContext(
            last_intent=AssistantIntent.recommendation,
        )

        with pytest.raises(PermissionError):
            repository.save(
                db,
                updated_context,
                session_id="preserve-user-session",
            )

        stored_context = (
            db.query(ConversationContextDB)
            .filter(
                ConversationContextDB.session_id
                == "preserve-user-session"
            )
            .one()
        )

        assert stored_context.user_id == user.id
        assert stored_context.last_intent == AssistantIntent.planning.value

    finally:
        db.close()


def test_save_cannot_change_existing_session_owner():
    db = create_test_db()

    try:
        user_one = UserDB(name="Usuario uno")
        user_two = UserDB(name="Usuario dos")

        db.add_all([user_one, user_two])
        db.commit()
        db.refresh(user_one)
        db.refresh(user_two)

        repository = ConversationMemoryRepository()

        original_context = ConversationContext(
            last_intent=AssistantIntent.planning,
        )

        repository.save(
            db,
            original_context,
            session_id="private-session",
            user_id=user_one.id,
        )

        new_context = ConversationContext(
            last_intent=AssistantIntent.recommendation,
        )

        with pytest.raises(PermissionError):
            repository.save(
                db,
                new_context,
                session_id="private-session",
                user_id=user_two.id,
            )

        stored_context = db.query(ConversationContextDB).filter(
            ConversationContextDB.session_id == "private-session"
        ).one()

        assert stored_context.user_id == user_one.id
        assert stored_context.last_intent == AssistantIntent.planning.value

    finally:
        db.close()

def test_save_without_user_cannot_modify_private_context():
    db = create_test_db()

    try:
        user = UserDB(name="Usuario privado")
        db.add(user)
        db.commit()
        db.refresh(user)

        repository = ConversationMemoryRepository()

        repository.save(
            db,
            ConversationContext(
                last_intent=AssistantIntent.planning,
            ),
            session_id="private-session",
            user_id=user.id,
        )

        with pytest.raises(PermissionError):
            repository.save(
                db,
                ConversationContext(
                    last_intent=AssistantIntent.recommendation,
                ),
                session_id="private-session",
            )

        stored_context = db.query(ConversationContextDB).filter(
            ConversationContextDB.session_id == "private-session"
        ).one()

        assert stored_context.user_id == user.id
        assert stored_context.last_intent == AssistantIntent.planning.value

    finally:
        db.close()

def test_get_without_user_cannot_read_private_context():
    db = create_test_db()

    try:
        user = UserDB(name="Usuario privado")
        db.add(user)
        db.commit()
        db.refresh(user)

        repository = ConversationMemoryRepository()

        repository.save(
            db,
            ConversationContext(
                last_intent=AssistantIntent.planning,
            ),
            session_id="private-read-session",
            user_id=user.id,
        )

        with pytest.raises(PermissionError):
            repository.get(
                db,
                session_id="private-read-session",
            )

    finally:
        db.close()

def test_clear_without_user_cannot_delete_private_context():
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
        user = UserDB(name="Usuario propietario")
        db.add(user)
        db.commit()
        db.refresh(user)

        repository = ConversationMemoryRepository()

        context = ConversationContext(
            awaiting_remaining_minutes=True,
            pending_active_task_id=10,
        )

        repository.save(
            db,
            context,
            session_id="private-clear-session",
            user_id=user.id,
        )

        # Intento de eliminar sin identificarse como propietario.
        try:
            repository.clear(
                db,
                session_id="private-clear-session",
            )
        except PermissionError:
            pass

        # La memoria del propietario debe seguir existiendo.
        stored_context = repository.get(
            db,
            session_id="private-clear-session",
            user_id=user.id,
        )

        assert stored_context.awaiting_remaining_minutes is True
        assert stored_context.pending_active_task_id == 10

    finally:
        db.close()

def test_clear_allows_session_owner_to_delete_context():
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
        user = UserDB(name="Usuario propietario")
        db.add(user)
        db.commit()
        db.refresh(user)

        repository = ConversationMemoryRepository()

        context = ConversationContext(
            awaiting_remaining_minutes=True,
            pending_active_task_id=10,
        )

        repository.save(
            db,
            context,
            session_id="owner-delete-session",
            user_id=user.id,
        )

        repository.clear(
            db,
            session_id="owner-delete-session",
            user_id=user.id,
        )

        stored_context = (
            db.query(ConversationContextDB)
            .filter(
                ConversationContextDB.session_id
                == "owner-delete-session"
            )
            .first()
        )

        assert stored_context is None

    finally:
        db.close()

def test_clear_cannot_delete_another_users_context():
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
        owner = UserDB(name="Usuario propietario")
        other_user = UserDB(name="Otro usuario")

        db.add_all([owner, other_user])
        db.commit()
        db.refresh(owner)
        db.refresh(other_user)

        repository = ConversationMemoryRepository()

        context = ConversationContext(
            awaiting_remaining_minutes=True,
            pending_active_task_id=10,
        )

        repository.save(
            db,
            context,
            session_id="private-other-user-session",
            user_id=owner.id,
        )

        with pytest.raises(PermissionError):
            repository.clear(
                db,
                session_id="private-other-user-session",
                user_id=other_user.id,
            )

        stored_context = repository.get(
            db,
            session_id="private-other-user-session",
            user_id=owner.id,
        )

        assert stored_context.awaiting_remaining_minutes is True
        assert stored_context.pending_active_task_id == 10

    finally:
        db.close()                                                        