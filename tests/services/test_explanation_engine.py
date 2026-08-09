from app.models.adaptive_profile import (
    AdaptiveProfile,
)
from app.models.explanation import (
    ExplanationType,
)
from app.services.explanation_engine import (
    ExplanationEngine,
)


def test_explain_adaptive_profile():
    engine = ExplanationEngine()

    profile = AdaptiveProfile(
        generated_from_executions=10,
        work_duration_multiplier=1.2,
        prefers_short_tasks_when_low_energy=True,
        confidence=0.75,
    )

    explanation = engine.explain_adaptive_profile(
        profile
    )

    assert (
        explanation.type
        == ExplanationType.adaptive_profile
    )

    assert (
        explanation.title
        == "Lo que he aprendido sobre ti"
    )

    assert (
        "10 ejecuciones"
        in explanation.summary
    )

    assert (
        "75%"
        in explanation.summary
    )

    assert len(explanation.details) == 2

    assert (
        "20%"
        in explanation.details[0]
    )

    assert (
        "baja energía"
        in explanation.details[1]
    )