from sqlalchemy.orm import Session
from app.models.role import Role


def get_by_name(db: Session, name: str) -> Role | None:
    return db.query(Role).filter(Role.name == name).first()
