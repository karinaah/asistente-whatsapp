from enum import Enum

from pydantic import BaseModel


class PlanningReasonCode(str, Enum):
    earliest_available = "earliest_available"
    preferred_start_time = "preferred_start_time"
    preferred_time_of_day = "preferred_time_of_day"
    avoids_busy_block = "avoids_busy_block"
    respects_break = "respects_break"
    adaptive_duration = "adaptive_duration"


class PlanningReason(BaseModel):
    code: PlanningReasonCode
    message: str