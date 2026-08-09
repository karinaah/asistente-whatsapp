from app.models.assistant_chat import (
    AssistantChatRequest,
)
from app.services.assistant_chat_service import (
    AssistantChatService,
)

def test_chat_planning():
    service = AssistantChatService()

    response = service.chat(
        db=None,
        request=AssistantChatRequest(
            message="Planifica mi día",
        ),
    )

    assert "planificar" in response.answer.lower()


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


def test_chat_explanation():
    service = AssistantChatService()

    response = service.chat(
        db=None,
        request=AssistantChatRequest(
            message="¿Por qué?",
        ),
    )

    assert "explic" in response.answer.lower()


def test_chat_unknown():
    service = AssistantChatService()

    response = service.chat(
        db=None,
        request=AssistantChatRequest(
            message="Hola",
        ),
    )

    assert "no entend" in response.answer.lower()

