from datetime import datetime

from app.models.recommendation import DecisionContext
from app.models.schedule import PlanningResponse, ScheduledTask
from app.services.decision_rules.deadline_rule import DeadlineRule
from app.services.decision_rules.preferred_time_rule import (
    PreferredTimeRule,
)
from app.services.decision_rules.priority_rule import PriorityRule
from tests.factories.task_factory import make_task
from app.services.decision_rules.available_time_rule import (
    AvailableTimeRule,
)
from app.services.decision_rules.context_rule import ContextRule
from app.services.decision_rules.overdue_rule import OverdueRule
from app.models.human_state import (
    EnergyLevel,
    HumanState,
    FocusLevel,
)
from app.services.decision_rules.energy_rule import EnergyRule


from app.models.recommendation import RecommendationReasonCode
from app.services.decision_rules.focus_rule import FocusRule

from app.models.human_state import StressLevel
from app.services.decision_rules.stress_rule import StressRule

def test_priority_rule_returns_reason_for_high_priority_task():
    rule = PriorityRule()

    task = make_task(
        title="Preparar propuesta",
        estimated_minutes=60,
        priority="alta",
    )

    scheduled_task = ScheduledTask(
        task=task,
        start_time=datetime.fromisoformat(
            "2026-08-01T10:00:00"
        ),
        end_time=datetime.fromisoformat(
            "2026-08-01T11:00:00"
        ),
    )

    plan = PlanningResponse(
        scheduled_tasks=[scheduled_task],
        unscheduled_tasks=[],
        timeline=[],
    )

    context = DecisionContext(
        current_time=scheduled_task.start_time,
        plan=plan,
    )    

    reasons = rule.evaluate(
    scheduled_task,
    context,)

    assert len(reasons) == 1
    assert reasons[0].code.value == "high_priority"
    assert reasons[0].score == 30.0
    assert "prioridad alta" in reasons[0].message.lower()




def test_deadline_rule_returns_reason_when_task_deadline_is_today():
    rule = DeadlineRule()

    task = make_task(
        title="Enviar propuesta",
        estimated_minutes=60,
        deadline=datetime.fromisoformat(
            "2026-08-01T18:00:00"
        ),
    )

    scheduled_task = ScheduledTask(
        task=task,
        start_time=datetime.fromisoformat(
            "2026-08-01T10:00:00"
        ),
        end_time=datetime.fromisoformat(
            "2026-08-01T11:00:00"
        ),
    )

    plan = PlanningResponse(
        scheduled_tasks=[scheduled_task],
        unscheduled_tasks=[],
        timeline=[],
    )

    context = DecisionContext(
        current_time=scheduled_task.start_time,
        plan=plan,
    )

    reasons = rule.evaluate(
    scheduled_task,
    context,)

    assert len(reasons) == 1
    assert reasons[0].code.value == "deadline_soon"
    assert reasons[0].score == 40.0
    assert "vence hoy" in reasons[0].message.lower()    

def test_preferred_time_rule_returns_reason_when_slot_matches_preference():
    rule = PreferredTimeRule()

    task = make_task(
        title="Entrenamiento",
        estimated_minutes=60,
        preferred_time_of_day="noche",
    )

    scheduled_task = ScheduledTask(
        task=task,
        start_time=datetime.fromisoformat(
            "2026-08-01T18:00:00"
        ),
        end_time=datetime.fromisoformat(
            "2026-08-01T19:00:00"
        ),
    )

    plan = PlanningResponse(
        scheduled_tasks=[scheduled_task],
        unscheduled_tasks=[],
        timeline=[],
    )

    context = DecisionContext(
        current_time=scheduled_task.start_time,
        plan=plan,
    )

    reasons = rule.evaluate(
    scheduled_task,
    context,)

    assert len(reasons) == 1
    assert reasons[0].code.value == "preferred_time_match"
    assert reasons[0].score == 20.0
    assert "horario preferido" in reasons[0].message.lower()    

def test_available_time_rule_returns_reason_when_task_fits():
    rule = AvailableTimeRule()

    task = make_task(
        title="Revisar correos",
        estimated_minutes=30,
    )

    scheduled_task = ScheduledTask(
        task=task,
        start_time=datetime.fromisoformat(
            "2026-08-01T10:00:00"
        ),
        end_time=datetime.fromisoformat(
            "2026-08-01T10:30:00"
        ),
    )

    plan = PlanningResponse(
        scheduled_tasks=[scheduled_task],
        unscheduled_tasks=[],
        timeline=[],
    )

    context = DecisionContext(
        current_time=datetime.fromisoformat(
            "2026-08-01T09:50:00"
        ),
        plan=plan,
        available_minutes=45,
    )

    reasons = rule.evaluate(
        scheduled_task,
        context,
    )

    assert len(reasons) == 1
    assert reasons[0].code.value == "fits_available_time"
    assert reasons[0].score == 25.0
    assert "tiempo" in reasons[0].message.lower()    

def test_context_rule_returns_reason_when_task_matches_active_context():
    rule = ContextRule()

    task = make_task(
        title="Preparar informe",
        estimated_minutes=60,
        context="trabajo",
    )

    scheduled_task = ScheduledTask(
        task=task,
        start_time=datetime.fromisoformat(
            "2026-08-02T10:00:00"
        ),
        end_time=datetime.fromisoformat(
            "2026-08-02T11:00:00"
        ),
    )

    plan = PlanningResponse(
        scheduled_tasks=[scheduled_task],
        unscheduled_tasks=[],
        timeline=[],
    )

    context = DecisionContext(
        current_time=datetime.fromisoformat(
            "2026-08-02T10:15:00"
        ),
        plan=plan,
        context="trabajo",
    )

    reasons = rule.evaluate(
        scheduled_task,
        context,
    )

    assert len(reasons) == 1
    assert reasons[0].code.value == "context_match"
    assert reasons[0].score == 35.0
    assert "contexto" in reasons[0].message.lower()    

