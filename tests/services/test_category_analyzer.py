from datetime import datetime

from app.models.task import TaskCategory, TaskContext
from app.models.task_execution import TaskExecution
from app.services.analyzers.category_analyzer import (
    CategoryAnalyzer,
)


def test_category_analyzer_orders_categories_by_error():
    analyzer = CategoryAnalyzer()

    executions = [
        TaskExecution(
            task_id=1,
            estimated_minutes=60,
            actual_minutes=90,
            started_at=datetime.fromisoformat(
                "2026-08-08T09:00:00"
            ),
            finished_at=datetime.fromisoformat(
                "2026-08-08T10:30:00"
            ),
            category=TaskCategory.work,
            context=TaskContext.work,
        ),
        TaskExecution(
            task_id=2,
            estimated_minutes=60,
            actual_minutes=66,
            started_at=datetime.fromisoformat(
                "2026-08-08T11:00:00"
            ),
            finished_at=datetime.fromisoformat(
                "2026-08-08T12:06:00"
            ),
            category=TaskCategory.study,
            context=TaskContext.personal,
        ),
    ]

    insights = analyzer.analyze(executions)

    assert len(insights) == 2
    assert insights[0].category == "trabajo"
    assert insights[0].average_error_percentage == 50.0
    assert insights[1].category == "estudio"
    assert insights[1].average_error_percentage == 10.0