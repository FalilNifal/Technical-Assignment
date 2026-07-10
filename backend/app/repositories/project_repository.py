from sqlalchemy.orm import Session
from app.models.project import Project


def list_projects(db: Session) -> list[Project]:
    return db.query(Project).order_by(Project.name).all()


def get_project(db: Session, project_id: int) -> Project | None:
    return db.get(Project, project_id)
