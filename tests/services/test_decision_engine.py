from datetime import datetime

from app.models.recommendation import (
    DecisionContext,
    RecommendationReasonCode,
)

from app.models.schedule import PlanningResponse, ScheduledTask
from app.services.decision_engine import DecisionEngine
from tests.factories.task_factory import make_task


from app.models.human_state import (
    EnergyLevel,
    FocusLevel,
    HumanState,
    StressLevel,
)

def test_recommends_active_task():
    engine = DecisionEngine()

    task = make_task(
        title="Preparar informe",
        estimated_minutes=60,
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
        current_time=datetime.fromisoformat(
            "2026-08-01T10:30:00"
        ),
        plan=plan,
    )

    recommendation = engine.recommend(context)

    assert recommendation is not None
    assert recommendation.task.title == "Preparar informe"
    assert recommendation.scheduled_task == scheduled_task
    assert recommendation.score == 100.0

def test_recommends_next_upcoming_task_when_none_is_active():
    engine = DecisionEngine()

    first_task = make_task(
        title="Revisar correos",
        estimated_minutes=30,
    )

    second_task = make_task(
        title="Preparar informe",
        estimated_minutes=60,
    )

    first_scheduled = ScheduledTask(
        task=first_task,
        start_time=datetime.fromisoformat(
            "2026-08-01T11:00:00"
        ),
        end_time=datetime.fromisoformat(
            "2026-08-01T11:30:00"
        ),
    )

    second_scheduled = ScheduledTask(
        task=second_task,
        start_time=datetime.fromisoformat(
            "2026-08-01T12:00:00"
        ),
        end_time=datetime.fromisoformat(
            "2026-08-01T13:00:00"
        ),
    )

    plan = PlanningResponse(
        scheduled_tasks=[
            second_scheduled,
            first_scheduled,
        ],
        unscheduled_tasks=[],
        timeline=[],
    )

    context = DecisionContext(
        current_time=datetime.fromisoformat(
            "2026-08-01T10:30:00"
        ),
        plan=plan,
    )

    recommendation = engine.recommend(context)

    assert recommendation is not None
    assert recommendation.task.title == "Revisar correos"
    assert recommendation.scheduled_task == first_scheduled
    assert recommendation.score == 50.0

def test_returns_none_when_plan_has_no_scheduled_tasks():
    engine = DecisionEngine()

    plan = PlanningResponse(
        scheduled_tasks=[],
        unscheduled_tasks=[],
        timeline=[],
    )

    context = DecisionContext(
        current_time=datetime.fromisoformat(
            "2026-08-01T10:30:00"
        ),
        plan=plan,
    )

    recommendation = engine.recommend(context)

    assert recommendation is None    

def test_returns_none_when_all_scheduled_tasks_are_in_the_past():
    engine = DecisionEngine()

    finished_task = make_task(
        title="Tarea terminada",
        estimated_minutes=60,
    )

    scheduled_task = ScheduledTask(
        task=finished_task,
        start_time=datetime.fromisoformat(
            "2026-08-01T08:00:00"
        ),
        end_time=datetime.fromisoformat(
            "2026-08-01T09:00:00"
        ),
    )

    plan = PlanningResponse(
        scheduled_tasks=[scheduled_task],
        unscheduled_tasks=[],
        timeline=[],
    )

    context = DecisionContext(
        current_time=datetime.fromisoformat(
            "2026-08-01T10:30:00"
        ),
        plan=plan,
    )

    recommendation = engine.recommend(context)

    assert recommendation is None    

def test_active_task_recommendation_explains_that_it_is_scheduled_now():
    engine = DecisionEngine()

    task = make_task(
        title="Preparar informe",
        estimated_minutes=60,
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
        current_time=datetime.fromisoformat(
            "2026-08-01T10:30:00"
        ),
        plan=plan,
    )

    recommendation = engine.recommend(context)

    assert recommendation is not None
    assert len(recommendation.reasons) == 1

    reason = recommendation.reasons[0]

    assert reason.code == RecommendationReasonCode.earliest_available
    assert reason.score == 100.0
    assert "ahora" in reason.message.lower()    

def test_high_priority_active_task_adds_priority_reason():
    engine = DecisionEngine()

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
        current_time=datetime.fromisoformat(
            "2026-08-01T10:30:00"
        ),
        plan=plan,
    )

    recommendation = engine.recommend(context)

    assert recommendation is not None
    assert recommendation.score == 130.0
    assert len(recommendation.reasons) == 2

    reason_codes = {
        reason.code
        for reason in recommendation.reasons
    }

    assert RecommendationReasonCode.earliest_available in reason_codes
    assert RecommendationReasonCode.high_priority in reason_codes

