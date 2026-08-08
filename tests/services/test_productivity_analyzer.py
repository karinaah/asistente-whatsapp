from datetime import datetime

from app.models.human_state import (
    EnergyLevel,
    FocusLevel,
    HumanState,
    StressLevel,
)
from app.models.task import TaskCategory, TaskContext
from app.models.task_execution import TaskExecution
from app.services.analyzers.productivity_analyzer import (
    ProductivityAnalyzer,
)


def test_productivity_analyzer_groups_by_human_state():
    analyzer = ProductivityAnalyzer()

    executions = [
        TaskExecution(
            task_id=1,
            estimated_minutes=60,
            actual_minutes=60,
            started_at=datetime.fromisoformat(
                "2026-08-08T09:00:00"
            ),
            finished_at=datetime.fromisoformat(
                "2026-08-08T10:00:00"
            ),
            category=TaskCategory.work,
            context=TaskContext.work,
            human_state=HumanState(
                energy=EnergyLevel.high,
                focus=FocusLevel.high,
                stress=StressLevel.low,
            ),
        ),
        TaskExecution(
            task_id=2,
            estimated_minutes=60,
            actual_minutes=90,
            started_at=datetime.fromisoformat(
                "2026-08-08T11:00:00"
            ),
            finished_at=datetime.fromisoformat(
                "2026-08-08T12:30:00"
            ),
            category=TaskCategory.work,
            context=TaskContext.work,
            human_state=HumanState(
                energy=EnergyLevel.low,
                focus=FocusLevel.low,
                stress=StressLevel.high,
            ),
        ),
    ]

    insights = analyzer.analyze(executions)

    assert insights.high_energy_average_error == 0.0
    assert insights.low_energy_average_error == 50.0    