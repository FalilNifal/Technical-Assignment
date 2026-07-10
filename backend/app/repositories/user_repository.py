from sqlalchemy.orm import Session
from app.models.user import User


def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def list_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.name).all()


def list_members(db: Session) -> list[User]:
    return db.query(User).join(User.role).filter_by(name="TEAM_MEMBER").order_by(User.name).all()
