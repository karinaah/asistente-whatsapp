from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config.dependencies import get_db
from app.services.user_service import UserService
from fastapi import Response
from app.services.auth_session_service import AuthSessionService
from app.config.auth_dependencies import AUTH_COOKIE_NAME
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from app.config.settings import settings

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)
templates = Jinja2Templates(directory="app/templates")

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str | None = None


class RegisterResponse(BaseModel):
    id: int
    email: str
    name: str | None = None

class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    message: str
    user_id: int

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "error": None,
        },
    )

@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "error": None,
        },
    )

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    service = UserService()

    try:
        user = service.register_user(
            db=db,
            email=request.email,
            password=request.password,
            name=request.name,
        )
    except ValueError as exc:
        message = str(exc)

        if "registrado" in message.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=message,
        ) from exc

    return RegisterResponse(
        id=user.id,
        email=user.email,
        name=user.name,
    )

@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    request: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    user_service = UserService()

    user = user_service.authenticate_user(
        db=db,
        email=request.email,
        password=request.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
        )

    session_service = AuthSessionService()

    token, auth_session = session_service.create_session(
        db=db,
        user_id=user.id,
    )

    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=session_service.SESSION_DURATION_DAYS * 24 * 60 * 60,
        path="/",
    )

    return LoginResponse(
        message="Inicio de sesión exitoso",
        user_id=user.id,
    )


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    token = request.cookies.get(AUTH_COOKIE_NAME)

    if token:
        session_service = AuthSessionService()

        session_service.revoke_session(
            db=db,
            token=token,
        )

    response.delete_cookie(
        key=AUTH_COOKIE_NAME,
        path="/",
        secure=settings.cookie_secure,
        httponly=True,
        samesite="lax",
    )

    return {
        "message": "Sesión cerrada correctamente",
    }

@router.post("/login/form")
def login_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = UserService().authenticate_user(
        db=db,
        email=email,
        password=password,
    )

    if user is None:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error": "Correo o contraseña incorrectos",
            },
            status_code=401,
        )

    session_service = AuthSessionService()

    token, _ = session_service.create_session(
        db=db,
        user_id=user.id,
    )

    response = RedirectResponse(
        url="/web",
        status_code=303,
    )

    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=session_service.SESSION_DURATION_DAYS * 24 * 60 * 60,
        path="/",
    )

    return response

@router.post("/register/form")
def register_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    name: str | None = Form(None),
    db: Session = Depends(get_db),
):
    try:
        UserService().register_user(
            db=db,
            email=email,
            password=password,
            name=name or None,
        )

    except ValueError as exc:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "error": str(exc),
            },
            status_code=400,
        )

    return RedirectResponse(
        url="/auth/login",
        status_code=303,
    )