from app.models.assistant_chat import (
    AssistantChatRequest,
)
from app.services.assistant_chat_service import (
    AssistantChatService,
)
from app.models.assistant_intent import AssistantIntent

from datetime import datetime

from app.models.schedule import (
    PlanningResponse,
    ScheduledTask,
)
from app.models.task import (
    ActivityType,
    Task,
    TaskWorkspace,
)
import re


def test_chat_planning(monkeypatch):
    service = AssistantChatService()

    monkeypatch.setattr(
        service.planning_workflow_service.task_service,
        "get_plannable",
        lambda db: [],
    )

    monkeypatch.setattr(
        service.planning_workflow_service.adaptive_profile_service,
        "get",
        lambda db: None,
    )

    response = service.chat(
        db=None,
        request=AssistantChatRequest(
            message="Planifica mi día",
        ),
    )

    assert (
        "no encontré tareas"
        in response.answer.lower()
    )


def test_chat_recommendation(monkeypatch):
    service = AssistantChatService()

    class FakeRecommendation:
        summary = "Te recomiendo hacer la tarea prioritaria."
        task = type(
            "FakeTask",
            (),
            {"title": "Tarea prioritaria"},
        )()

    monkeypatch.setattr(
        service.recommendation_workflow_service,
        "recommend",
        lambda db, request: FakeRecommendation(),
    )

    response = service.chat(
        db=None,
        request=AssistantChatRequest(
            message="¿Qué hago ahora?",
        ),
    )

    assert "recomiendo" in response.answer.lower()


def test_chat_learning(monkeypatch):
    service = AssistantChatService()

    fake_insights = []

    monkeypatch.setattr(
        service.task_execution_service,
        "get_all_for_learning",
        lambda db: [],
    )

    monkeypatch.setattr(
        service.learning_service,
        "get_estimation_insights",
        lambda executions: fake_insights,
    )

    response = service.chat(
        db=None,
        request=AssistantChatRequest(
            message="¿Qué has aprendido?",
        ),
    )

    assert (
        "todavía no tengo suficiente"
        in response.answer.lower()
    )


def test_chat_explanation(monkeypatch):
    service = AssistantChatService()

    fake_history = type(
        "FakeHistory",
        (),
        {
            "summary": (
                "Te recomendé hacer Preparar presentación."
            ),
            "task_title": "Preparar presentación",
            "reasons_json": (
                '[{"message": "Tiene prioridad alta."}]'
            ),
        },
    )()

    monkeypatch.setattr(
        service.recommendation_history_service,
        "get_latest",
        lambda db: fake_history,
    )

    response = service.chat(
        db=None,
        request=AssistantChatRequest(
            message="¿Por qué?",
        ),
    )

    assert (
        response.answer
        == "Te recomendé hacer Preparar presentación."
    )


def test_chat_unknown():
    service = AssistantChatService()

    response = service.chat(
        db=None,
        request=AssistantChatRequest(
            message="Hola",
        ),
    )

    assert "no entend" in response.answer.lower()

def test_chat_stores_last_intent():
    service = AssistantChatService()

    service.chat(
        db=None,
        request=AssistantChatRequest(
            message="Hola",
        ),
    )

    context = (
        service.conversation_memory_service
        .get_context()
    )

    assert (
        context.last_intent
        == AssistantIntent.unknown
    )


def test_chat_stores_last_recommendation(
    monkeypatch,
):
    service = AssistantChatService()

    class FakeRecommendation:
        summary = (
            "Te recomiendo hacer "
            "Preparar presentación."
        )

        task = type(
            "FakeTask",
            (),
            {
                "title": (
                    "Preparar presentación"
                )
            },
        )()

    fake_recommendation = FakeRecommendation()

    monkeypatch.setattr(
        service.recommendation_workflow_service,
        "recommend",
        lambda db, request: fake_recommendation,
    )

    service.chat(
        db=None,
        request=AssistantChatRequest(
            message="¿Qué hago ahora?",
        ),
    )

    context = (
        service.conversation_memory_service
        .get_context()
    )

    assert (
        context.last_recommendation
        is fake_recommendation
    )    


