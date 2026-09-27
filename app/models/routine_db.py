from datetime import datetime, time

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Time,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base


class RoutineDB(Base):
    __tablename__ = "routines"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    weekdays: Mapped[list[int]] = mapped_column(
        JSON,
        nullable=False,
    )

    preferred_start_time: Mapped[time | None] = mapped_column(
        Time,
        nullable=True,
    )

    estimated_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    context: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    workspace: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    activity_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="routine",
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
    )