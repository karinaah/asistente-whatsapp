from app.models.assistant_intent import AssistantIntent
from app.models.conversation_context import ConversationContext
from app.services.conversation_memory_service import (
    ConversationMemoryService,
)


def test_context_starts_empty():
    service = ConversationMemoryService()

    context = service.get_context()

    assert isinstance(context, ConversationContext)
    assert context.last_intent is None
    assert context.last_recommendation is None
    assert context.last_plan is None


def test_set_last_intent():
    service = ConversationMemoryService()

    service.set_last_intent(
        AssistantIntent.recommendation
    )

    assert (
        service.get_context().last_intent
        == AssistantIntent.recommendation
    )


def test_clear_context():
    service = ConversationMemoryService()

    service.set_last_intent(
        AssistantIntent.planning
    )

    service.clear()

    context = service.get_context()

    assert context.last_intent is None
    assert context.last_recommendation is None
    assert context.last_plan is None