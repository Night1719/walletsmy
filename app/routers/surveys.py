from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Form, Request, HTTPException
from starlette.responses import RedirectResponse
from starlette import status
from sqlalchemy.orm import Session
from sqlalchemy import func
from slugify import slugify

from ..database import get_db
from ..models import User, Survey, Question, Option, Response, Answer
from ..auth import require_login, require_roles, get_current_user
from ..utils import extract_internal_ip
from ..config import settings

router = APIRouter(prefix="/surveys", tags=["surveys"])


@router.get("")
async def surveys_list(request: Request, db: Session = Depends(get_db), current_user: Optional[User] = Depends(require_login)):
    if current_user.role in ("admin", "creator"):
        surveys = db.query(Survey).filter((Survey.owner_id == current_user.id) | (Survey.is_active == True)).order_by(Survey.created_at.desc()).all()
    else:
        surveys = db.query(Survey).filter(Survey.is_active == True).order_by(Survey.created_at.desc()).all()
    return request.app.state.templates.TemplateResponse("surveys/list.html", {"request": request, "surveys": surveys, "current_user": current_user})


@router.get("/new")
async def survey_new_form(request: Request, current_user: User = Depends(require_roles(["admin", "creator"]))):
    return request.app.state.templates.TemplateResponse("surveys/form.html", {"request": request, "title": "Новый опрос"})


@router.post("/new")
async def survey_new(
    request: Request,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    is_anonymous: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "creator"]))
):
    survey = Survey(owner_id=current_user.id, title=title.strip(), description=description, is_anonymous=bool(is_anonymous))
    db.add(survey)
    db.commit()
    return RedirectResponse(url=f"/surveys/{survey.id}/edit", status_code=status.HTTP_302_FOUND)


@router.get("/{survey_id}/edit")
async def survey_edit_form(survey_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_roles(["admin", "creator"]))):
    survey = db.get(Survey, survey_id)
    if not survey or (survey.owner_id != current_user.id and current_user.role != "admin"):
        raise HTTPException(status_code=404)
    return request.app.state.templates.TemplateResponse("surveys/form.html", {"request": request, "survey": survey, "title": "Редактировать опрос"})


@router.post("/{survey_id}/edit")
async def survey_edit(
    survey_id: int,
    request: Request,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    is_anonymous: Optional[str] = Form(None),
    questions_payload: str = Form("[]"),  # JSON from front-end
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "creator"]))
):
    import json

    survey = db.get(Survey, survey_id)
    if not survey or (survey.owner_id != current_user.id and current_user.role != "admin"):
        raise HTTPException(status_code=404)

    survey.title = title.strip()
    survey.description = description
    survey.is_anonymous = bool(is_anonymous)

    # Replace questions/options based on payload
    data = json.loads(questions_payload)
    # Clear existing
    survey.questions.clear()
    db.flush()

    for idx, q in enumerate(data):
        question = Question(survey=survey, text=q.get("text", "").strip(), qtype=q.get("qtype", "single"), order_index=idx)
        if question.qtype in ("single", "multiple"):
            for oidx, opt in enumerate(q.get("options", [])):
                option = Option(question=question, text=str(opt).strip(), order_index=oidx)
        db.add(question)

    db.commit()
    return RedirectResponse(url=f"/surveys/{survey.id}/edit", status_code=status.HTTP_302_FOUND)


@router.get("/{survey_id}/share")
async def survey_share(survey_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_roles(["admin", "creator"]))):
    from secrets import token_urlsafe

    survey = db.get(Survey, survey_id)
    if not survey or (survey.owner_id != current_user.id and current_user.role != "admin"):
        raise HTTPException(status_code=404)
    if not survey.share_token:
        survey.share_token = token_urlsafe(16)
        db.commit()
    public_url = settings.PUBLIC_URL or ""
    share_url = f"{public_url}/s/{survey.share_token}" if public_url else f"/s/{survey.share_token}"
    return request.app.state.templates.TemplateResponse("surveys/share.html", {"request": request, "survey": survey, "share_url": share_url, "title": "Шеринг опроса"})


