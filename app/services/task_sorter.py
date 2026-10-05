from app.models.task import (
    Task,
    TaskFlexibility,
    TaskPriority,
    TaskStatus,
)


class TaskSorter:
    status_order = {
        TaskStatus.in_progress: 0,
        TaskStatus.pending: 1,
        TaskStatus.completed: 2,
        TaskStatus.cancelled: 3,
    }

    priority_order = {
        TaskPriority.high: 0,
        TaskPriority.medium: 1,
        TaskPriority.low: 2,
    }

    flexibility_order = {
        TaskFlexibility.fixed: 0,
        TaskFlexibility.semi_flexible: 1,
        TaskFlexibility.flexible: 2,
    }    

    def sort(self, tasks: list[Task]) -> list[Task]:
        return sorted(
            tasks,
            key=lambda task: (
                self.status_order[task.status],
                self.flexibility_order[task.flexibility],
                self.priority_order[task.priority],
                task.deadline or task.created_at,
                -task.estimated_minutes,
            ),
        )