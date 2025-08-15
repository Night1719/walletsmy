from fastapi import APIRouter, Depends, Form, Request
from starlette.responses import RedirectResponse
from starlette import status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..auth import verify_password

router = APIRouter()


@router.get("/login")
async def login_form(request: Request):
    return request.app.state.templates.TemplateResponse("login.html", {"request": request, "title": "Вход"})


@router.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.is_active or not verify_password(password, user.password_hash):
        return request.app.state.templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Неверный логин или пароль"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    request.session["user_id"] = user.id
    return RedirectResponse(url="/surveys", status_code=status.HTTP_302_FOUND)


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)