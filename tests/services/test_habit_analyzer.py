from datetime import datetime

from app.models.task import TaskCategory, TaskContext
from app.models.task_execution import TaskExecution
from app.services.analyzers.habit_analyzer import (
    HabitAnalyzer,
)


def test_habit_analyzer_returns_basic_execution_metrics():
    analyzer = HabitAnalyzer()

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
        ),
        TaskExecution(
            task_id=2,
            estimated_minutes=30,
            actual_minutes=45,
            started_at=datetime.fromisoformat(
                "2026-08-08T11:00:00"
            ),
            finished_at=datetime.fromisoformat(
                "2026-08-08T11:45:00"
            ),
            category=TaskCategory.study,
            context=TaskContext.personal,
        ),
    ]

    result = analyzer.analyze(executions)

    assert result.executions == 2
    assert result.average_actual_minutes == 60.0    