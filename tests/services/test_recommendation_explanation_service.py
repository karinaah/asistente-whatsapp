from datetime import datetime

from app.models.explanation import (
    ExplanationType,
)
from app.models.recommendation import (
    Recommendation,
    RecommendationReason,
    RecommendationReasonCode,
)
from app.models.schedule import ScheduledTask
from app.models.task import Task
from app.services.recommendation_explanation_service import (
    RecommendationExplanationService,
)


def test_build_recommendation_explanation():
    service = (
        RecommendationExplanationService()
    )

    task = Task(
        title="Preparar presentación",
        estimated_minutes=60,
        category="trabajo",
        context="trabajo",
    )

    scheduled = ScheduledTask(
        task=task,
        start_time=datetime.fromisoformat(
            "2026-08-08T10:00:00"
        ),
        end_time=datetime.fromisoformat(
            "2026-08-08T11:00:00"
        ),
    )

    recommendation = Recommendation(
        task=task,
        scheduled_task=scheduled,
        score=12.5,
        summary=(
            "Es un buen momento para "
            "realizar esta tarea."
        ),


        reasons=[
            RecommendationReason(
                code=(
                    RecommendationReasonCode
                    .high_priority
                ),
                message="Tiene prioridad alta.",
                score=5,
            ),
            RecommendationReason(
                code=(
                    RecommendationReasonCode
                    .deadline_soon
                ),
                message="Su deadline está cerca.",
                score=3,
            ),
        ],
    )

    explanation = service.build(
        recommendation
    )

    assert (
        explanation.type
        == ExplanationType.recommendation
    )

    assert (
        "Preparar presentación"
        in explanation.title
    )

    assert (
        explanation.summary
        == recommendation.summary
    )

    assert len(explanation.details) == 2

    assert (
        "prioridad alta"
        in explanation.details[0]
    )

    assert (
        "deadline"
        in explanation.details[1]
    )