from app.models.proactive_follow_up import (
    FollowUpStatus,
    FollowUpType,
    ProactiveFollowUp,
)


def test_creates_pending_proactive_follow_up():
    follow_up = ProactiveFollowUp(
        user_id=1,
        follow_up_type=FollowUpType.PENDING_TASKS,
        title="Tareas pendientes",
        message="Todavía tienes tareas pendientes para hoy.",
    )

    assert follow_up.user_id == 1
    assert (
        follow_up.follow_up_type
        == FollowUpType.PENDING_TASKS
    )
    assert follow_up.status == FollowUpStatus.PENDING
    assert follow_up.task_id is None
    assert follow_up.routine_id is None
    assert follow_up.resolved_at is None


def test_follow_up_can_reference_task_and_routine():
    follow_up = ProactiveFollowUp(
        user_id=1,
        follow_up_type=FollowUpType.ROUTINE_PENDING,
        title="Rutina pendiente",
        message="Tu rutina de yoga sigue pendiente.",
        task_id=10,
        routine_id=5,
    )

    assert follow_up.task_id == 10
    assert follow_up.routine_id == 5