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