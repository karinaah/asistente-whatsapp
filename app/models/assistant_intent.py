from enum import Enum


class AssistantIntent(str, Enum):
    planning = "planning"
    replanning = "replanning"
    active_task_delay = "active_task_delay"
    recommendation = "recommendation"
    learning = "learning"
    explanation = "explanation"
    follow_up = "follow_up"
    task_creation = "task_creation"
    unknown = "unknown"