from datetime import datetime

from app.models.task import TaskCategory, TaskContext
from app.models.task_execution import TaskExecution
from app.services.analyzers.estimation_analyzer import (
    EstimationAnalyzer,
)


def test_estimation_analyzer_groups_by_category():
    analyzer = EstimationAnalyzer()

    executions = [
        TaskExecution(
            task_id=1,
            estimated_minutes=60,
            actual_minutes=75,
            started_at=datetime.fromisoformat(
                "2026-08-08T10:00:00"
            ),
            finished_at=datetime.fromisoformat(
                "2026-08-08T11:15:00"
            ),
            category=TaskCategory.work,
            context=TaskContext.work,
        ),
        TaskExecution(
            task_id=2,
            estimated_minutes=30,
            actual_minutes=36,
            started_at=datetime.fromisoformat(
                "2026-08-08T12:00:00"
            ),
            finished_at=datetime.fromisoformat(
                "2026-08-08T12:36:00"
            ),
            category=TaskCategory.work,
            context=TaskContext.work,
        ),
        TaskExecution(
            task_id=3,
            estimated_minutes=45,
            actual_minutes=45,
            started_at=datetime.fromisoformat(
                "2026-08-08T15:00:00"
            ),
            finished_at=datetime.fromisoformat(
                "2026-08-08T15:45:00"
            ),
            category=TaskCategory.health,
            context=TaskContext.personal,
        ),
    ]

    insights = analyzer.analyze(executions)

    assert len(insights) == 2

    work_insight = next(
        insight
        for insight in insights
        if insight.category == "trabajo"
    )

    assert work_insight.executions == 2
    assert work_insight.average_error_percentage == 22.5
    assert work_insight.average_estimated_minutes == 45.0
    assert work_insight.average_actual_minutes == 55.5

def test_estimation_analyzer_returns_empty_list_when_no_executions():
    analyzer = EstimationAnalyzer()

    insights = analyzer.analyze([])

    assert insights == []    