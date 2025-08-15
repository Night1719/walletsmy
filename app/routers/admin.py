from typing import Optional
from fastapi import APIRouter, Depends, Form, Request, HTTPException
from starlette.responses import RedirectResponse
from starlette import status
from sqlalchemy.orm import Session
from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES

from ..database import get_db
from ..models import User
from ..auth import hash_password, require_roles
from ..config import settings

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("")
async def admin_dashboard(request: Request, current_user: User = Depends(require_roles(["admin"]))):
    return request.app.state.templates.TemplateResponse("admin/dashboard.html", {"request": request, "title": "Админ панель"})


@router.get("/users")
async def users_list(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_roles(["admin"]))):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return request.app.state.templates.TemplateResponse("admin/users.html", {"request": request, "users": users, "title": "Пользователи"})


@router.get("/users/new")
async def user_new_form(request: Request, current_user: User = Depends(require_roles(["admin"]))):
    return request.app.state.templates.TemplateResponse("admin/user_form.html", {"request": request, "title": "Новый пользователь"})


@router.post("/users/new")
async def user_new(
    request: Request,
    username: str = Form(...),
    email: Optional[str] = Form(None),
    password: str = Form(...),
    role: str = Form("user"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    if db.query(User).filter(User.username == username).first():
        return request.app.state.templates.TemplateResponse(
            "admin/user_form.html", {"request": request, "error": "Пользователь уже существует"}, status_code=status.HTTP_400_BAD_REQUEST
        )
    user = User(username=username, email=email, password_hash=hash_password(password), role=role)
    db.add(user)
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=status.HTTP_302_FOUND)


@router.get("/users/{user_id}/edit")
async def user_edit_form(user_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_roles(["admin"]))):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404)
    return request.app.state.templates.TemplateResponse("admin/user_form.html", {"request": request, "user": user, "title": "Редактировать пользователя"})


@router.post("/users/{user_id}/edit")
async def user_edit(
    user_id: int,
    request: Request,
    email: Optional[str] = Form(None),
    role: str = Form("user"),
    is_active: Optional[str] = Form(None),
    new_password: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404)
    user.email = email
    user.role = role
    user.is_active = bool(is_active)
    if new_password:
        user.password_hash = hash_password(new_password)
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=status.HTTP_302_FOUND)


@router.post("/users/{user_id}/delete")
async def user_delete(user_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_roles(["admin"]))):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404)
    db.delete(user)
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=status.HTTP_302_FOUND)


@router.get("/ldap/import")
async def ldap_import_form(request: Request, current_user: User = Depends(require_roles(["admin"]))):
    return request.app.state.templates.TemplateResponse("admin/ldap_import.html", {"request": request, "title": "Импорт из LDAP"})


@router.post("/ldap/import")
async def ldap_import(
    request: Request,
    base_dn: Optional[str] = Form(None),
    search_filter: str = Form(settings.LDAP_USER_FILTER),
    username_attr: str = Form(settings.LDAP_USERNAME_ATTRIBUTE),
    email_attr: str = Form(settings.LDAP_EMAIL_ATTRIBUTE),
    default_role: str = Form("user"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    server_uri = settings.LDAP_SERVER_URI
    bind_dn = settings.LDAP_BIND_DN
    bind_password = settings.LDAP_BIND_PASSWORD
    base = base_dn or settings.LDAP_BASE_DN

    if not (server_uri and bind_dn and bind_password and base):
        return request.app.state.templates.TemplateResponse(
            "admin/ldap_import.html",
            {"request": request, "error": "LDAP настройки не заданы. Укажите параметры в .env"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    server = Server(server_uri, get_info=ALL)
    conn = Connection(server, user=bind_dn, password=bind_password, auto_bind=True)
    conn.search(search_base=base, search_filter=search_filter, attributes=ALL_ATTRIBUTES)
    created = 0
    for entry in conn.entries:
        username = str(entry[username_attr]) if username_attr in entry else None
        email = str(entry[email_attr]) if email_attr in entry else None
        if not username:
            continue
        if not db.query(User).filter(User.username == username).first():
            # Generate a random password; user should change later
            from secrets import token_urlsafe

            tmp_password = token_urlsafe(12)
            user = User(username=username, email=email, password_hash=hash_password(tmp_password), role=default_role)
            db.add(user)
            created += 1
    db.commit()

    return request.app.state.templates.TemplateResponse(
        "admin/ldap_import.html", {"request": request, "message": f"Импортировано пользователей: {created}"}
    )