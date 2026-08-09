from app.models.explanation import (
    ExplanationType,
)
from app.models.learning_insight import (
    LearningInsight,
)
from app.services.learning_explanation_service import (
    LearningExplanationService,
)


def test_build_learning_explanation():
    service = LearningExplanationService()

    insights = [
        LearningInsight(
            category="trabajo",
            executions=3,
            average_error_percentage=20.0,
            average_estimated_minutes=60.0,
            average_actual_minutes=72.0,
        ),
        LearningInsight(
            category="estudio",
            executions=2,
            average_error_percentage=0.0,
            average_estimated_minutes=45.0,
            average_actual_minutes=45.0,
        ),
    ]

    explanation = service.build(insights)

    assert (
        explanation.type
        == ExplanationType.learning
    )

    assert (
        explanation.title
        == "Lo que he aprendido"
    )

    assert (
        "2 categorías"
        in explanation.summary
    )

    assert len(explanation.details) == 2

    assert (
        "20% más"
        in explanation.details[0]
    )

    assert (
        "estimaciones han sido precisas"
        in explanation.details[1]
    )


def test_build_learning_explanation_without_insights():
    service = LearningExplanationService()

    explanation = service.build([])

    assert (
        explanation.type
        == ExplanationType.learning
    )

    assert explanation.details == []

    assert (
        "Todavía no tengo suficiente"
        in explanation.summary
    )