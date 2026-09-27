from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base


class UserProfileDB(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )

    work_duration_multiplier: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )    

    study_duration_multiplier: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )

    personal_duration_multiplier: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )

    health_duration_multiplier: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )

    other_duration_multiplier: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )

    prefers_short_tasks_when_low_energy: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
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