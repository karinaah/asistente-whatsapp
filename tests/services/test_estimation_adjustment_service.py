from app.models.learning_insight import LearningInsight
from app.services.estimation_adjustment_service import (
    EstimationAdjustmentService,
)


def test_adjust_increases_estimation():
    service = EstimationAdjustmentService()

    insight = LearningInsight(
        category="trabajo",
        executions=5,
        average_error_percentage=20.0,
        average_estimated_minutes=60,
        average_actual_minutes=72,
    )

    adjusted = service.adjust(60, insight)

    assert adjusted == 72


def test_adjust_requires_minimum_history():
    service = EstimationAdjustmentService()

    insight = LearningInsight(
        category="trabajo",
        executions=2,
        average_error_percentage=20.0,
        average_estimated_minutes=60,
        average_actual_minutes=72,
    )

    adjusted = service.adjust(60, insight)

    assert adjusted == 60


def test_adjust_never_returns_zero():
    service = EstimationAdjustmentService()

    insight = LearningInsight(
        category="trabajo",
        executions=10,
        average_error_percentage=95.0,
        average_estimated_minutes=100,
        average_actual_minutes=1,
    )

    adjusted = service.adjust(1, insight)

    assert adjusted == 1