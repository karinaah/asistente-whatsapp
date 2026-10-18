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
from app.models.schedule import PlanningResponse
from app.models.task import Task
from app.models.recommendation import Recommendation

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

def test_set_last_intent_updates_context_for_its_owner():
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

        service = ConversationMemoryService()

        service.set_last_intent(
            intent=AssistantIntent.planning,
            db=db,
            session_id="owner-session",
            user_id=user.id,
        )

        service.set_last_intent(
            intent=AssistantIntent.recommendation,
            db=db,
            session_id="owner-session",
            user_id=user.id,
        )

        stored_context = service.repository.get(
            db,
            session_id="owner-session",
            user_id=user.id,
        )

        assert stored_context.last_intent == AssistantIntent.recommendation

    finally:
        db.close()

def test_get_context_allows_session_owner():
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

        service = ConversationMemoryService()

        service.set_last_intent(
            intent=AssistantIntent.planning,
            db=db,
            session_id="owner-read-session",
            user_id=user.id,
        )

        context = service.get_context(
            db=db,
            session_id="owner-read-session",
            user_id=user.id,
        )

        assert context.last_intent == AssistantIntent.planning

    finally:
        db.close()        

def test_set_last_plan_updates_context_for_its_owner():
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

        service = ConversationMemoryService()

        plan = PlanningResponse(
            scheduled_tasks=[],
            unscheduled_tasks=[],
            timeline=[],
        )

        service.set_last_plan(
            plan=plan,
            db=db,
            session_id="owner-plan-session",
            user_id=user.id,
        )

        service.set_last_plan(
            plan=plan,
            db=db,
            session_id="owner-plan-session",
            user_id=user.id,
        )

        stored_context = service.repository.get(
            db,
            session_id="owner-plan-session",
            user_id=user.id,
        )

        assert stored_context.last_plan == plan

    finally:
        db.close()

def test_set_last_recommendation_updates_context_for_its_owner():
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

        service = ConversationMemoryService()

        task = Task(
            title="Preparar informe",
            estimated_minutes=60,
        )

        recommendation_one = Recommendation(
            task=task,
            score=0.7,
            summary="Primera recomendación",
        )

        recommendation_two = Recommendation(
            task=task,
            score=0.9,
            summary="Recomendación actualizada",
        )

        service.set_last_recommendation(
            recommendation=recommendation_one,
            db=db,
            session_id="owner-recommendation-session",
            user_id=user.id,
        )

        service.set_last_recommendation(
            recommendation=recommendation_two,
            db=db,
            session_id="owner-recommendation-session",
            user_id=user.id,
        )

        stored_context = service.repository.get(
            db,
            session_id="owner-recommendation-session",
            user_id=user.id,
        )

        assert stored_context.last_recommendation == recommendation_two

    finally:
        db.close()  

def test_set_awaiting_remaining_minutes_updates_context_for_its_owner():
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

        service = ConversationMemoryService()

        service.set_awaiting_remaining_minutes(
            task_id=10,
            db=db,
            session_id="owner-awaiting-session",
            user_id=user.id,
        )

        service.set_awaiting_remaining_minutes(
            task_id=20,
            db=db,
            session_id="owner-awaiting-session",
            user_id=user.id,
        )

        stored_context = service.repository.get(
            db,
            session_id="owner-awaiting-session",
            user_id=user.id,
        )

        assert stored_context.awaiting_remaining_minutes is True
        assert stored_context.pending_active_task_id == 20

    finally:
        db.close()

def test_clear_awaiting_remaining_minutes_for_its_owner():
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

        service = ConversationMemoryService()

        service.set_awaiting_remaining_minutes(
            task_id=10,
            db=db,
            session_id="owner-clear-awaiting-session",
            user_id=user.id,
        )

        service.clear_awaiting_remaining_minutes(
            db=db,
            session_id="owner-clear-awaiting-session",
            user_id=user.id,
        )

        stored_context = service.repository.get(
            db,
            session_id="owner-clear-awaiting-session",
            user_id=user.id,
        )

        assert stored_context.awaiting_remaining_minutes is False
        assert stored_context.pending_active_task_id is None

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

        service = ConversationMemoryService()

        service.set_awaiting_remaining_minutes(
            task_id=10,
            db=db,
            session_id="owner-service-clear-session",
            user_id=user.id,
        )

        service.clear(
            db=db,
            session_id="owner-service-clear-session",
            user_id=user.id,
        )

        stored_context = (
            db.query(ConversationContextDB)
            .filter(
                ConversationContextDB.session_id
                == "owner-service-clear-session"
            )
            .first()
        )

        assert stored_context is None

    finally:
        db.close()                                      