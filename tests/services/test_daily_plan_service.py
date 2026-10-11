from datetime import date, datetime
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.daily_plan_db import DailyPlanDB
from app.models.user_db import UserDB
from app.models.schedule import PlanningResponse, ScheduledTask
from app.models.task import Task

from app.services.daily_plan_service import DailyPlanService
from app.models.task_db import TaskDB
from app.models.routine_db import RoutineDB

def create_test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    return TestingSessionLocal()


def create_user(db):
    user = UserDB(name="Usuario de prueba")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_empty_plan():
    return PlanningResponse(
        scheduled_tasks=[],
        unscheduled_tasks=[],
        timeline=[],
    )


def test_save_and_get_daily_plan():
    db = create_test_db()

    try:
        user = create_user(db)
        service = DailyPlanService()
        plan_date = date(2026, 10, 11)

        plan = create_empty_plan()

        service.save(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
            plan=plan,
        )

        recovered = service.get(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
        )

        assert recovered is not None
        assert recovered == plan

    finally:
        db.close()


def test_save_updates_existing_plan():
    db = create_test_db()

    try:
        user = create_user(db)
        service = DailyPlanService()
        plan_date = date(2026, 10, 11)

        plan = create_empty_plan()

        service.save(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
            plan=plan,
        )

        service.save(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
            plan=plan,
        )

        records = db.scalars(
            select(DailyPlanDB).where(
                DailyPlanDB.user_id == user.id,
                DailyPlanDB.plan_date == plan_date,
            )
        ).all()

        assert len(records) == 1

    finally:
        db.close()


def test_get_does_not_mix_users_or_dates():
    db = create_test_db()

    try:
        user_1 = create_user(db)
        user_2 = create_user(db)
        service = DailyPlanService()

        plan_date = date(2026, 10, 11)

        service.save(
            db=db,
            user_id=user_1.id,
            plan_date=plan_date,
            plan=create_empty_plan(),
        )

        other_user_plan = service.get(
            db=db,
            user_id=user_2.id,
            plan_date=plan_date,
        )

        other_date_plan = service.get(
            db=db,
            user_id=user_1.id,
            plan_date=date(2026, 10, 12),
        )

        assert other_user_plan is None
        assert other_date_plan is None

    finally:
        db.close()

def test_save_and_update_plan_with_scheduled_task():
    db = create_test_db()

    try:
        user = create_user(db)
        service = DailyPlanService()
        plan_date = date(2026, 10, 11)

        task = Task(
            id=101,
            user_id=user.id,
            title="Código tesis",
            estimated_minutes=120,
        )

        initial_plan = PlanningResponse(
            scheduled_tasks=[
                ScheduledTask(
                    task=task,
                    start_time=datetime(2026, 10, 11, 10, 0),
                    end_time=datetime(2026, 10, 11, 12, 0),
                )
            ],
            unscheduled_tasks=[],
            timeline=[],
        )

        service.save(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
            plan=initial_plan,
        )

        recovered = service.get(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
        )

        assert recovered is not None
        assert recovered == initial_plan
        assert recovered.scheduled_tasks[0].task.id == 101
        assert recovered.scheduled_tasks[0].task.title == "Código tesis"
        assert recovered.scheduled_tasks[0].start_time.hour == 10

        updated_plan = PlanningResponse(
            scheduled_tasks=[
                ScheduledTask(
                    task=task,
                    start_time=datetime(2026, 10, 11, 13, 0),
                    end_time=datetime(2026, 10, 11, 15, 0),
                )
            ],
            unscheduled_tasks=[],
            timeline=[],
        )

        service.save(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
            plan=updated_plan,
        )

        recovered_updated = service.get(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
        )

        assert recovered_updated is not None
        assert recovered_updated == updated_plan
        assert recovered_updated.scheduled_tasks[0].start_time.hour == 13
        assert recovered_updated.scheduled_tasks[0].end_time.hour == 15

        records = db.scalars(
            select(DailyPlanDB).where(
                DailyPlanDB.user_id == user.id,
                DailyPlanDB.plan_date == plan_date,
            )
        ).all()

        assert len(records) == 1

    finally:
        db.close()


