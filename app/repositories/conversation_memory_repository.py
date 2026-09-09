from sqlalchemy.orm import Session

from app.models.assistant_intent import AssistantIntent
from app.models.conversation_context import ConversationContext
from app.models.conversation_context_db import ConversationContextDB
from app.models.recommendation import Recommendation
from app.models.schedule import PlanningResponse


class ConversationMemoryRepository:
    def get(
        self,
        db: Session,
        session_id: str = "default",
    ) -> ConversationContext:
        context_db = (
            db.query(ConversationContextDB)
            .filter(
                ConversationContextDB.session_id
                == session_id
            )
            .first()
        )


        if context_db is None:
            return ConversationContext()

        return ConversationContext(
            last_intent=(
                AssistantIntent(context_db.last_intent)
                if context_db.last_intent
                else None
            ),
            last_recommendation=(
                Recommendation.model_validate(
                    context_db.last_recommendation
                )
                if context_db.last_recommendation
                else None
            ),
            last_plan=(
                PlanningResponse.model_validate(
                    context_db.last_plan
                )
                if context_db.last_plan
                else None
            ),
            awaiting_remaining_minutes=(
                context_db.awaiting_remaining_minutes
            ),
            pending_active_task_id=(
                context_db.pending_active_task_id
            ),
        )


    def save(
        self,
        db: Session,
        context: ConversationContext,
        session_id: str = "default",
        user_id: int | None = None,
    ) -> ConversationContextDB:
        context_db = (
            db.query(ConversationContextDB)
            .filter(
                ConversationContextDB.session_id
                == session_id
            )
            .first()
        )

        if context_db is None:
            context_db = ConversationContextDB(
                session_id=session_id,
                user_id=user_id,
            )
            db.add(context_db)
        else:
            context_db.user_id = user_id


        context_db.last_intent = (
            context.last_intent.value
            if context.last_intent
            else None
        )

        context_db.last_recommendation = (
            context.last_recommendation.model_dump(
                mode="json"
            )
            if context.last_recommendation
            else None
        )

        context_db.last_plan = (
            context.last_plan.model_dump(
                mode="json"
            )
            if context.last_plan
            else None
        )

        context_db.awaiting_remaining_minutes = (
            context.awaiting_remaining_minutes
        )

        context_db.pending_active_task_id = (
            context.pending_active_task_id
        )

        db.commit()
        db.refresh(context_db)

        return context_db

    def clear(
        self,
        db: Session,
        session_id: str = "default",
    ) -> None:
        context_db = (
            db.query(ConversationContextDB)
            .filter(
                ConversationContextDB.session_id
                == session_id
            )
            .first()
        )        

        if context_db is None:
            return

        db.delete(context_db)
        db.commit()
