from fastapi.testclient import TestClient

from app.config.database import SessionLocal
from app.main import app
from app.models.task import Task
from app.models.task_db import TaskDB
from app.models.user_db import UserDB
from app.services.task_service import TaskService
from app.services.user_service import UserService
from app.models.conversation_message_db import ConversationMessageDB

client = TestClient(app)
user_service = UserService()

def test_web_home_returns_200():
    response = client.get("/web")

    assert response.status_code == 200

def test_web_tasks_returns_200():
    response = client.get("/web/tasks")

    assert response.status_code == 200    

def test_web_chat_returns_200():
    response = client.get("/web/chat")

    assert response.status_code == 200    

def test_web_chat_creates_session_cookie():
    client.cookies.clear()

    response = client.get("/web/chat")

    assert response.status_code == 200
    assert "aura_session_id" in response.cookies

    session_id = response.cookies.get(
        "aura_session_id"
    )

    assert session_id is not None
    assert session_id != ""    


def test_web_chat_creates_user_cookie():
    client.cookies.clear()

    response = client.get("/web/chat")

    assert response.status_code == 200
    assert "aura_user_id" in response.cookies

    user_id = response.cookies.get(
        "aura_user_id"
    )

    assert user_id is not None
    assert user_id != ""
    assert int(user_id) >= 1

def test_web_home_replaces_stale_user_cookie():
    client.cookies.clear()

    client.cookies.set(
        "aura_user_id",
        "999999999",
        domain="testserver.local",
        path="/",
    )

    response = client.get("/web")

    assert response.status_code == 200

    user_id = client.cookies.get(
        "aura_user_id"
    )

    assert user_id is not None
    assert user_id != "999999999"

    with SessionLocal() as db:
        user = user_service.get_user(
            db,
            user_id=int(user_id),
        )

    assert user is not None

def test_web_chat_reuses_user_cookie():
    client.cookies.clear()

    first_response = client.get("/web/chat")

    user_id = first_response.cookies.get(
        "aura_user_id"
    )

    second_response = client.get("/web/chat")

    assert second_response.status_code == 200

    assert (
        client.cookies.get("aura_user_id")
        == user_id
    )

def test_web_chat_reuses_session_cookie():
    client.cookies.clear()

    get_response = client.get("/web/chat")

    session_id = get_response.cookies.get(
        "aura_session_id"
    )

    post_response = client.post(
        "/web/chat",
        data={
            "message": "Hola",
        },
    )

    assert post_response.status_code == 200

    assert (
        client.cookies.get("aura_session_id")
        == session_id
    )    

def test_web_chat_persists_memory_with_cookie_session():
    client.cookies.clear()

    get_response = client.get("/web/chat")

    session_id = get_response.cookies.get(
        "aura_session_id"
    )

    post_response = client.post(
        "/web/chat",
        data={
            "message": "¿Qué hago ahora?",
        },
    )

    assert post_response.status_code == 200

    from app.config.database import SessionLocal
    from app.repositories.conversation_memory_repository import (
        ConversationMemoryRepository,
    )
    from app.models.assistant_intent import AssistantIntent

    db = SessionLocal()

    try:
        repository = ConversationMemoryRepository()

        context = repository.get(
            db,
            session_id=session_id,
        )

        assert context is not None
        assert (
            context.last_intent
            == AssistantIntent.recommendation
        )

    finally:
        db.close()


def test_web_chat_persists_memory_with_cookie_user():
    client.cookies.clear()

    get_response = client.get("/web/chat")

    session_id = get_response.cookies.get(
        "aura_session_id"
    )
    user_id = get_response.cookies.get(
        "aura_user_id"
    )

    assert session_id is not None
    assert user_id is not None

    post_response = client.post(
        "/web/chat",
        data={
            "message": "Planifica mi día",
        },
    )

    assert post_response.status_code == 200

    from app.config.database import SessionLocal
    from app.models.conversation_context_db import (
        ConversationContextDB,
    )

    db = SessionLocal()

    try:
        context_db = (
            db.query(ConversationContextDB)
            .filter(
                ConversationContextDB.session_id
                == session_id
            )
            .first()
        )

        assert context_db is not None
        assert context_db.user_id == int(user_id)

    finally:
        db.close()  

