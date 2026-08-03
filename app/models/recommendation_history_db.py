from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base


class RecommendationHistoryDB(Base):
    __tablename__ = "recommendation_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    task_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    task_title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    reasons_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    energy: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    focus: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    stress: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    available_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )