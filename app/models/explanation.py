from enum import Enum

from pydantic import BaseModel, Field


class ExplanationType(str, Enum):
    adaptive_profile = "adaptive_profile"
    recommendation = "recommendation"
    planning = "planning"
    learning = "learning"


class Explanation(BaseModel):
    type: ExplanationType

    title: str = Field(
        min_length=1,
    )

    summary: str = Field(
        min_length=1,
    )

    details: list[str] = Field(
        default_factory=list,
    )