from datetime import datetime

from app.models.adaptive_profile import AdaptiveProfile
from app.models.human_state import (
    EnergyLevel,
    FocusLevel,
    HumanState,
    StressLevel,
)
from app.models.recommendation import DecisionContext
from app.models.schedule import ScheduledTask
from app.models.task import Task
from app.services.decision_rules.adaptive_energy_rule import (
    AdaptiveEnergyRule,
)
from app.models.schedule import PlanningResponse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.user_db import UserDB
from app.models.user_profile_db import UserProfileDB
from app.repositories.user_profile_repository import (
    UserProfileRepository,
)
from app.services.user_profile_service import (
    UserProfileService,
)

def test_adaptive_energy_rule_penalizes_long_tasks_when_low_energy():
    rule = AdaptiveEnergyRule()

    task = Task(
        title="Preparar presentación",
        estimated_minutes=90,
        category="trabajo",
        context="trabajo",
    )

    scheduled_task = ScheduledTask(
        task=task,
        start_time=datetime.fromisoformat(
            "2026-08-08T10:00:00"
        ),
        end_time=datetime.fromisoformat(
            "2026-08-08T11:30:00"
        ),
    )


    context = DecisionContext(
        current_time=datetime.fromisoformat(
            "2026-08-08T10:15:00"
        ),
        plan=PlanningResponse(
            scheduled_tasks=[scheduled_task],
            unscheduled_tasks=[],
            timeline=[],
        ),
        human_state=HumanState(
            energy=EnergyLevel.low,
            focus=FocusLevel.low,
            stress=StressLevel.low,
        ),
        adaptive_profile=AdaptiveProfile(
            generated_from_executions=10,
            prefers_short_tasks_when_low_energy=True,
        ),
    )


    reasons = rule.evaluate(
        scheduled_task,
        context,
    )

    assert len(reasons) == 1
    assert reasons[0].score < 0

def test_adaptive_energy_rule_uses_persisted_user_preference():
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
        user = UserDB(
            name="Low Energy Rule User",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        profile_service = UserProfileService(
            repository=UserProfileRepository()
        )

        profile_service.create_profile(
            db,
            user_id=user.id,
        )

        profile_service.update_from_adaptive_profile(
            db,
            user_id=user.id,
            adaptive_profile=AdaptiveProfile(
                generated_from_executions=10,
                prefers_short_tasks_when_low_energy=True,
            ),
        )

        persisted_profile = (
            profile_service.build_adaptive_profile(
                db,
                user_id=user.id,
            )
        )

        task = Task(
            title="Preparar presentación",
            estimated_minutes=90,
            category="trabajo",
            context="trabajo",
        )

        scheduled_task = ScheduledTask(
            task=task,
            start_time=datetime.fromisoformat(
                "2026-08-08T10:00:00"
            ),
            end_time=datetime.fromisoformat(
                "2026-08-08T11:30:00"
            ),
        )

        context = DecisionContext(
            current_time=datetime.fromisoformat(
                "2026-08-08T10:15:00"
            ),
            plan=PlanningResponse(
                scheduled_tasks=[scheduled_task],
                unscheduled_tasks=[],
                timeline=[],
            ),
            human_state=HumanState(
                energy=EnergyLevel.low,
                focus=FocusLevel.low,
                stress=StressLevel.low,
            ),
            adaptive_profile=persisted_profile,
        )

        reasons = AdaptiveEnergyRule().evaluate(
            scheduled_task,
            context,
        )

        assert persisted_profile is not None
        assert (
            persisted_profile
            .prefers_short_tasks_when_low_energy
            is True
        )
        assert len(reasons) == 1
        assert reasons[0].score < 0

    finally:
        db.close()    