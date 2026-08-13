from enum import Enum


class AssistantIntent(str, Enum):
    planning = "planning"
    recommendation = "recommendation"
    learning = "learning"
    explanation = "explanation"
    follow_up = "follow_up"
    unknown = "unknown"
