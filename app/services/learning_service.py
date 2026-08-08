from collections import defaultdict

from app.models.task_execution import TaskExecution
from app.services.execution_analysis_service import (
    ExecutionAnalysisService,
)


class LearningService:
    def __init__(self) -> None:
        self.analysis_service = ExecutionAnalysisService()

    def average_error_by_category(
        self,
        executions: list[TaskExecution],
    ) -> dict[str, float]:
        errors_by_category = defaultdict(list)

        for execution in executions:
            analysis = self.analysis_service.analyze(
                execution
            )

            errors_by_category[
                execution.category.value
            ].append(
                analysis.error_percentage
            )

        return {
            category: round(
                sum(errors) / len(errors),
                2,
            )
            for category, errors
            in errors_by_category.items()
        }