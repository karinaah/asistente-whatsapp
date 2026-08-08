from app.models.adaptive_profile import AdaptiveProfile
from app.models.task_execution import TaskExecution
from app.services.adaptive_profile_builder import (
    AdaptiveProfileBuilder,
)
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
        self.estimation_analyzer = EstimationAnalyzer()
        self.category_analyzer = CategoryAnalyzer()
        self.productivity_analyzer = ProductivityAnalyzer()
        self.habit_analyzer = HabitAnalyzer()
        self.profile_builder = AdaptiveProfileBuilder()

    def build_profile(
        self,
        executions: list[TaskExecution],
    ) -> AdaptiveProfile:
        estimation_insights = (
            self.estimation_analyzer.analyze(
                executions
            )
        )

        productivity_insight = (
            self.productivity_analyzer.analyze(
                executions
            )
        )

        return self.profile_builder.build(
            estimation_insights=estimation_insights,
            productivity=productivity_insight,
        )