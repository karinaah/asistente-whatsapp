from abc import ABC, abstractmethod

from app.models.recommendation import (
    DecisionContext,
    RecommendationReason,
)
from app.models.schedule import ScheduledTask


class DecisionRule(ABC):
    @abstractmethod
    def evaluate(
        self,
        scheduled_task: ScheduledTask,
        context: DecisionContext,
    ) -> list[RecommendationReason]:
        raise NotImplementedError