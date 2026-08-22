from app.models.assistant_intent import (
    AssistantIntent,
)
from app.services.intent_detection_service import (
    IntentDetectionService,
)


def test_detect_planning_intent():
    service = IntentDetectionService()

    assert (
        service.detect(
            "Planifica mi día"
        )
        == AssistantIntent.planning
    )


def test_detect_recommendation_intent():
    service = IntentDetectionService()

    assert (
        service.detect(
            "¿Qué hago ahora?"
        )
        == AssistantIntent.recommendation
    )


def test_detect_learning_intent():
    service = IntentDetectionService()

    assert (
        service.detect(
            "¿Qué has aprendido?"
        )
        == AssistantIntent.learning
    )


def test_detect_explanation_intent():
    service = IntentDetectionService()

    assert (
        service.detect(
            "¿Por qué?"
        )
        == AssistantIntent.explanation
    )


def test_detect_unknown_intent():
    service = IntentDetectionService()

    assert (
        service.detect(
            "Hola"
        )
        == AssistantIntent.unknown
    )

def test_detect_follow_up_intent():
    service = IntentDetectionService()

    assert (
        service.detect(
            "¿Y después?"
        )
        == AssistantIntent.follow_up
    )    

def test_detects_replanning_intent():
    service = IntentDetectionService()

    intent = service.detect(
        "Reorganiza lo que me queda del día"
    )

    assert intent == AssistantIntent.replanning    