def test_invalidate_daily_plan():
    db = create_test_db()

    try:
        user_1 = create_user(db)
        user_2 = create_user(db)

        service = DailyPlanService()
        plan_date = date(2026, 10, 11)

        service.save(
            db=db,
            user_id=user_1.id,
            plan_date=plan_date,
            plan=create_empty_plan(),
        )

        service.save(
            db=db,
            user_id=user_2.id,
            plan_date=plan_date,
            plan=create_empty_plan(),
        )

        service.invalidate(
            db=db,
            user_id=user_1.id,
            plan_date=plan_date,
        )

        invalidated_plan = service.get(
            db=db,
            user_id=user_1.id,
            plan_date=plan_date,
        )

        other_user_plan = service.get(
            db=db,
            user_id=user_2.id,
            plan_date=plan_date,
        )

        assert invalidated_plan is None
        assert other_user_plan is not None

    finally:
        db.close()

def test_completing_task_preserves_daily_plan():
    db = create_test_db()

    try:
        user = create_user(db)
        service = DailyPlanService()
        plan_date = date.today()

        service.save(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
            plan=create_empty_plan(),
        )

        from app.services.task_service import TaskService

        task_service = TaskService()

        task = task_service.create(
            db=db,
            task=Task(
                user_id=user.id,
                title="Preparar presentación",
                estimated_minutes=60,
            ),
        )

        # Crear nuevamente la agenda, ya que
        # crear una tarea también la invalida.
        service.save(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
            plan=create_empty_plan(),
        )

        assert service.get(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
        ) is not None

        task_service.mark_completed(
            db=db,
            task_id=task.id,
            user_id=user.id,
        )

        assert service.get(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
        ) is not None

    finally:
        db.close()

def test_save_proposal_preserves_confirmed_plan():
    db = create_test_db()

    try:
        user = create_user(db)
        service = DailyPlanService()
        plan_date = date(2026, 10, 11)

        task = Task(
            id=101,
            user_id=user.id,
            title="Código tesis",
            estimated_minutes=60,
        )

        # Agenda original: 10:00 a 11:00
        original_plan = PlanningResponse(
            scheduled_tasks=[
                ScheduledTask(
                    task=task,
                    start_time=datetime(2026, 10, 11, 10, 0),
                    end_time=datetime(2026, 10, 11, 11, 0),
                )
            ],
            unscheduled_tasks=[],
            timeline=[],
        )

        # Propuesta: mover la tarea a las 15:00
        proposed_plan = PlanningResponse(
            scheduled_tasks=[
                ScheduledTask(
                    task=task,
                    start_time=datetime(2026, 10, 11, 15, 0),
                    end_time=datetime(2026, 10, 11, 16, 0),
                )
            ],
            unscheduled_tasks=[],
            timeline=[],
        )

        service.save(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
            plan=original_plan,
        )

        service.save_proposal(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
            proposal=proposed_plan,
        )

        confirmed = service.get(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
        )

        proposal = service.get_proposal(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
        )

        assert confirmed == original_plan
        assert proposal == proposed_plan

        assert confirmed.scheduled_tasks[0].start_time.hour == 10
        assert proposal.scheduled_tasks[0].start_time.hour == 15

    finally:
        db.close()