def test_chat_uses_memory_for_follow_up_explanation(
    monkeypatch,
):
    service = AssistantChatService()

    class FakeRecommendation:
        summary = (
            "Te recomiendo hacer Preparar presentación."
        )

        task = type(
            "FakeTask",
            (),
            {
                "title": "Preparar presentación"
            },
        )()

    fake_recommendation = FakeRecommendation()

    monkeypatch.setattr(
        service.recommendation_workflow_service,
        "recommend",
        lambda db, request: fake_recommendation,
    )

    # Primera interacción:
    # el Assistant genera una recomendación
    first_response = service.chat(
        db=None,
        request=AssistantChatRequest(
            message="¿Qué hago ahora?",
        ),
    )

    # Si la memoria funciona bien,
    # esta consulta NO debería necesitar historial.
    monkeypatch.setattr(
        service.recommendation_history_service,
        "get_latest",
        lambda db: (_ for _ in ()).throw(
            AssertionError(
                "No debería consultar el historial."
            )
        ),
    )

    second_response = service.chat(
        db=None,
        request=AssistantChatRequest(
            message="¿Por qué?",
        ),
    )

    assert (
        "preparar presentación"
        in first_response.answer.lower()
    )

    assert (
        "preparar presentación"
        in second_response.answer.lower()
    )    

def test_chat_stores_last_plan(monkeypatch):
    service = AssistantChatService()

    fake_plan = type(
        "FakePlan",
        (),
        {
            "scheduled_tasks": [],
            "unscheduled_tasks": [],
            "timeline": [],
        },
    )()

    fake_result = type(
        "FakeResult",
        (),
        {
            "response": fake_plan,
            "decisions": [],
        },
    )()

    monkeypatch.setattr(
        service.planning_workflow_service,
        "create_plan_with_decisions_from_db",
        lambda db, request: fake_result,
    )

    service.chat(
        db=None,
        request=AssistantChatRequest(
            message="Planifica mi día",
        ),
    )

    context = (
        service.conversation_memory_service
        .get_context()
    )

    assert context.last_plan is fake_plan    


def test_chat_follow_up_returns_next_task(
    monkeypatch,
):
    service = AssistantChatService()

    first_task = Task(
        id=1,
        title="Preparar presentación",
        estimated_minutes=60,
        category="trabajo",
        context="trabajo",
    )

    second_task = Task(
        id=2,
        title="Responder correos",
        estimated_minutes=30,
        category="trabajo",
        context="trabajo",
    )

    first_scheduled = ScheduledTask(
        task=first_task,
        start_time=datetime.fromisoformat(
            "2026-08-10T09:00:00"
        ),
        end_time=datetime.fromisoformat(
            "2026-08-10T10:00:00"
        ),
    )

    second_scheduled = ScheduledTask(
        task=second_task,
        start_time=datetime.fromisoformat(
            "2026-08-10T10:00:00"
        ),
        end_time=datetime.fromisoformat(
            "2026-08-10T10:30:00"
        ),
    )

    fake_plan = PlanningResponse(
        scheduled_tasks=[
            first_scheduled,
            second_scheduled,
        ],
        unscheduled_tasks=[],
        timeline=[],
    )

    fake_recommendation = type(
        "FakeRecommendation",
        (),
        {
            "task": first_task,
            "summary": (
                "Te recomiendo hacer "
                "Preparar presentación."
            ),
        },
    )()

    service.conversation_memory_service.set_last_plan(
        fake_plan
    )

    service.conversation_memory_service.set_last_recommendation(
        fake_recommendation
    )

    response = service.chat(
        db=None,
        request=AssistantChatRequest(
            message="¿Y después?",
        ),
    )

    assert (
        "responder correos"
        in response.answer.lower()
    )

    assert "10:00" in response.answer    

def test_chat_creates_task_from_natural_language(
    monkeypatch,
):
    service = AssistantChatService()

    created_task = Task(
        title="Preparar informe para el cliente mañana",
        estimated_minutes=60,
        workspace=TaskWorkspace.work,
        activity_type=ActivityType.deep_work,
    )

    monkeypatch.setattr(
        service.task_creation_workflow_service,
        "create_from_text",
        lambda db, text, reference_date: [
            created_task
        ],
    )

    response = service.chat(
        db=None,
        request=AssistantChatRequest(
            message=(
                "Preparar informe para "
                "el cliente mañana"
            ),
        ),
    )

    assert "creé la tarea" in response.answer.lower()
    assert "workspace: trabajo" in response.answer.lower()
    assert "deep_work" in response.answer.lower()    

