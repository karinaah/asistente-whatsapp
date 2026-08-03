from datetime import date, datetime, time
from sqlalchemy import Date, DateTime, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base


class TaskDB(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
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

    estimated_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    effort: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="medio",
    )

    focus_demand: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="medio",
    )

    category: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    context: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    deadline: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    preferred_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    preferred_time_of_day: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    preferred_start_time: Mapped[time | None] = mapped_column(
        Time,
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
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