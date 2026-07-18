from typing import Protocol

from app.models.task import Task


class AIService(Protocol):
    def extract_tasks(self, text: str) -> list[Task]:
        ...