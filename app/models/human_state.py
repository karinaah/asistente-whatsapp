from enum import Enum

from pydantic import BaseModel, Field


class EnergyLevel(str, Enum):
    very_low = "muy_baja"
    low = "baja"
    medium = "media"
    high = "alta"
    very_high = "muy_alta"


class FocusLevel(str, Enum):
    low = "bajo"
    medium = "medio"
    high = "alto"


class StressLevel(str, Enum):
    low = "bajo"
    medium = "medio"
    high = "alto"


class HumanState(BaseModel):
    energy: EnergyLevel | None = None
    focus: FocusLevel | None = None
    stress: StressLevel | None = None
    available_minutes: int | None = Field(
        default=None,
        ge=0,
    )