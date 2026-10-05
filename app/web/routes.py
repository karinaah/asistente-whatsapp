from datetime import date, datetime, time
from uuid import uuid4


from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config.dependencies import get_db
from app.config.service_dependencies import (
    get_planning_workflow_service,
    get_task_service,
)
from app.services.planning_workflow_service import (
    PlanningWorkflowService,
)
from app.models.schedule import PlanningFromDBRequest
from app.services.task_service import TaskService
from app.models.task import Task, TaskUpdate
from app.models.assistant_chat import AssistantChatRequest
from app.services.assistant_chat_service import AssistantChatService
from app.services.user_service import UserService
from app.services.notification_service import NotificationService
from app.services.routine_service import RoutineService
from app.models.routine import Routine, Weekday
from app.services.recurring_availability_service import (
    RecurringAvailabilityService,
)
from app.models.recurring_availability import (
    RecurringAvailability,
)
from app.repositories.conversation_message_repository import (
    ConversationMessageRepository,
)

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")
assistant_chat_service = AssistantChatService()
user_service = UserService()
notification_service = NotificationService()
routine_service = RoutineService()
recurring_availability_service = (
    RecurringAvailabilityService()
)
conversation_message_repository = ConversationMessageRepository()

def get_or_create_web_user_id(
    request: Request,
    db: Session,
) -> str:
    user_id = request.cookies.get(
        "aura_user_id",
    )

    if user_id is not None:
        try:
            user = user_service.get_user(
                db,
                user_id=int(user_id),
            )
        except ValueError:
            user = None

        if user is not None:
            return str(user.id)

    user = user_service.create_user(db)

    return str(user.id)

@router.get("/web")
def home(
    request: Request,
    db: Session = Depends(get_db),
    planning_workflow_service: PlanningWorkflowService = Depends(
        get_planning_workflow_service
    ),
):
    today = date.today()

    user_id = get_or_create_web_user_id(
        request=request,
        db=db,
    )

    planning_request = PlanningFromDBRequest()

    plan = planning_workflow_service.create_plan_from_db(
        db=db,
        request=planning_request,
        user_id=int(user_id),
    )
    scheduled_task_ids = {
        (
            item.start_time,
            item.end_time,
        ): item.task.id
        for item in plan.scheduled_tasks
    }

    notifications = notification_service.get_pending_for_user(
        db=db,
        user_id=int(user_id),
    )
    response = templates.TemplateResponse(
        request=request,
        name="today.html",
        context={
            "today": today,
            "plan": plan,
            "notifications": notifications,
            "scheduled_task_ids": scheduled_task_ids,
        },
    )

    response.set_cookie(
        key="aura_user_id",
        value=user_id,
        httponly=True,
        samesite="lax",
    )

    return response

@router.post("/web/tasks/{task_id}/complete")
def complete_task(
    task_id: int,
    request: Request,
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
):
    user_id = request.cookies.get(
        "aura_user_id",
    )

    if user_id is None:
        return RedirectResponse(
            url="/web",
            status_code=303,
        )

    task_service.mark_completed(
        db=db,
        task_id=task_id,
        user_id=int(user_id),
    )

    return RedirectResponse(
        url="/web",
        status_code=303,
    )

@router.get("/web/tasks")
def tasks_page(
    request: Request,
    workspace: str | None = None,
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
):
    user_id = get_or_create_web_user_id(
        request=request,
        db=db,
    )
    tasks = task_service.get_for_user(
        db=db,
        user_id=int(user_id),
    )

    if workspace in {"trabajo", "personal"}:
        tasks = [
            task
            for task in tasks
            if task.workspace.value == workspace
        ]

    response = templates.TemplateResponse(
        request=request,
        name="tasks.html",
        context={
            "tasks": tasks,
            "selected_workspace": workspace,
        },
    )

    response.set_cookie(
        key="aura_user_id",
        value=user_id,
        httponly=True,
        samesite="lax",
    )

    return response

@router.post("/web/tasks/{task_id}/delete")
def delete_task(
    task_id: int,
    request: Request,
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
):
    user_id = request.cookies.get(
        "aura_user_id",
    )

    if user_id is None:
        return RedirectResponse(
            url="/web/tasks",
            status_code=303,
        )

    task_service.delete(
        db=db,
        task_id=task_id,
        user_id=int(user_id),
    )

    return RedirectResponse(
        url="/web/tasks",
        status_code=303,
    )


