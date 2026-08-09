from enum import Enum


class AssistantIntent(str, Enum):
    planning = "planning"
    recommendation = "recommendation"
    learning = "learning"
    explanation = "explanation"
    unknown = "unknown"