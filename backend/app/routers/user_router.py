from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import require_manager
from app.db.session import get_db
from app.schemas.user_schema import UserOut
from app.services.user_service import all_users

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
def users(db: Session = Depends(get_db), _=Depends(require_manager)):
    return all_users(db)