@router.post("/web/tasks/create")
def create_task_from_web(
    request: Request,
    title: str = Form(...),
    estimated_minutes: int = Form(...),
    priority: str = Form("media"),
    category: str = Form("otro"),
    workspace: str = Form("personal"),
    activity_type: str = Form("other"),
    flexibility: str = Form("flexible"),
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
    description: str = Form(""),
    effort: str = Form("medio"),
    focus_demand: str = Form("medio"),
    preferred_date: str = Form(""),
    deadline: str = Form(""),
    preferred_time_of_day: str = Form(""),
    preferred_start_time: str = Form(""),
):
    user_id = get_or_create_web_user_id(
        request=request,
        db=db,
    )

    task = Task(
        user_id=int(user_id),
        title=title,
        estimated_minutes=estimated_minutes,
        priority=priority,
        category=category,
        workspace=workspace,
        activity_type=activity_type,
        flexibility=flexibility,
        description=description or None,
        effort=effort,
        focus_demand=focus_demand,

        deadline=(
            datetime.fromisoformat(deadline)
            if deadline
            else None
        ),        
        preferred_date=(
            date.fromisoformat(preferred_date)
            if preferred_date
            else None
        ),
        preferred_time_of_day=(
            preferred_time_of_day
            if preferred_time_of_day
            else None
        ),
        preferred_start_time=(
            time.fromisoformat(preferred_start_time)
            if preferred_start_time
            else None
        ),        
    )    

    task_service.create(
        db=db,
        task=task,
    )

    return RedirectResponse(
        url="/web/tasks",
        status_code=303,
    )

@router.post("/web/tasks/{task_id}/edit")
def edit_task_from_web(
    task_id: int,
    request: Request,
    title: str = Form(...),
    estimated_minutes: int = Form(...),
    priority: str = Form(...),
    category: str = Form(...),
    workspace: str = Form(...),
    activity_type: str = Form(...),
    flexibility: str = Form(...),
    description: str = Form(""),
    effort: str = Form("medio"),
    focus_demand: str = Form("medio"),
    preferred_date: str = Form(""),
    deadline: str = Form(""),
    preferred_time_of_day: str = Form(""),
    preferred_start_time: str = Form(""),
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
):
    user_id = request.cookies.get(
        "aura_user_id",
    )

    if user_id is None:
        return RedirectResponse(
            url="/web/tasks",
            status_code=303,
        )

    task_update = TaskUpdate(
        title=title,
        estimated_minutes=estimated_minutes,
        priority=priority,
        category=category,
        workspace=workspace,
        activity_type=activity_type,
        flexibility=flexibility,
        description=description or None,
        effort=effort,
        focus_demand=focus_demand,
        deadline=(
            datetime.fromisoformat(deadline)
            if deadline
            else None
        ),

        preferred_date=(
            date.fromisoformat(preferred_date)
            if preferred_date
            else None
        ),
        preferred_time_of_day=(
            preferred_time_of_day
            if preferred_time_of_day
            else None
        ),
        preferred_start_time=(
            time.fromisoformat(preferred_start_time)
            if preferred_start_time
            else None
        ),

    )

    task_service.update(
        db=db,
        task_id=task_id,
        request=task_update,
        user_id=int(user_id),
    )

    return RedirectResponse(
        url="/web/tasks",
        status_code=303,
    )

