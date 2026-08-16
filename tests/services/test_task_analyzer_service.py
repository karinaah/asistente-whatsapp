from datetime import date

from app.models.task import (
    ActivityType,
    Task,
    TaskContext,
    TaskWorkspace,
)
from app.services.task_analyzer_service import TaskAnalyzerService
from app.services.temporal_parser import TemporalParser


def test_infers_exercise_activity_type():
    service = TaskAnalyzerService(
        temporal_parser=TemporalParser(),
    )

    task = Task(
        title="Ir al gimnasio",
        estimated_minutes=60,
    )

    analyzed = service.analyze(
        tasks=[task],
        reference_date=date.today(),
    )

    assert analyzed[0].activity_type == ActivityType.exercise


def test_infers_deep_work_activity_type():
    service = TaskAnalyzerService(
        temporal_parser=TemporalParser(),
    )

    task = Task(
        title="Preparar informe cliente",
        estimated_minutes=60,
    )

    analyzed = service.analyze(
        tasks=[task],
        reference_date=date.today(),
    )

    assert analyzed[0].activity_type == ActivityType.deep_work


def test_infers_work_workspace():
    service = TaskAnalyzerService(
        temporal_parser=TemporalParser(),
    )

    task = Task(
        title="Preparar informe cliente",
        estimated_minutes=60,
    )

    analyzed = service.analyze(
        tasks=[task],
        reference_date=date.today(),
    )

    assert analyzed[0].workspace == TaskWorkspace.work


def test_infers_personal_workspace():
    service = TaskAnalyzerService(
        temporal_parser=TemporalParser(),
    )

    task = Task(
        title="Ir al gimnasio",
        estimated_minutes=60,
    )

    analyzed = service.analyze(
        tasks=[task],
        reference_date=date.today(),
    )

    assert analyzed[0].workspace == TaskWorkspace.personal    

def test_work_workspace_sets_work_context():
    service = TaskAnalyzerService(
        temporal_parser=TemporalParser(),
    )

    task = Task(
        title="Preparar informe cliente",
        estimated_minutes=60,
    )

    analyzed = service.analyze(
        tasks=[task],
        reference_date=date.today(),
    )

    assert analyzed[0].workspace == TaskWorkspace.work
    assert analyzed[0].context == TaskContext.work


def test_personal_workspace_sets_personal_context():
    service = TaskAnalyzerService(
        temporal_parser=TemporalParser(),
    )

    task = Task(
        title="Ir al gimnasio",
        estimated_minutes=60,
    )

    analyzed = service.analyze(
        tasks=[task],
        reference_date=date.today(),
    )

    assert analyzed[0].workspace == TaskWorkspace.personal
    assert analyzed[0].context == TaskContext.personal    