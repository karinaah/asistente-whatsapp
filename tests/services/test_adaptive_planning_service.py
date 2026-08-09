from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.adaptive_profile import AdaptiveProfile
from app.models.adaptive_profile_db import AdaptiveProfileDB
from app.models.schedule import PlanningRequest
from app.models.task import Task
from app.services.adaptive_planning_service import (
    AdaptivePlanningService,
)


def test_adaptive_planning_uses_persisted_profile():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        service = AdaptivePlanningService()

        profile = AdaptiveProfile(
            generated_from_executions=3,
            work_duration_multiplier=1.2,
            confidence=0.15,
        )

        service.adaptive_profile_service.repository.save(
            db=db,
            profile=profile,
        )

        task = Task(
            title="Preparar presentación",
            estimated_minutes=60,
            category="trabajo",
            context="trabajo",
        )

        request = PlanningRequest(
            tasks=[task],
            plan_date=date.fromisoformat("2026-08-10"),
            day_start_hour=8,
            day_end_hour=20,
            break_minutes=0,
            busy_blocks=[],
            context="trabajo",
        )

        plan = service.create_plan(
            db=db,
            request=request,
        )

        assert len(plan.scheduled_tasks) == 1

        scheduled = plan.scheduled_tasks[0]

        duration_minutes = int(
            (
                scheduled.end_time
                - scheduled.start_time
            ).total_seconds()
            / 60
        )

        assert duration_minutes == 72
        assert task.estimated_minutes == 60

    finally:
        db.close()