def test_overdue_rule_returns_reason_when_task_is_overdue():
    rule = OverdueRule()

    task = make_task(
        title="Enviar informe",
        estimated_minutes=60,
        deadline=datetime.fromisoformat(
            "2026-08-01T18:00:00"
        ),
    )

    scheduled_task = ScheduledTask(
        task=task,
        start_time=datetime.fromisoformat(
            "2026-08-02T10:00:00"
        ),
        end_time=datetime.fromisoformat(
            "2026-08-02T11:00:00"
        ),
    )

    plan = PlanningResponse(
        scheduled_tasks=[scheduled_task],
        unscheduled_tasks=[],
        timeline=[],
    )

    context = DecisionContext(
        current_time=datetime.fromisoformat(
            "2026-08-02T10:15:00"
        ),
        plan=plan,
    )

    reasons = rule.evaluate(
        scheduled_task,
        context,
    )

    assert len(reasons) == 1
    assert reasons[0].code.value == "overdue"
    assert reasons[0].score == 60.0
    assert "vencida" in reasons[0].message.lower()    

def test_energy_rule_returns_reason_when_energy_matches_task_effort():
    rule = EnergyRule()

    task = make_task(
        title="Preparar presentación",
        estimated_minutes=60,
        effort="alto",
    )

    scheduled_task = ScheduledTask(
        task=task,
        start_time=datetime.fromisoformat(
            "2026-08-03T09:00:00"
        ),
        end_time=datetime.fromisoformat(
            "2026-08-03T10:00:00"
        ),
    )

    plan = PlanningResponse(
        scheduled_tasks=[scheduled_task],
        unscheduled_tasks=[],
        timeline=[],
    )

    context = DecisionContext(
        current_time=datetime.fromisoformat(
            "2026-08-03T09:15:00"
        ),
        plan=plan,
        human_state=HumanState(
            energy=EnergyLevel.high,
        ),
    )

    reasons = rule.evaluate(
        scheduled_task,
        context,
    )

    assert len(reasons) == 1
    assert reasons[0].code == RecommendationReasonCode.energy_match
    assert reasons[0].score == 40.0    


def test_energy_rule_returns_reason_when_energy_matches_task_effort():
    rule = EnergyRule()

    task = make_task(
        title="Preparar presentación",
        estimated_minutes=60,
        effort="alto",
    )

    scheduled_task = ScheduledTask(
        task=task,
        start_time=datetime.fromisoformat(
            "2026-08-03T09:00:00"
        ),
        end_time=datetime.fromisoformat(
            "2026-08-03T10:00:00"
        ),
    )

    plan = PlanningResponse(
        scheduled_tasks=[scheduled_task],
        unscheduled_tasks=[],
        timeline=[],
    )

    context = DecisionContext(
        current_time=datetime.fromisoformat(
            "2026-08-03T09:15:00"
        ),
        plan=plan,
        human_state=HumanState(
            energy=EnergyLevel.high,
        ),
    )

    reasons = rule.evaluate(
        scheduled_task,
        context,
    )

    assert len(reasons) == 1
    assert reasons[0].code == RecommendationReasonCode.energy_match
    assert reasons[0].score == 40.0
    assert "energía" in reasons[0].message.lower()    

def test_focus_rule_returns_reason_when_focus_matches_task():
    rule = FocusRule()

    task = make_task(
        title="Arquitectura de software",
        estimated_minutes=90,
        focus_demand="alto",
    )

    scheduled_task = ScheduledTask(
        task=task,
        start_time=datetime.fromisoformat(
            "2026-08-03T09:00:00"
        ),
        end_time=datetime.fromisoformat(
            "2026-08-03T10:30:00"
        ),
    )

    plan = PlanningResponse(
        scheduled_tasks=[scheduled_task],
        unscheduled_tasks=[],
        timeline=[],
    )

    context = DecisionContext(
        current_time=datetime.fromisoformat(
            "2026-08-03T09:15:00"
        ),
        plan=plan,
        human_state=HumanState(
            focus=FocusLevel.high,
        ),
    )

    reasons = rule.evaluate(
        scheduled_task,
        context,
    )

    assert len(reasons) == 1
    assert (
        reasons[0].code
        == RecommendationReasonCode.focus_match
    )
    assert reasons[0].score == 35.0
    assert "enfoque" in reasons[0].message.lower()    

def test_stress_rule_penalizes_demanding_task_when_stress_is_high():
    rule = StressRule()

    task = make_task(
        title="Preparar propuesta compleja",
        estimated_minutes=90,
        effort="alto",
        focus_demand="alto",
    )

    scheduled_task = ScheduledTask(
        task=task,
        start_time=datetime.fromisoformat(
            "2026-08-03T09:00:00"
        ),
        end_time=datetime.fromisoformat(
            "2026-08-03T10:30:00"
        ),
    )

    plan = PlanningResponse(
        scheduled_tasks=[scheduled_task],
        unscheduled_tasks=[],
        timeline=[],
    )

    context = DecisionContext(
        current_time=datetime.fromisoformat(
            "2026-08-03T09:15:00"
        ),
        plan=plan,
        human_state=HumanState(
            stress=StressLevel.high,
        ),
    )

    reasons = rule.evaluate(
        scheduled_task,
        context,
    )

    assert len(reasons) == 1
    assert (
        reasons[0].code
        == RecommendationReasonCode.high_stress_penalty
    )
    assert reasons[0].score == -45.0
    assert "estrés" in reasons[0].message.lower()    