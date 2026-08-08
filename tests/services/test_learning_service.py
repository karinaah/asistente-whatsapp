from datetime import datetime

from app.models.human_state import (
    EnergyLevel,
    FocusLevel,
    HumanState,
    StressLevel,
)
from app.models.task import TaskCategory, TaskContext
from app.models.task_execution import TaskExecution
from app.services.learning_service import (
    LearningService,
)


def test_learning_service_generates_all_insights():
    service = LearningService()

    executions = [
        TaskExecution(
            task_id=1,
            estimated_minutes=60,
            actual_minutes=75,
            started_at=datetime.fromisoformat(
                "2026-08-08T09:00:00"
            ),
            finished_at=datetime.fromisoformat(
                "2026-08-08T10:15:00"
            ),
            category=TaskCategory.work,
            context=TaskContext.work,
            human_state=HumanState(
                energy=EnergyLevel.high,
                focus=FocusLevel.high,
                stress=StressLevel.low,
            ),
        )
    ]

    insights = service.generate_insights(
        executions
    )

    assert "estimation" in insights
    assert "categories" in insights
    assert "productivity" in insights
    assert "habits" in insights