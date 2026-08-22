from enum import Enum


class AssistantIntent(str, Enum):
    planning = "planning"
    replanning = "replanning"
    recommendation = "recommendation"
    learning = "learning"
    explanation = "explanation"
    follow_up = "follow_up"
    task_creation = "task_creation"
    unknown = "unknown"