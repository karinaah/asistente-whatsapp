from app.models.execution_analysis import (
    EstimationStatus,
    ExecutionAnalysis,
)
from app.models.task_execution import TaskExecution


class ExecutionAnalysisService:
    def analyze(
        self,
        execution: TaskExecution,
    ) -> ExecutionAnalysis:
        difference = (
            execution.actual_minutes
            - execution.estimated_minutes
        )

        error_percentage = (
            abs(difference)
            / execution.estimated_minutes
        ) * 100

        if difference > 0:
            status = EstimationStatus.underestimated
        elif difference < 0:
            status = EstimationStatus.overestimated
        else:
            status = EstimationStatus.accurate

        return ExecutionAnalysis(
            task_id=execution.task_id,
            estimated_minutes=execution.estimated_minutes,
            actual_minutes=execution.actual_minutes,
            difference_minutes=difference,
            error_percentage=round(
                error_percentage,
                2,
            ),
            estimation_status=status,
        )