def test_web_home_shows_pending_notification():
    client.cookies.clear()

    first_response = client.get("/web")

    assert first_response.status_code == 200

    user_id = client.cookies.get(
        "aura_user_id"
    )

    assert user_id is not None

    from app.config.database import SessionLocal
    from app.models.notification import Notification
    from app.repositories.notification_repository import (
        NotificationRepository,
    )

    db = SessionLocal()

    try:
        repository = NotificationRepository()

        notification = repository.create(
            db,
            Notification(
                user_id=int(user_id),
                title="Recordatorio AURA",
                message=(
                    "Tienes una tarea pendiente "
                    "para completar hoy."
                ),
            ),
        )

        assert notification.id is not None

    finally:
        db.close()

    response = client.get("/web")

    assert response.status_code == 200
    assert "Recordatorio AURA" in response.text
    assert (
        "Tienes una tarea pendiente "
        "para completar hoy."
        in response.text
    )        

def test_web_notification_disappears_after_marking_as_read():
    client.cookies.clear()

    first_response = client.get("/web")

    assert first_response.status_code == 200

    user_id = client.cookies.get(
        "aura_user_id"
    )

    assert user_id is not None

    from app.config.database import SessionLocal
    from app.models.notification import (
        Notification,
        NotificationStatus,
    )
    from app.models.notification_db import NotificationDB
    from app.repositories.notification_repository import (
        NotificationRepository,
    )

    db = SessionLocal()

    try:
        repository = NotificationRepository()

        notification = repository.create(
            db,
            Notification(
                user_id=int(user_id),
                title="Notificación para cerrar",
                message=(
                    "Esta notificación debe "
                    "desaparecer después de leerla."
                ),
            ),
        )

        notification_id = notification.id

    finally:
        db.close()

    response = client.get("/web")

    assert response.status_code == 200
    assert "Notificación para cerrar" in response.text

    read_response = client.post(
        f"/web/notifications/{notification_id}/read",
        follow_redirects=False,
    )

    assert read_response.status_code == 303
    assert read_response.headers["location"] == "/web"

    db = SessionLocal()

    try:
        stored_notification = (
            db.query(NotificationDB)
            .filter(
                NotificationDB.id
                == notification_id
            )
            .first()
        )

        assert stored_notification is not None
        assert (
            stored_notification.status
            == NotificationStatus.READ.value
        )
        assert stored_notification.read_at is not None

    finally:
        db.close()

    response = client.get("/web")

    assert response.status_code == 200
    assert (
        "Notificación para cerrar"
        not in response.text
    )    

def test_web_routines_shows_only_current_user_routines():
    client.cookies.clear()

    response = client.get("/web")

    assert response.status_code == 200

    user_id = client.cookies.get(
        "aura_user_id"
    )

    assert user_id is not None

    from app.config.database import SessionLocal
    from app.models.routine import (
        Routine,
        Weekday,
    )
    from app.services.routine_service import (
        RoutineService,
    )
    from app.services.user_service import UserService

    db = SessionLocal()

    try:
        routine_service = RoutineService()
        local_user_service = UserService()

        other_user = local_user_service.create_user(
            db
        )

        routine_service.create(
            db,
            Routine(
                user_id=int(user_id),
                title="Rutina visible v18",
                weekdays=[
                    Weekday.monday,
                    Weekday.wednesday,
                ],
                estimated_minutes=30,
            ),
        )

        routine_service.create(
            db,
            Routine(
                user_id=other_user.id,
                title="Rutina privada v18",
                weekdays=[
                    Weekday.tuesday,
                ],
                estimated_minutes=45,
            ),
        )

    finally:
        db.close()

    response = client.get("/web/routines")

    assert response.status_code == 200
    assert "Rutina visible v18" in response.text
    assert "Rutina privada v18" not in response.text    

