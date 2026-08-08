from app.models.learning_insight import LearningInsight
from app.models.task_execution import TaskExecution
from app.services.analyzers.estimation_analyzer import (
    EstimationAnalyzer,
)


class CategoryAnalyzer:
    def __init__(self) -> None:
        self.estimation_analyzer = EstimationAnalyzer()

    def analyze(
        self,
        executions: list[TaskExecution],
    ) -> list[LearningInsight]:
        insights = self.estimation_analyzer.analyze(
            executions
        )

        return sorted(
            insights,
            key=lambda insight: (
                insight.average_error_percentage
            ),
            reverse=True,
        )