@router.get("/{survey_id}/analytics")
async def survey_analytics(survey_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_roles(["admin", "creator", "analyst"]))):
    survey = db.get(Survey, survey_id)
    if not survey or (survey.owner_id != current_user.id and current_user.role not in ("admin", "analyst")):
        raise HTTPException(status_code=404)

    total_responses = db.query(func.count(Response.id)).filter(Response.survey_id == survey_id).scalar() or 0

    q_stats: List[Dict[str, Any]] = []
    for q in survey.questions:
        if q.qtype in ("single", "multiple"):
            option_counts = (
                db.query(Option.id, Option.text, func.count(Answer.id))
                .outerjoin(Answer, (Answer.option_id == Option.id))
                .filter(Option.question_id == q.id)
                .group_by(Option.id)
                .order_by(Option.order_index)
                .all()
            )
            q_stats.append({
                "question": q,
                "type": q.qtype,
                "options": [{"id": oid, "text": text, "count": cnt} for oid, text, cnt in option_counts],
            })
        else:
            text_count = db.query(func.count(Answer.id)).filter(Answer.question_id == q.id).scalar() or 0
            q_stats.append({"question": q, "type": q.qtype, "text_count": text_count})

    return request.app.state.templates.TemplateResponse(
        "surveys/analytics.html",
        {"request": request, "survey": survey, "total_responses": total_responses, "q_stats": q_stats, "title": "Аналитика"},
    )


@router.get("/take/{survey_id}")
async def take_survey_authed(survey_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_login)):
    survey = db.get(Survey, survey_id)
    if not survey or not survey.is_active:
        raise HTTPException(status_code=404)
    return request.app.state.templates.TemplateResponse("surveys/take.html", {"request": request, "survey": survey, "title": survey.title})


@router.get("/s/{token}")
async def take_survey_token(token: str, request: Request, db: Session = Depends(get_db)):
    survey = db.query(Survey).filter(Survey.share_token == token).first()
    if not survey or not survey.is_active:
        raise HTTPException(status_code=404)
    return request.app.state.templates.TemplateResponse("surveys/take.html", {"request": request, "survey": survey, "title": survey.title})


@router.post("/submit/{survey_id}")
async def submit_survey(
    survey_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    from fastapi import Form

    survey = db.get(Survey, survey_id)
    if not survey or not survey.is_active:
        raise HTTPException(status_code=404)

    # Enforce auth when survey is not anonymous and no token route used
    # For simplicity we allow both anonymous and authed if is_anonymous True, otherwise require auth
    if not survey.is_anonymous and not current_user:
        return RedirectResponse(url=f"/login?next=/surveys/take/{survey_id}", status_code=status.HTTP_302_FOUND)

    # Collect answers from form
    response = Response(
        survey_id=survey.id,
        respondent_user_id=current_user.id if (current_user and not survey.is_anonymous) else None,
        ip_address=extract_internal_ip(
            request.headers.get("X-Forwarded-For"), request.headers.get("X-Real-IP")
        ),
        user_agent=request.headers.get("User-Agent"),
    )
    db.add(response)
    db.flush()

    form = await request.form()

    for q in survey.questions:
        key = f"q_{q.id}"
        if q.qtype == "text":
            text_value = form.get(key)
            if text_value:
                db.add(Answer(response_id=response.id, question_id=q.id, text_answer=str(text_value)))
        elif q.qtype == "single":
            opt_id = form.get(key)
            if opt_id:
                db.add(Answer(response_id=response.id, question_id=q.id, option_id=int(opt_id)))
        elif q.qtype == "multiple":
            opt_ids = form.getlist(key)
            for oid in opt_ids:
                db.add(Answer(response_id=response.id, question_id=q.id, option_id=int(oid)))

    db.commit()

    return request.app.state.templates.TemplateResponse(
        "surveys/thankyou.html", {"request": request, "survey": survey, "title": "Спасибо!"}
    )