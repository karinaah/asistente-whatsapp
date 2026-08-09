from app.models.assistant_chat import (
    AssistantChatRequest,
)
from app.services.assistant_chat_service import (
    AssistantChatService,
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

