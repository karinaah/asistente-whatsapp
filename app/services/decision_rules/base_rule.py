from abc import ABC, abstractmethod

from app.models.recommendation import RecommendationReason
from app.models.schedule import ScheduledTask


class DecisionRule(ABC):
    @abstractmethod
    def evaluate(
        self,
        scheduled_task: ScheduledTask,
    ) -> list[RecommendationReason]:
        """Evalúa una tarea programada y devuelve las razones aplicables."""
        raise NotImplementedError