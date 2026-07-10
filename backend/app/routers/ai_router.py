from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import require_manager_or_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.ai_schema import GenerateTeamInsightsRequest, TeamInsightsResponse
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.ai_service import AIService
from app.services.chat_service import ChatService


router = APIRouter(prefix="/ai", tags=["AI Team Intelligence"])


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    return ChatService.answer(db=db, current_user=current_user, payload=payload)


@router.post("/team-insights", response_model=TeamInsightsResponse)
def generate_team_insights(
    payload: GenerateTeamInsightsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    try:
        return AIService.generate_team_insights(
            db=db,
            current_user=current_user,
            week_start=payload.week_start,
            week_end=payload.week_end,
            project_id=payload.project_id,
            member_id=payload.member_id,
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
