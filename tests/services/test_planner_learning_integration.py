from datetime import date

from app.models.learning_insight import LearningInsight
from app.models.schedule import PlanningRequest
from app.models.task import Task
from app.services.planner_service import PlannerService


def test_planner_adjusts_task_duration_using_learning_insight():
    planner = PlannerService()

    task = Task(
        title="Preparar presentación",
        estimated_minutes=60,
        category="trabajo",
        context="trabajo",
    )

    request = PlanningRequest(
        tasks=[task],
        plan_date=date.fromisoformat("2026-08-09"),
        day_start_hour=8,
        day_end_hour=20,
        break_minutes=0,
        busy_blocks=[],
        context="trabajo",
    )

    insight = LearningInsight(
        category="trabajo",
        executions=5,
        average_error_percentage=20.0,
        average_estimated_minutes=60.0,
        average_actual_minutes=72.0,
    )

    plan = planner.create_plan(
        request=request,
        learning_insights=[insight],
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

    # La tarea original no debe modificarse.
    assert task.estimated_minutes == 60