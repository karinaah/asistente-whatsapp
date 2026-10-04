from sqlalchemy.orm import Session

from app.models.conversation_message_db import ConversationMessageDB


class ConversationMessageRepository:

    def add(
        self,
        db: Session,
        session_id: str,
        role: str,
        content: str,
        user_id: int | None = None,
    ) -> ConversationMessageDB:
        message = ConversationMessageDB(
            session_id=session_id,
            user_id=user_id,
            role=role,
            content=content,
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        return message

    def get_by_session(
        self,
        db: Session,
        session_id: str,
        user_id: int | None = None,
    ) -> list[ConversationMessageDB]:
        query = (
            db.query(ConversationMessageDB)
            .filter(
                ConversationMessageDB.session_id
                == session_id
            )
        )

        if user_id is not None:
            query = query.filter(
                ConversationMessageDB.user_id
                == user_id
            )

        return (
            query
            .order_by(
                ConversationMessageDB.created_at.asc(),
                ConversationMessageDB.id.asc(),
            )
            .all()
        )