def test_chat_creates_personal_exercise_task(
    monkeypatch,
):
    service = AssistantChatService()

    created_task = Task(
        title="Ir al gimnasio mañana",
        estimated_minutes=60,
        workspace=TaskWorkspace.personal,
        activity_type=ActivityType.exercise,
    )

    monkeypatch.setattr(
        service.task_creation_workflow_service,
        "create_from_text",
        lambda db, text, reference_date: [
            created_task
        ],
    )

    response = service.chat(
        db=None,
        request=AssistantChatRequest(
            message="Ir al gimnasio mañana",
        ),
    )

    assert "creé la tarea" in response.answer.lower()
    assert "workspace: personal" in response.answer.lower()
    assert "exercise" in response.answer.lower()    


def test_chat_replanning(monkeypatch):
    service = AssistantChatService()

    task = Task(
        title="Tarea pendiente",
        estimated_minutes=60,
    )

    fake_plan = PlanningResponse(
        scheduled_tasks=[
            ScheduledTask(
                task=task,
                start_time=datetime.fromisoformat(
                    "2026-08-22T15:00:00"
                ),
                end_time=datetime.fromisoformat(
                    "2026-08-22T16:00:00"
                ),
            )
        ],
        unscheduled_tasks=[],
        timeline=[],
    )

    monkeypatch.setattr(
        service.replanning_service,
        "replan",
        lambda db, request: fake_plan,
    )

    response = service.chat(
        db=None,
        request=AssistantChatRequest(
            message="Reorganiza lo que me queda del día",
        ),
    )

    assert "reorganicé" in response.answer.lower()
    assert "tarea pendiente" in response.answer.lower()    

def test_find_active_scheduled_task():
    service = AssistantChatService()

    task_a = Task(
        title="Tarea A",
        estimated_minutes=60,
    )

    task_b = Task(
        title="Tarea B",
        estimated_minutes=60,
    )

    plan = PlanningResponse(
        scheduled_tasks=[
            ScheduledTask(
                task=task_a,
                start_time=datetime.fromisoformat(
                    "2026-08-22T10:00:00"
                ),
                end_time=datetime.fromisoformat(
                    "2026-08-22T11:00:00"
                ),
            ),
            ScheduledTask(
                task=task_b,
                start_time=datetime.fromisoformat(
                    "2026-08-22T11:00:00"
                ),
                end_time=datetime.fromisoformat(
                    "2026-08-22T12:00:00"
                ),
            ),
        ],
        unscheduled_tasks=[],
        timeline=[],
    )

    active_task = service._find_active_scheduled_task(
        plan=plan,
        now=datetime.fromisoformat(
            "2026-08-22T11:20:00"
        ),
    )

    assert active_task is not None
    assert active_task.task.title == "Tarea B"    


def test_extract_remaining_minutes():
    service = AssistantChatService()

    assert (
        service._extract_remaining_minutes(
            "Me faltan 30 minutos"
        )
        == 30
    )


def test_extract_remaining_minutes_short_form():
    service = AssistantChatService()

    assert (
        service._extract_remaining_minutes(
            "Necesito 45 min más"
        )
        == 45
    )


def test_extract_remaining_minutes_from_hours():
    service = AssistantChatService()

    assert (
        service._extract_remaining_minutes(
            "Me falta 1 hora"
        )
        == 60
    )


def test_extract_remaining_minutes_from_hours_and_minutes():
    service = AssistantChatService()

    assert (
        service._extract_remaining_minutes(
            "Necesito 1 hora 30 minutos"
        )
        == 90
    )    

def test_chat_active_task_delay(monkeypatch):
    service = AssistantChatService()

    active_task = Task(
        id=12,
        title="Preparar informe",
        estimated_minutes=60,
        status="en_progreso",
    )

    plan = PlanningResponse(
        scheduled_tasks=[
            ScheduledTask(
                task=active_task,
                start_time=datetime.fromisoformat(
                    "2026-08-22T11:00:00"
                ),
                end_time=datetime.fromisoformat(
                    "2026-08-22T12:00:00"
                ),
            )
        ],
        unscheduled_tasks=[],
        timeline=[],
    )

    service.conversation_memory_service.set_last_plan(
        plan
    )

    monkeypatch.setattr(
        service,
        "_find_active_scheduled_task",
        lambda plan, now: plan.scheduled_tasks[0],
    )

    fake_replanned = PlanningResponse(
        scheduled_tasks=[
            ScheduledTask(
                task=active_task,
                start_time=datetime.fromisoformat(
                    "2026-08-22T11:30:00"
                ),
                end_time=datetime.fromisoformat(
                    "2026-08-22T12:00:00"
                ),
            )
        ],
        unscheduled_tasks=[],
        timeline=[],
    )

    monkeypatch.setattr(
        service.replanning_service,
        "replan",
        lambda db, request: fake_replanned,
    )

    response = service.chat(
        db=None,
        request=AssistantChatRequest(
            message="Me faltan 30 minutos",
        ),
    )

    assert "30 minutos" in response.answer.lower()
    assert "preparar informe" in response.answer.lower()
    assert "reorganicé" in response.answer.lower()