def test_accept_proposal_updates_confirmed_plan():
    db = create_test_db()

    try:
        user = create_user(db)
        service = DailyPlanService()
        plan_date = date(2026, 10, 11)

        task = Task(
            id=101,
            user_id=user.id,
            title="Código tesis",
            estimated_minutes=60,
        )

        original_plan = PlanningResponse(
            scheduled_tasks=[
                ScheduledTask(
                    task=task,
                    start_time=datetime(2026, 10, 11, 10, 0),
                    end_time=datetime(2026, 10, 11, 11, 0),
                )
            ],
            unscheduled_tasks=[],
            timeline=[],
        )

        proposed_plan = PlanningResponse(
            scheduled_tasks=[
                ScheduledTask(
                    task=task,
                    start_time=datetime(2026, 10, 11, 15, 0),
                    end_time=datetime(2026, 10, 11, 16, 0),
                )
            ],
            unscheduled_tasks=[],
            timeline=[],
        )

        service.save(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
            plan=original_plan,
        )

        service.save_proposal(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
            proposal=proposed_plan,
        )

        service.accept_proposal(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
        )

        confirmed = service.get(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
        )

        pending_proposal = service.get_proposal(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
        )

        records = db.scalars(
            select(DailyPlanDB).where(
                DailyPlanDB.user_id == user.id,
                DailyPlanDB.plan_date == plan_date,
            )
        ).all()

        assert confirmed == proposed_plan
        assert confirmed.scheduled_tasks[0].start_time.hour == 15
        assert pending_proposal is None
        assert len(records) == 1

    finally:
        db.close()         

def test_reject_proposal_preserves_confirmed_plan():
    db = create_test_db()

    try:
        user = create_user(db)
        service = DailyPlanService()
        plan_date = date(2026, 10, 11)

        task = Task(
            id=101,
            user_id=user.id,
            title="Código tesis",
            estimated_minutes=60,
        )

        original_plan = PlanningResponse(
            scheduled_tasks=[
                ScheduledTask(
                    task=task,
                    start_time=datetime(2026, 10, 11, 10, 0),
                    end_time=datetime(2026, 10, 11, 11, 0),
                )
            ],
            unscheduled_tasks=[],
            timeline=[],
        )

        proposed_plan = PlanningResponse(
            scheduled_tasks=[
                ScheduledTask(
                    task=task,
                    start_time=datetime(2026, 10, 11, 15, 0),
                    end_time=datetime(2026, 10, 11, 16, 0),
                )
            ],
            unscheduled_tasks=[],
            timeline=[],
        )

        service.save(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
            plan=original_plan,
        )

        service.save_proposal(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
            proposal=proposed_plan,
        )

        service.reject_proposal(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
        )

        confirmed = service.get(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
        )

        pending_proposal = service.get_proposal(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
        )

        assert confirmed == original_plan
        assert confirmed.scheduled_tasks[0].start_time.hour == 10
        assert pending_proposal is None

    finally:
        db.close()

def test_updating_confirmed_plan_discards_old_proposal():
    db = create_test_db()

    try:
        user = create_user(db)
        service = DailyPlanService()
        plan_date = date(2026, 10, 11)

        task = Task(
            id=101,
            user_id=user.id,
            title="Código tesis",
            estimated_minutes=60,
        )

        def make_plan(hour):
            return PlanningResponse(
                scheduled_tasks=[
                    ScheduledTask(
                        task=task,
                        start_time=datetime(2026, 10, 11, hour, 0),
                        end_time=datetime(2026, 10, 11, hour + 1, 0),
                    )
                ],
                unscheduled_tasks=[],
                timeline=[],
            )

        original_plan = make_plan(10)
        proposed_plan = make_plan(15)
        updated_plan = make_plan(12)

        service.save(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
            plan=original_plan,
        )

        service.save_proposal(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
            proposal=proposed_plan,
        )

        # La agenda confirmada cambia antes
        # de que se acepte la propuesta.
        service.save(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
            plan=updated_plan,
        )

        confirmed = service.get(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
        )

        pending_proposal = service.get_proposal(
            db=db,
            user_id=user.id,
            plan_date=plan_date,
        )

        assert confirmed == updated_plan
        assert pending_proposal is None

    finally:
        db.close()        