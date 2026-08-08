from app.models.learning_insight import LearningInsight
from app.models.task_execution import TaskExecution
from app.services.execution_analysis_service import (
    ExecutionAnalysisService,
)


class EstimationAnalyzer:
    def __init__(self) -> None:
        self.analysis_service = (
            ExecutionAnalysisService()
        )

    def analyze(
        self,
        executions: list[TaskExecution],
    ) -> list[LearningInsight]:
        if not executions:
            return []

        insights: list[LearningInsight] = []

        by_category: dict[str, list[TaskExecution]] = {}

        for execution in executions:
            by_category.setdefault(
                execution.category.value,
                [],
            ).append(execution)

        for category, items in by_category.items():
            analyses = [
                self.analysis_service.analyze(item)
                for item in items
            ]

            average_error = (
                sum(
                    analysis.error_percentage
                    for analysis in analyses
                )
                / len(analyses)
            )

            average_estimated = (
                sum(
                    item.estimated_minutes
                    for item in items
                )
                / len(items)
            )

            average_actual = (
                sum(
                    item.actual_minutes
                    for item in items
                )
                / len(items)
            )

            insights.append(
                LearningInsight(
                    category=category,
                    executions=len(items),
                    average_error_percentage=round(
                        average_error,
                        2,
                    ),
                    average_estimated_minutes=round(
                        average_estimated,
                        2,
                    ),
                    average_actual_minutes=round(
                        average_actual,
                        2,
                    ),
                )
            )

        return insights