from sqlalchemy.orm import Session

from app.models.conversation_context import (
    ConversationContext,
)
from app.models.assistant_intent import (
    AssistantIntent,
)
from app.models.recommendation import Recommendation
from app.models.schedule import PlanningResponse
from app.repositories.conversation_memory_repository import (
    ConversationMemoryRepository,
)


class ConversationMemoryService:
    def __init__(
        self,
        repository: ConversationMemoryRepository | None = None,
    ) -> None:
        self._context = ConversationContext()
        self.repository = (
            repository
            or ConversationMemoryRepository()
        )

    def get_context(
        self,
        db: Session | None = None,
        session_id: str = "default",
    ) -> ConversationContext:
        if db is not None:
            return self.repository.get(
                db,
                session_id=session_id,
            )

        return self._context

    def clear(
        self,
        db: Session | None = None,
        session_id: str = "default",
    ) -> None:
        if db is not None:
            self.repository.clear(
                db,
                session_id=session_id,
            )
            return

        self._context = ConversationContext()

    def set_last_intent(
        self,
        intent: AssistantIntent,
        db: Session | None = None,
        session_id: str = "default",
        user_id: int | None = None,
    ) -> None:
        if db is not None:
            context = self.repository.get(
                db,
                session_id=session_id,
            )
            context.last_intent = intent

            self.repository.save(
                db,
                context,
                session_id=session_id,
                user_id=user_id,
            )


            return

        self._context.last_intent = intent

    def set_last_recommendation(
        self,
        recommendation: Recommendation,
        db: Session | None = None,
        session_id: str = "default",
        user_id: int | None = None,   
    ) -> None:
        if db is not None:
            context = self.repository.get(
                db,
                session_id=session_id,
            )

            context.last_recommendation = (
                recommendation
            )

            self.repository.save(
                db,
                context,
                session_id=session_id,
                user_id=user_id,
            )
            return

        self._context.last_recommendation = (
            recommendation
        )

    def set_last_plan(
        self,
        plan: PlanningResponse,
        db: Session | None = None,
        session_id: str = "default",
        user_id: int | None = None,
    ) -> None:
        if db is not None:
            context = self.repository.get(
                db,
                session_id=session_id,
            )

            context.last_plan = plan

            self.repository.save(
                db,
                context,
                session_id=session_id,
                user_id=user_id,
            )
            return

        self._context.last_plan = plan

    def set_awaiting_remaining_minutes(
        self,
        task_id: int,
        db: Session | None = None,
        session_id: str = "default",
        user_id: int | None = None,
    ) -> None:
        if db is not None:
            context = self.repository.get(
                db,
                session_id=session_id,
            )

            context.awaiting_remaining_minutes = True
            context.pending_active_task_id = task_id

            self.repository.save(
                db,
                context,
                session_id=session_id,
                user_id=user_id,
            )
            return

        self._context.awaiting_remaining_minutes = True
        self._context.pending_active_task_id = task_id

    def clear_awaiting_remaining_minutes(
        self,
        db: Session | None = None,
        session_id: str = "default",
        user_id: int | None = None,
    ) -> None:
        if db is not None:
            context = self.repository.get(
                db,
                session_id=session_id,
            )

            context.awaiting_remaining_minutes = False
            context.pending_active_task_id = None

            self.repository.save(
                db,
                context,
                session_id=session_id,
                user_id=user_id,
            )
            return

        self._context.awaiting_remaining_minutes = False
        self._context.pending_active_task_id = None