def test_chat_planning_uses_current_time_for_today(
    monkeypatch,
):
    service = AssistantChatService()

    captured_request = {}

    class FakeResult:
        response = PlanningResponse(
            scheduled_tasks=[],
            unscheduled_tasks=[],
            timeline=[],
        )
        decisions = []

    def fake_create_plan(
        db,
        request,
    ):
        captured_request["request"] = request
        return FakeResult()

    monkeypatch.setattr(
        service.planning_workflow_service,
        "create_plan_with_decisions_from_db",
        fake_create_plan,
    )

    service.chat(
        db=None,
        request=AssistantChatRequest(
            message="Organiza mi día",
        ),
    )

    planning_request = captured_request["request"]

    assert planning_request.planning_start_time is not None        

def test_chat_active_task_delay_asks_for_remaining_time(
    monkeypatch,
):
    service = AssistantChatService()

    active_task = Task(
        id=12,
        title="Preparar informe",
        estimated_minutes=60,
        status="en_progreso",
    )

    plan = PlanningResponse(
        scheduled_tasks=[
            ScheduledTask(
                task=active_task,
                start_time=datetime.fromisoformat(
                    "2026-08-23T14:00:00"
                ),
                end_time=datetime.fromisoformat(
                    "2026-08-23T15:00:00"
                ),
            )
        ],
        unscheduled_tasks=[],
        timeline=[],
    )

    service.conversation_memory_service.set_last_plan(
        plan
    )

    monkeypatch.setattr(
        service,
        "_find_active_scheduled_task",
        lambda plan, now: plan.scheduled_tasks[0],
    )

    response = service.chat(
        db=None,
        request=AssistantChatRequest(
            message="Me atrasé",
        ),
    )

    context = (
        service.conversation_memory_service
        .get_context()
    )

    assert "cuánto tiempo" in response.answer.lower()
    assert "preparar informe" in response.answer.lower()
    assert context.awaiting_remaining_minutes is True
    assert context.pending_active_task_id == 12    

def test_chat_active_task_delay_follow_up(
    monkeypatch,
):
    service = AssistantChatService()

    active_task = Task(
        id=12,
        title="Preparar informe",
        estimated_minutes=60,
        status="en_progreso",
    )

    plan = PlanningResponse(
        scheduled_tasks=[
            ScheduledTask(
                task=active_task,
                start_time=datetime.fromisoformat(
                    "2026-08-23T14:00:00"
                ),
                end_time=datetime.fromisoformat(
                    "2026-08-23T15:00:00"
                ),
            )
        ],
        unscheduled_tasks=[],
        timeline=[],
    )

    service.conversation_memory_service.set_last_plan(
        plan
    )

    monkeypatch.setattr(
        service,
        "_find_active_scheduled_task",
        lambda plan, now: plan.scheduled_tasks[0],
    )

    first_response = service.chat(
        db=None,
        request=AssistantChatRequest(
            message="Me atrasé",
        ),
    )

    assert "cuánto tiempo" in first_response.answer.lower()

    fake_replanned = PlanningResponse(
        scheduled_tasks=[
            ScheduledTask(
                task=active_task,
                start_time=datetime.fromisoformat(
                    "2026-08-23T14:30:00"
                ),
                end_time=datetime.fromisoformat(
                    "2026-08-23T15:10:00"
                ),
            )
        ],
        unscheduled_tasks=[],
        timeline=[],
    )

    monkeypatch.setattr(
        service.replanning_service,
        "replan",
        lambda db, request: fake_replanned,
    )

    second_response = service.chat(
        db=None,
        request=AssistantChatRequest(
            message="40 minutos",
        ),
    )

    context = (
        service.conversation_memory_service
        .get_context()
    )

    assert "40 minutos" in second_response.answer.lower()
    assert "preparar informe" in second_response.answer.lower()
    assert "reorganicé" in second_response.answer.lower()
    assert context.awaiting_remaining_minutes is False
    assert context.pending_active_task_id is None    