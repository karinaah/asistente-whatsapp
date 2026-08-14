from datetime import date

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/web")
def home(request: Request):
    today = date.today()

    return templates.TemplateResponse(
        request=request,
        name="today.html",
        context={
            "today": today,
        },
    )