from datetime import date

from app.models.adaptive_profile import AdaptiveProfile
from app.models.schedule import PlanningRequest
from app.models.task import Task
from app.services.planner_service import PlannerService


def test_planner_adjusts_task_duration_using_adaptive_profile():
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

    profile = AdaptiveProfile(
        generated_from_executions=5,
        work_duration_multiplier=1.2,
        confidence=0.25,
    )

    plan = planner.create_plan(
        request=request,
        adaptive_profile=profile,
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