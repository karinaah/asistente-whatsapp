from pydantic import BaseModel


class AdaptiveProfile(BaseModel):
    generated_from_executions: int

    work_duration_multiplier: float = 1.0
    study_duration_multiplier: float = 1.0
    personal_duration_multiplier: float = 1.0
    health_duration_multiplier: float = 1.0
    other_duration_multiplier: float = 1.0

    prefers_short_tasks_when_low_energy: bool = False

    best_energy: str | None = None
    best_focus: str | None = None

    confidence: float = 0.0