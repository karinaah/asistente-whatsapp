from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base


class ConversationContextDB(Base):
    __tablename__ = "conversation_context"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )


    session_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        default="default",
    )

    last_intent: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    last_recommendation: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    last_plan: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    awaiting_remaining_minutes: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    pending_active_task_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
    )