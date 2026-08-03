from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base


class HumanStateDB(Base):
    __tablename__ = "human_states"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
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