from datetime import datetime

from app.models.execution_analysis import EstimationStatus
from app.models.task import TaskCategory, TaskContext
from app.models.task_execution import TaskExecution
from app.services.execution_analysis_service import (
    ExecutionAnalysisService,
)


def test_analyze_underestimated_task():
    service = ExecutionAnalysisService()

    execution = TaskExecution(
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
    )

    analysis = service.analyze(execution)

    assert analysis.difference_minutes == 15
    assert analysis.error_percentage == 25.0
    assert (
        analysis.estimation_status
        == EstimationStatus.underestimated
    )


def test_analyze_overestimated_task():
    service = ExecutionAnalysisService()

    execution = TaskExecution(
        task_id=1,
        estimated_minutes=60,
        actual_minutes=45,
        started_at=datetime.fromisoformat(
            "2026-08-08T10:00:00"
        ),
        finished_at=datetime.fromisoformat(
            "2026-08-08T10:45:00"
        ),
        category=TaskCategory.work,
        context=TaskContext.work,
    )

    analysis = service.analyze(execution)

    assert analysis.difference_minutes == -15
    assert analysis.error_percentage == 25.0
    assert (
        analysis.estimation_status
        == EstimationStatus.overestimated
    )


def test_analyze_accurate_task():
    service = ExecutionAnalysisService()

    execution = TaskExecution(
        task_id=1,
        estimated_minutes=60,
        actual_minutes=60,
        started_at=datetime.fromisoformat(
            "2026-08-08T10:00:00"
        ),
        finished_at=datetime.fromisoformat(
            "2026-08-08T11:00:00"
        ),
        category=TaskCategory.work,
        context=TaskContext.work,
    )

    analysis = service.analyze(execution)

    assert analysis.difference_minutes == 0
    assert analysis.error_percentage == 0
    assert (
        analysis.estimation_status
        == EstimationStatus.accurate
    )