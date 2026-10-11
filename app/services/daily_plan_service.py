from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.daily_plan_db import DailyPlanDB
from app.models.schedule import PlanningResponse


class DailyPlanService:

    def get(
        self,
        db: Session,
        user_id: int,
        plan_date: date,
    ) -> PlanningResponse | None:
        statement = select(DailyPlanDB).where(
            DailyPlanDB.user_id == user_id,
            DailyPlanDB.plan_date == plan_date,
        )

        record = db.scalar(statement)

        if record is None:
            return None

        return PlanningResponse.model_validate(
            record.plan_data
        )

    def save(
        self,
        db: Session,
        user_id: int,
        plan_date: date,
        plan: PlanningResponse,
    ) -> None:
        statement = select(DailyPlanDB).where(
            DailyPlanDB.user_id == user_id,
            DailyPlanDB.plan_date == plan_date,
        )

        record = db.scalar(statement)

        if record is None:
            record = DailyPlanDB(
                user_id=user_id,
                plan_date=plan_date,
                plan_data=plan.model_dump(mode="json"),
            )
            db.add(record)
        else:
            record.plan_data = plan.model_dump(
                mode="json"
            )

        db.commit()

    def invalidate(
        self,
        db: Session,
        user_id: int,
        plan_date: date,
    ) -> None:
        statement = select(DailyPlanDB).where(
            DailyPlanDB.user_id == user_id,
            DailyPlanDB.plan_date == plan_date,
        )

        record = db.scalar(statement)

        if record is not None:
            db.delete(record)
            db.commit()