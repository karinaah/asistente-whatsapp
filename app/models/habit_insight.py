from pydantic import BaseModel


class HabitInsight(BaseModel):
    executions: int
    average_actual_minutes: float