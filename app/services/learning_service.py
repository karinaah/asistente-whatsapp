from app.models.learning_insight import LearningInsight
from app.models.task_execution import TaskExecution
from app.services.analyzers.category_analyzer import (
    CategoryAnalyzer,
)
from app.services.analyzers.estimation_analyzer import (
    EstimationAnalyzer,
)
from app.services.analyzers.habit_analyzer import (
    HabitAnalyzer,
)
from app.services.analyzers.productivity_analyzer import (
    ProductivityAnalyzer,
)


class LearningService:
    def __init__(self) -> None:
        self.estimation_analyzer = (
            EstimationAnalyzer()
        )
        self.category_analyzer = (
            CategoryAnalyzer()
        )
        self.productivity_analyzer = (
            ProductivityAnalyzer()
        )
        self.habit_analyzer = (
            HabitAnalyzer()
        )

    def generate_insights(
        self,
        executions: list[TaskExecution],
    ) -> dict[str, object]:
        return {
            "estimation": self.estimation_analyzer.analyze(
                executions
            ),
            "categories": self.category_analyzer.analyze(
                executions
            ),
            "productivity": (
                self.productivity_analyzer.analyze(
                    executions
                )
            ),
            "habits": self.habit_analyzer.analyze(
                executions
            ),
        }