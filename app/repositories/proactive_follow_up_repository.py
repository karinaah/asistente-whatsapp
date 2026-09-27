from datetime import date, datetime, time

from sqlalchemy.orm import Session

from app.models.proactive_follow_up import (
    FollowUpStatus,
    FollowUpType,
    ProactiveFollowUp,
)
from app.models.proactive_follow_up_db import (
    ProactiveFollowUpDB,
)


class ProactiveFollowUpRepository:
    def create(
        self,
        db: Session,
        follow_up: ProactiveFollowUp,
    ) -> ProactiveFollowUpDB:
        db_follow_up = ProactiveFollowUpDB(
            user_id=follow_up.user_id,
            follow_up_type=follow_up.follow_up_type.value,
            title=follow_up.title,
            message=follow_up.message,
            task_id=follow_up.task_id,
            routine_id=follow_up.routine_id,
            status=follow_up.status.value,
            created_at=follow_up.created_at,
            resolved_at=follow_up.resolved_at,
        )

        db.add(db_follow_up)
        db.commit()
        db.refresh(db_follow_up)

        return db_follow_up

    def get_pending_by_user_id(
        self,
        db: Session,
        user_id: int,
    ) -> list[ProactiveFollowUpDB]:
        return (
            db.query(ProactiveFollowUpDB)
            .filter(
                ProactiveFollowUpDB.user_id == user_id,
                ProactiveFollowUpDB.status
                == FollowUpStatus.PENDING.value,
            )
            .order_by(ProactiveFollowUpDB.created_at)
            .all()
        )

    def exists_for_day(
        self,
        db: Session,
        user_id: int,
        follow_up_type: FollowUpType,
        target_date: date,
    ) -> bool:
        day_start = datetime.combine(
            target_date,
            time.min,
        )
        day_end = datetime.combine(
            target_date,
            time.max,
        )

        existing = (
            db.query(ProactiveFollowUpDB)
            .filter(
                ProactiveFollowUpDB.user_id == user_id,
                ProactiveFollowUpDB.follow_up_type
                == follow_up_type.value,
                ProactiveFollowUpDB.created_at
                >= day_start,
                ProactiveFollowUpDB.created_at
                <= day_end,
            )
            .first()
        )

        return existing is not None

    def resolve(
        self,
        db: Session,
        follow_up_id: int,
        status: FollowUpStatus,
    ) -> ProactiveFollowUpDB | None:
        follow_up = (
            db.query(ProactiveFollowUpDB)
            .filter(
                ProactiveFollowUpDB.id
                == follow_up_id,
            )
            .first()
        )

        if follow_up is None:
            return None

        follow_up.status = status.value
        follow_up.resolved_at = datetime.now()

        db.commit()
        db.refresh(follow_up)

        return follow_up    