def test_active_task_with_deadline_today_adds_deadline_reason():
    engine = DecisionEngine()

    task = make_task(
        title="Enviar propuesta",
        estimated_minutes=60,
        priority="media",
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
        current_time=datetime.fromisoformat(
            "2026-08-01T10:30:00"
        ),
        plan=plan,
    )

    recommendation = engine.recommend(context)

    assert recommendation is not None

    reason_codes = {
        reason.code
        for reason in recommendation.reasons
    }

    assert RecommendationReasonCode.deadline_soon in reason_codes

def test_active_task_matching_preferred_time_adds_preferred_time_reason():
    engine = DecisionEngine()

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
        current_time=datetime.fromisoformat(
            "2026-08-01T18:30:00"
        ),
        plan=plan,
    )

    recommendation = engine.recommend(context)

    assert recommendation is not None
    assert recommendation.score == 120.0

    reason_codes = {
        reason.code
        for reason in recommendation.reasons
    }

    assert (
        RecommendationReasonCode.preferred_time_match
        in reason_codes
    )

def test_active_task_that_fits_available_time_adds_reason():
    engine = DecisionEngine()

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
            "2026-08-01T10:10:00"
        ),
        plan=plan,
        available_minutes=45,
    )

    recommendation = engine.recommend(context)

    assert recommendation is not None
    assert recommendation.score == 125.0

    reason_codes = {
        reason.code
        for reason in recommendation.reasons
    }

    assert (
        RecommendationReasonCode.fits_available_time
        in reason_codes
    )        

def test_active_task_matching_context_adds_context_reason():
    engine = DecisionEngine()

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

    recommendation = engine.recommend(context)

    assert recommendation is not None
    assert recommendation.score == 135.0

    reason_codes = {
        reason.code
        for reason in recommendation.reasons
    }

    assert RecommendationReasonCode.context_match in reason_codes    

def test_active_task_with_overdue_deadline_adds_overdue_reason():
    engine = DecisionEngine()

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

    recommendation = engine.recommend(context)

    assert recommendation is not None
    assert recommendation.score == 160.0

    reason_codes = {
        reason.code
        for reason in recommendation.reasons
    }

    assert RecommendationReasonCode.overdue in reason_codes    

def test_active_task_matching_energy_adds_energy_reason():
    engine = DecisionEngine()

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

    recommendation = engine.recommend(context)

    assert recommendation is not None
    assert recommendation.score == 140.0

    reason_codes = {
        reason.code
        for reason in recommendation.reasons
    }

    assert RecommendationReasonCode.energy_match in reason_codes    

def test_active_task_matching_focus_adds_focus_reason():
    engine = DecisionEngine()

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

    recommendation = engine.recommend(context)

    assert recommendation is not None
    assert recommendation.score == 135.0

    reason_codes = {
        reason.code
        for reason in recommendation.reasons
    }

    assert RecommendationReasonCode.focus_match in reason_codes    


def test_active_demanding_task_with_high_stress_is_penalized():
    engine = DecisionEngine()

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

    recommendation = engine.recommend(context)

    assert recommendation is not None
    assert recommendation.score == 55.0

    reason_codes = {
        reason.code
        for reason in recommendation.reasons
    }

    assert (
        RecommendationReasonCode.high_stress_penalty
        in reason_codes
    )    

def test_recommendation_includes_natural_summary():
    engine = DecisionEngine()

    task = make_task(
        title="Preparar presentación",
        estimated_minutes=60,
        priority="alta",
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
    )

    recommendation = engine.recommend(context)

    assert recommendation is not None
    assert recommendation.summary is not None
    assert "Preparar presentación" in recommendation.summary
    assert "prioridad alta" in recommendation.summary.lower()    


def test_recommendation_summary_groups_reasons_naturally():
    engine = DecisionEngine()

    task = make_task(
        title="Preparar presentación",
        estimated_minutes=60,
        priority="alta",
        effort="alto",
        focus_demand="alto",
        preferred_time_of_day="mañana",
        context="trabajo",
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
            "2026-08-03T08:30:00"
        ),
        plan=plan,
        context="trabajo",
        available_minutes=90,
        human_state=HumanState(
            energy=EnergyLevel.high,
            focus=FocusLevel.high,
            stress=StressLevel.low,
        ),
    )

    recommendation = engine.recommend(context)

    assert recommendation is not None
    assert recommendation.summary is not None
    assert recommendation.summary.startswith(
        "Te recomiendo hacer Preparar presentación."
    )
    assert "tiene prioridad alta" in recommendation.summary
    assert "coincide con tu contexto actual" in recommendation.summary
    assert "tu nivel de energía es adecuado" in recommendation.summary
    assert "tu nivel de enfoque es adecuado" in recommendation.summary    