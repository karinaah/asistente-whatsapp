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