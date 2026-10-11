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
            record.proposed_plan_data = None
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

    def get_proposal(
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

        if record is None or record.proposed_plan_data is None:
            return None

        return PlanningResponse.model_validate(
            record.proposed_plan_data
        )

    def save_proposal(
        self,
        db: Session,
        user_id: int,
        plan_date: date,
        proposal: PlanningResponse,
    ) -> None:
        statement = select(DailyPlanDB).where(
            DailyPlanDB.user_id == user_id,
            DailyPlanDB.plan_date == plan_date,
        )

        record = db.scalar(statement)

        if record is None:
            raise ValueError(
                "No existe una planificación confirmada para este día."
            )

        record.proposed_plan_data = proposal.model_dump(
            mode="json"
        )
        db.commit()

    def accept_proposal(
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

        if record is None or record.proposed_plan_data is None:
            raise ValueError(
                "No existe una propuesta pendiente de aprobación."
            )

        record.plan_data = record.proposed_plan_data
        record.proposed_plan_data = None
        db.commit()

    def reject_proposal(
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

        if record is None or record.proposed_plan_data is None:
            return

        record.proposed_plan_data = None
        db.commit()            