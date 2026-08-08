from pydantic import BaseModel


class LearningInsight(BaseModel):
    category: str

    executions: int

    average_error_percentage: float

    average_estimated_minutes: float

    average_actual_minutes: float