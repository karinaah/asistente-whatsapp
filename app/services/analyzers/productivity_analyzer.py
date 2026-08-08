from app.models.productivity_insight import ProductivityInsight
from app.models.task_execution import TaskExecution
from app.services.execution_analysis_service import (
    ExecutionAnalysisService,
)


class ProductivityAnalyzer:
    def __init__(self) -> None:
        self.analysis_service = ExecutionAnalysisService()

    def analyze(
        self,
        executions: list[TaskExecution],
    ) -> ProductivityInsight:
        high_energy_errors = []
        low_energy_errors = []

        for execution in executions:
            if (
                execution.human_state is None
                or execution.human_state.energy is None
            ):
                continue

            analysis = self.analysis_service.analyze(
                execution
            )

            energy = execution.human_state.energy.value

            if energy in {"alta", "muy_alta"}:
                high_energy_errors.append(
                    analysis.error_percentage
                )

            if energy in {"baja", "muy_baja"}:
                low_energy_errors.append(
                    analysis.error_percentage
                )

        return ProductivityInsight(
            high_energy_average_error=(
                round(
                    sum(high_energy_errors)
                    / len(high_energy_errors),
                    2,
                )
                if high_energy_errors
                else 0.0
            ),
            low_energy_average_error=(
                round(
                    sum(low_energy_errors)
                    / len(low_energy_errors),
                    2,
                )
                if low_energy_errors
                else 0.0
            ),
        )