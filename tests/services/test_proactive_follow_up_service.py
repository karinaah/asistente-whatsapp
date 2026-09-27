from datetime import date

from app.models.proactive_follow_up import (
    FollowUpType,
)
from app.models.task import Task
from app.services.proactive_follow_up_service import (
    ProactiveFollowUpService,
)


class FakeFollowUpRepository:
    def __init__(self):
        self.created = []
        self.exists = False

    def exists_for_day(
        self,
        db,
        user_id,
        follow_up_type,
        target_date,
    ):
        return self.exists

    def create(
        self,
        db,
        follow_up,
    ):
        self.created.append(follow_up)
        return follow_up


class FakeTaskService:
    def __init__(self, tasks):
        self.tasks = tasks

    def get_plannable(
        self,
        db,
        user_id=None,
    ):
        return self.tasks


class FakeNotificationService:
    def __init__(self):
        self.created_from_follow_ups = []

    def create_from_follow_up(
        self,
        db,
        follow_up,
    ):
        self.created_from_follow_ups.append(
            follow_up
        )


def test_creates_follow_up_when_user_has_pending_tasks():
    repository = FakeFollowUpRepository()
    notification_service = FakeNotificationService()

    task_service = FakeTaskService(
        [
            Task(
                user_id=1,
                title="Preparar informe",
                estimated_minutes=60,
                preferred_date=date(
                    2026,
                    9,
                    28,
                ),
            ),
        ]
    )

    service = ProactiveFollowUpService(
        repository=repository,
        task_service=task_service,
        notification_service=notification_service,
    )

    follow_up = service.check_pending_tasks(
        db=None,
        user_id=1,
        target_date=date(2026, 9, 28),
    )

    assert follow_up is not None
    assert (
        follow_up.follow_up_type
        == FollowUpType.PENDING_TASKS
    )
    assert follow_up.user_id == 1
    assert len(repository.created) == 1

    assert (
        len(
            notification_service
            .created_from_follow_ups
        )
        == 1
    )

    assert (
        notification_service
        .created_from_follow_ups[0]
        == follow_up
    )


def test_does_not_create_follow_up_without_pending_tasks():
    repository = FakeFollowUpRepository()

    service = ProactiveFollowUpService(
        repository=repository,
        task_service=FakeTaskService([]),
    )

    follow_up = service.check_pending_tasks(
        db=None,
        user_id=1,
        target_date=date(2026, 9, 28),
    )

    assert follow_up is None
    assert repository.created == []


def test_does_not_duplicate_follow_up_same_day():
    repository = FakeFollowUpRepository()
    repository.exists = True

    task_service = FakeTaskService(
        [
            Task(
                user_id=1,
                title="Preparar informe",
                estimated_minutes=60,
                preferred_date=date(
                    2026,
                    9,
                    28,
                ),
            ),
        ]
    )

    service = ProactiveFollowUpService(
        repository=repository,
        task_service=task_service,
    )

    follow_up = service.check_pending_tasks(
        db=None,
        user_id=1,
        target_date=date(2026, 9, 28),
    )

    assert follow_up is None
    assert repository.created == []