@router.get("/web/routines")
def routines_page(
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = get_or_create_web_user_id(
        request=request,
        db=db,
    )

    routines = routine_service.get_for_user(
        db=db,
        user_id=int(user_id),
    )

    response = templates.TemplateResponse(
        request=request,
        name="routines.html",
        context={
            "routines": routines,
        },
    )

    response.set_cookie(
        key="aura_user_id",
        value=user_id,
        httponly=True,
        samesite="lax",
    )

    return response

@router.post("/web/routines/create")
def create_routine_from_web(
    request: Request,
    title: str = Form(...),
    weekdays: list[int] = Form(...),
    preferred_start_time: str = Form(""),
    estimated_minutes: int = Form(...),
    category: str = Form("otro"),
    workspace: str = Form("personal"),
    db: Session = Depends(get_db),
):
    user_id = get_or_create_web_user_id(
        request=request,
        db=db,
    )

    parsed_start_time = None

    if preferred_start_time:
        hour, minute = preferred_start_time.split(":")

        parsed_start_time = time(
            hour=int(hour),
            minute=int(minute),
        )

    routine = Routine(
        user_id=int(user_id),
        title=title,
        weekdays=[
            Weekday(weekday)
            for weekday in weekdays
        ],
        preferred_start_time=parsed_start_time,
        estimated_minutes=estimated_minutes,
        category=category,
        workspace=workspace,
    )

    routine_service.create(
        db=db,
        routine=routine,
    )

    return RedirectResponse(
        url="/web/routines",
        status_code=303,
    )

@router.post("/web/routines/{routine_id}/deactivate")
def deactivate_routine_from_web(
    routine_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = request.cookies.get(
        "aura_user_id",
    )

    if user_id is None:
        return RedirectResponse(
            url="/web/routines",
            status_code=303,
        )

    routine_service.set_active(
        db=db,
        routine_id=routine_id,
        user_id=int(user_id),
        active=False,
    )

    return RedirectResponse(
        url="/web/routines",
        status_code=303,
    )

@router.post("/web/routines/{routine_id}/activate")
def activate_routine_from_web(
    routine_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = request.cookies.get(
        "aura_user_id",
    )

    if user_id is None:
        return RedirectResponse(
            url="/web/routines",
            status_code=303,
        )

    routine_service.set_active(
        db=db,
        routine_id=routine_id,
        user_id=int(user_id),
        active=True,
    )

    return RedirectResponse(
        url="/web/routines",
        status_code=303,
    )

@router.get("/web/chat")
def chat_page(
    request: Request,
    db: Session = Depends(get_db),
):
    session_id = request.cookies.get(
        "aura_session_id",
    )

    if session_id is None:
        session_id = str(uuid4())

    user_id = get_or_create_web_user_id(
        request=request,
        db=db,
    )

    messages = conversation_message_repository.get_by_session(
        db=db,
        session_id=session_id,
        user_id=int(user_id),
    )

    response = templates.TemplateResponse(
        request=request,
        name="chat.html",
        context={
            "messages": messages,
        },
    )

    response.set_cookie(
        key="aura_session_id",
        value=session_id,
        httponly=True,
        samesite="lax",
    )

    response.set_cookie(
        key="aura_user_id",
        value=user_id,
        httponly=True,
        samesite="lax",
    )

    return response


@router.post("/web/chat")
def chat_message(
    request: Request,
    message: str = Form(...),
    db: Session = Depends(get_db),
):

    session_id = request.cookies.get(
        "aura_session_id",
        "default",
    )

    user_id = request.cookies.get(
        "aura_user_id",
    )

    chat_request = AssistantChatRequest(
        message=message,
        session_id=session_id,
        user_id=(
            int(user_id)
            if user_id is not None
            else None
        ),
    )

    conversation_message_repository.add(
        db=db,
        session_id=session_id,
        user_id=(
            int(user_id)
            if user_id is not None
            else None
        ),
        role="user",
        content=message,
    )

    response = assistant_chat_service.chat(
        db=db,
        request=chat_request,
    )

    conversation_message_repository.add(
        db=db,
        session_id=session_id,
        user_id=(
            int(user_id)
            if user_id is not None
            else None
        ),
        role="assistant",
        content=response.answer,
    )

    return RedirectResponse(
        url="/web/chat",
        status_code=303,
    )

@router.post("/web/notifications/{notification_id}/read")
def read_notification(
    notification_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = request.cookies.get(
        "aura_user_id",
    )

    if user_id is not None:
        notification_service.mark_read(
            db=db,
            notification_id=notification_id,
            user_id=int(user_id),
        )

    return RedirectResponse(
        url="/web",
        status_code=303,
    )

@router.get("/web/availability")
def availability_page(
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = get_or_create_web_user_id(
        request=request,
        db=db,
    )

    availabilities = (
        recurring_availability_service.get_for_user(
            db,
            user_id=int(user_id),
        )
    )

    response = templates.TemplateResponse(
        request=request,
        name="availability.html",
        context={
            "availabilities": availabilities,
        },
    )

    response.set_cookie(
        key="aura_user_id",
        value=user_id,
        httponly=True,
        samesite="lax",
    )

    return response

@router.post("/web/availability/create")
def create_availability_from_web(
    request: Request,
    weekday: int = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    db: Session = Depends(get_db),
):
    user_id = get_or_create_web_user_id(
        request=request,
        db=db,
    )

    start_hour, start_minute = map(
        int,
        start_time.split(":"),
    )
    end_hour, end_minute = map(
        int,
        end_time.split(":"),
    )

    recurring_availability_service.create(
        db,
        RecurringAvailability(
            user_id=int(user_id),
            weekday=Weekday(weekday),
            start_time=time(
                start_hour,
                start_minute,
            ),
            end_time=time(
                end_hour,
                end_minute,
            ),
        ),
    )

    response = RedirectResponse(
        url="/web/availability",
        status_code=303,
    )

    response.set_cookie(
        key="aura_user_id",
        value=user_id,
        httponly=True,
        samesite="lax",
    )

    return response

@router.post(
    "/web/availability/{availability_id}/deactivate"
)
def deactivate_availability_from_web(
    availability_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = request.cookies.get(
        "aura_user_id",
    )

    if user_id is None:
        return RedirectResponse(
            url="/web/availability",
            status_code=303,
        )

    recurring_availability_service.set_active(
        db=db,
        availability_id=availability_id,
        user_id=int(user_id),
        active=False,
    )

    return RedirectResponse(
        url="/web/availability",
        status_code=303,
    )


@router.post(
    "/web/availability/{availability_id}/activate"
)
def activate_availability_from_web(
    availability_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = request.cookies.get(
        "aura_user_id",
    )

    if user_id is None:
        return RedirectResponse(
            url="/web/availability",
            status_code=303,
        )

    recurring_availability_service.set_active(
        db=db,
        availability_id=availability_id,
        user_id=int(user_id),
        active=True,
    )

    return RedirectResponse(
        url="/web/availability",
        status_code=303,
    )