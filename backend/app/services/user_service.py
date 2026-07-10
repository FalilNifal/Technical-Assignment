from sqlalchemy.orm import Session
from app.repositories.user_repository import list_users


def all_users(db: Session):
    return list_users(db)
