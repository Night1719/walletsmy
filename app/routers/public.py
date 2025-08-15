from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Survey

router = APIRouter()


@router.get("/s/{token}")
async def take_survey_token(token: str, request: Request, db: Session = Depends(get_db)):
    survey = db.query(Survey).filter(Survey.share_token == token).first()
    if not survey or not survey.is_active:
        raise HTTPException(status_code=404)
    return request.app.state.templates.TemplateResponse("surveys/take.html", {"request": request, "survey": survey, "title": survey.title})