def test_web_can_create_routine():
    client.cookies.clear()

    response = client.get("/web/routines")

    assert response.status_code == 200

    user_id = client.cookies.get(
        "aura_user_id"
    )

    assert user_id is not None

    response = client.post(
        "/web/routines/create",
        data={
            "title": "Yoga mañana v18",
            "weekdays": ["0", "2", "4"],
            "preferred_start_time": "07:30",
            "estimated_minutes": "60",
            "category": "salud",
            "workspace": "personal",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert (
        response.headers["location"]
        == "/web/routines"
    )

    from app.config.database import SessionLocal
    from app.models.routine_db import RoutineDB

    db = SessionLocal()

    try:
        routine = (
            db.query(RoutineDB)
            .filter(
                RoutineDB.user_id
                == int(user_id),
                RoutineDB.title
                == "Yoga mañana v18",
            )
            .first()
        )

        assert routine is not None
        assert routine.estimated_minutes == 60
        assert routine.weekdays == [0, 2, 4]
        assert (
            routine.preferred_start_time.strftime(
                "%H:%M"
            )
            == "07:30"
        )
        assert routine.category == "salud"
        assert routine.workspace == "personal"

    finally:
        db.close()    

def test_web_can_deactivate_own_routine():
    client.cookies.clear()

    response = client.get("/web/routines")

    assert response.status_code == 200

    user_id = client.cookies.get(
        "aura_user_id"
    )

    assert user_id is not None

    from app.config.database import SessionLocal
    from app.models.routine import (
        Routine,
        Weekday,
    )
    from app.models.routine_db import RoutineDB
    from app.services.routine_service import (
        RoutineService,
    )

    db = SessionLocal()

    try:
        service = RoutineService()

        routine = service.create(
            db,
            Routine(
                user_id=int(user_id),
                title="Rutina desactivar v18",
                weekdays=[Weekday.monday],
                estimated_minutes=30,
            ),
        )

        routine_id = routine.id

    finally:
        db.close()

    response = client.post(
        f"/web/routines/{routine_id}/deactivate",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert (
        response.headers["location"]
        == "/web/routines"
    )

    db = SessionLocal()

    try:
        stored = (
            db.query(RoutineDB)
            .filter(
                RoutineDB.id == routine_id
            )
            .first()
        )

        assert stored is not None
        assert stored.active is False

    finally:
        db.close()        

def test_web_cannot_deactivate_other_user_routine():
    client.cookies.clear()

    response = client.get("/web/routines")

    assert response.status_code == 200

    current_user_id = client.cookies.get(
        "aura_user_id"
    )

    assert current_user_id is not None

    from app.config.database import SessionLocal
    from app.models.routine import (
        Routine,
        Weekday,
    )
    from app.models.routine_db import RoutineDB
    from app.services.routine_service import (
        RoutineService,
    )
    from app.services.user_service import UserService

    db = SessionLocal()

    try:
        service = RoutineService()
        local_user_service = UserService()

        other_user = local_user_service.create_user(
            db
        )

        routine = service.create(
            db,
            Routine(
                user_id=other_user.id,
                title="Rutina protegida v18",
                weekdays=[Weekday.tuesday],
                estimated_minutes=45,
            ),
        )

        routine_id = routine.id

    finally:
        db.close()

    response = client.post(
        f"/web/routines/{routine_id}/deactivate",
        follow_redirects=False,
    )

    assert response.status_code == 303

    db = SessionLocal()

    try:
        stored = (
            db.query(RoutineDB)
            .filter(
                RoutineDB.id == routine_id
            )
            .first()
        )

        assert stored is not None
        assert stored.active is True

    finally:
        db.close()        

def test_web_can_activate_own_routine():
    client.cookies.clear()

    response = client.get("/web/routines")

    assert response.status_code == 200

    user_id = client.cookies.get(
        "aura_user_id"
    )

    assert user_id is not None

    from app.config.database import SessionLocal
    from app.models.routine import (
        Routine,
        Weekday,
    )
    from app.models.routine_db import RoutineDB
    from app.services.routine_service import (
        RoutineService,
    )

    db = SessionLocal()

    try:
        service = RoutineService()

        routine = service.create(
            db,
            Routine(
                user_id=int(user_id),
                title="Rutina reactivar v18",
                weekdays=[Weekday.friday],
                estimated_minutes=30,
                active=False,
            ),
        )

        routine_id = routine.id

    finally:
        db.close()

    response = client.post(
        f"/web/routines/{routine_id}/activate",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert (
        response.headers["location"]
        == "/web/routines"
    )

    db = SessionLocal()

    try:
        stored = (
            db.query(RoutineDB)
            .filter(
                RoutineDB.id == routine_id
            )
            .first()
        )

        assert stored is not None
        assert stored.active is True

    finally:
        db.close()        

def test_web_availability_shows_only_current_user_availability():
    client.cookies.clear()

    response = client.get("/web")

    assert response.status_code == 200

    user_id = client.cookies.get(
        "aura_user_id"
    )

    assert user_id is not None

    from datetime import time

    from app.config.database import SessionLocal
    from app.models.recurring_availability import (
        RecurringAvailability,
    )
    from app.models.routine import Weekday
    from app.services.recurring_availability_service import (
        RecurringAvailabilityService,
    )
    from app.services.user_service import UserService

    db = SessionLocal()

    try:
        availability_service = (
            RecurringAvailabilityService()
        )
        local_user_service = UserService()

        other_user = local_user_service.create_user(
            db
        )

        availability_service.create(
            db,
            RecurringAvailability(
                user_id=int(user_id),
                weekday=Weekday.monday,
                start_time=time(8, 0),
                end_time=time(18, 0),
            ),
        )

        availability_service.create(
            db,
            RecurringAvailability(
                user_id=other_user.id,
                weekday=Weekday.tuesday,
                start_time=time(10, 0),
                end_time=time(20, 0),
            ),
        )

    finally:
        db.close()

    response = client.get(
        "/web/availability"
    )

    assert response.status_code == 200

    assert "08:00" in response.text
    assert "18:00" in response.text

    assert "10:00" not in response.text
    assert "20:00" not in response.text        

def test_web_can_create_availability():
    client.cookies.clear()

    response = client.get(
        "/web/availability"
    )

    assert response.status_code == 200

    user_id = client.cookies.get(
        "aura_user_id"
    )

    assert user_id is not None

    response = client.post(
        "/web/availability/create",
        data={
            "weekday": "0",
            "start_time": "08:30",
            "end_time": "17:30",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert (
        response.headers["location"]
        == "/web/availability"
    )

    from datetime import time

    from app.config.database import SessionLocal
    from app.models.recurring_availability_db import (
        RecurringAvailabilityDB,
    )

    db = SessionLocal()

    try:
        stored = (
            db.query(RecurringAvailabilityDB)
            .filter(
                RecurringAvailabilityDB.user_id
                == int(user_id),
                RecurringAvailabilityDB.weekday
                == 0,
            )
            .order_by(
                RecurringAvailabilityDB.id.desc()
            )
            .first()
        )

        assert stored is not None
        assert stored.start_time == time(8, 30)
        assert stored.end_time == time(17, 30)
        assert stored.active is True

    finally:
        db.close()    

def test_web_tasks_shows_only_current_user_tasks():
    client.cookies.clear()

    response = client.get("/web")

    assert response.status_code == 200

    user_id = int(
        client.cookies.get("aura_user_id")
    )

    db = SessionLocal()

    try:
        other_user = UserDB(
            name="Other Task User",
        )
        db.add(other_user)
        db.commit()
        db.refresh(other_user)

        task_service = TaskService()

        own_task = task_service.create(
            db,
            Task(
                user_id=user_id,
                title="MY UNIQUE WEB TASK",
                estimated_minutes=30,
            ),
        )

        other_task = task_service.create(
            db,
            Task(
                user_id=other_user.id,
                title="OTHER UNIQUE WEB TASK",
                estimated_minutes=30,
            ),
        )

        response = client.get("/web/tasks")

        assert response.status_code == 200
        assert own_task.title in response.text
        assert other_task.title not in response.text

    finally:
        db.close()        

def test_web_create_task_assigns_current_user():
    client.cookies.clear()

    response = client.get("/web/tasks")

    assert response.status_code == 200

    user_id = int(
        client.cookies.get("aura_user_id")
    )

    response = client.post(
        "/web/tasks/create",
        data={
            "title": "USER OWNED WEB TASK",
            "description": "Preparar presentación del proyecto",
            "estimated_minutes": 90,
            "priority": "alta",
            "effort": "alto",
            "focus_demand": "alto",
            "category": "trabajo",
            "workspace": "trabajo",
            "activity_type": "deep_work",
            "flexibility": "semi_flexible",
            "deadline": "2026-10-10T18:30",
            "preferred_date": "2026-10-05",
            "preferred_time_of_day": "tarde",
            "preferred_start_time": "15:30",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303

    db = SessionLocal()

    try:
        task = (
            db.query(TaskDB)
            .filter(
                TaskDB.title
                == "USER OWNED WEB TASK"
            )
            .order_by(TaskDB.id.desc())
            .first()
        )

        assert task is not None
        assert task.user_id == user_id
        assert task.description == "Preparar presentación del proyecto"
        assert task.estimated_minutes == 90
        assert task.effort == "alto"
        assert task.focus_demand == "alto"
        assert task.deadline.isoformat() == "2026-10-10T18:30:00"
        assert task.preferred_date.isoformat() == "2026-10-05"
        assert task.preferred_time_of_day == "tarde"
        assert task.preferred_start_time.strftime("%H:%M") == "15:30"
    finally:
        db.close()        

def test_web_edit_task_updates_planning_fields():
    client.cookies.clear()

    response = client.get("/web/tasks")

    assert response.status_code == 200

    user_id = int(
        client.cookies.get("aura_user_id")
    )

    db = SessionLocal()

    try:
        task_service = TaskService()

        task = task_service.create(
            db,
            Task(
                user_id=user_id,
                title="TASK TO EDIT",
                estimated_minutes=30,
            ),
        )

        task_id = task.id

    finally:
        db.close()

    response = client.post(
        f"/web/tasks/{task_id}/edit",
        data={
            "title": "TASK EDITED",
            "description": "Descripción actualizada",
            "estimated_minutes": 75,
            "priority": "alta",
            "effort": "alto",
            "focus_demand": "alto",
            "category": "trabajo",
            "workspace": "trabajo",
            "activity_type": "deep_work",
            "flexibility": "semi_flexible",
            "deadline": "2026-10-15T20:00",
            "preferred_date": "2026-10-06",
            "preferred_time_of_day": "tarde",
            "preferred_start_time": "16:00",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303

    db = SessionLocal()

    try:
        task = (
            db.query(TaskDB)
            .filter(TaskDB.id == task_id)
            .first()
        )

        assert task is not None
        assert task.title == "TASK EDITED"
        assert task.description == "Descripción actualizada"
        assert task.estimated_minutes == 75
        assert task.effort == "alto"
        assert task.focus_demand == "alto"
        assert task.deadline.isoformat() == "2026-10-15T20:00:00"
        assert task.preferred_date.isoformat() == "2026-10-06"
        assert task.preferred_time_of_day == "tarde"
        assert task.preferred_start_time.strftime("%H:%M") == "16:00"

    finally:
        db.close()        

def test_web_chat_persists_user_and_assistant_messages():
    client.cookies.clear()

    response = client.get("/web/chat")

    assert response.status_code == 200

    session_id = client.cookies.get(
        "aura_session_id"
    )

    user_id = int(
        client.cookies.get(
            "aura_user_id"
        )
    )

    response = client.post(
        "/web/chat",
        data={
            "message": "¿Qué debería hacer ahora?"
        },
    )

    assert response.status_code == 200

    db = SessionLocal()

    try:
        messages = (
            db.query(ConversationMessageDB)
            .filter(
                ConversationMessageDB.session_id
                == session_id,
                ConversationMessageDB.user_id
                == user_id,
            )
            .order_by(
                ConversationMessageDB.id.asc()
            )
            .all()
        )

        assert len(messages) == 2

        assert messages[0].role == "user"
        assert (
            messages[0].content
            == "¿Qué debería hacer ahora?"
        )

        assert messages[1].role == "assistant"
        assert messages[1].content

    finally:
        db.close()      

def test_web_chat_refresh_does_not_duplicate_messages():
    client.cookies.clear()

    response = client.get("/web/chat")

    assert response.status_code == 200

    session_id = client.cookies.get(
        "aura_session_id"
    )

    user_id = int(
        client.cookies.get(
            "aura_user_id"
        )
    )

    response = client.post(
        "/web/chat",
        data={
            "message": "Mensaje único para refresh"
        },
    )

    assert response.status_code == 200

    response = client.get("/web/chat")

    assert response.status_code == 200

    db = SessionLocal()

    try:
        messages = (
            db.query(ConversationMessageDB)
            .filter(
                ConversationMessageDB.session_id
                == session_id,
                ConversationMessageDB.user_id
                == user_id,
            )
            .order_by(
                ConversationMessageDB.id.asc()
            )
            .all()
        )

        assert len(messages) == 2

        assert messages[0].role == "user"
        assert (
            messages[0].content
            == "Mensaje único para refresh"
        )

        assert messages[1].role == "assistant"

    finally:
        db.close()          

def test_web_home_can_complete_scheduled_task():
    client.cookies.clear()

    response = client.get("/web")
    assert response.status_code == 200

    user_id = int(client.cookies.get("aura_user_id"))

    db = SessionLocal()

    try:
        task = TaskService().create(
            db,
            Task(
                user_id=user_id,
                title="Tarea dashboard completar test",
                estimated_minutes=15,
            ),
        )
        task_id = task.id
    finally:
        db.close()

    response = client.get("/web")

    assert response.status_code == 200
    assert "Tarea dashboard completar test" in response.text

    assert (
        f'/web/tasks/{task_id}/complete'
        in response.text
    )       

def test_web_cannot_mark_other_user_notification_as_read():
    client.cookies.clear()

    response = client.get("/web")
    assert response.status_code == 200

    current_user_id = int(
        client.cookies.get("aura_user_id")
    )

    from app.models.notification import (
        Notification,
        NotificationStatus,
    )
    from app.models.notification_db import NotificationDB
    from app.repositories.notification_repository import (
        NotificationRepository,
    )
    from app.services.user_service import UserService

    db = SessionLocal()

    try:
        other_user = UserService().create_user(db)

        assert other_user.id != current_user_id

        notification = NotificationRepository().create(
            db,
            Notification(
                user_id=other_user.id,
                title="Notificación de otro usuario",
                message="No debe poder modificarse.",
            ),
        )

        notification_id = notification.id

    finally:
        db.close()

    response = client.post(
        f"/web/notifications/{notification_id}/read",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/web"

    db = SessionLocal()

    try:
        stored_notification = (
            db.query(NotificationDB)
            .filter(
                NotificationDB.id
                == notification_id
            )
            .first()
        )

        assert stored_notification is not None
        assert (
            stored_notification.status
            == NotificationStatus.PENDING.value
        )
        assert stored_notification.read_at is None

    finally:
        db.close()     