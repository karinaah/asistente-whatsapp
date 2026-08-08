from enum import Enum

from pydantic import BaseModel


class EstimationStatus(str, Enum):
    underestimated = "subestimada"
    overestimated = "sobreestimada"
    accurate = "precisa"


class ExecutionAnalysis(BaseModel):
    task_id: int

    estimated_minutes: int
    actual_minutes: int

    difference_minutes: int
    error_percentage: float

    estimation_status: EstimationStatus