from uuid import UUID

from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project_schema import ProjectCreate, ProjectUpdate


class ProjectService:
    @staticmethod
    def list_projects(db: Session) -> list[Project]:
        return db.query(Project).filter(Project.is_active.is_(True)).order_by(Project.name.asc()).all()

    @staticmethod
    def create_project(db: Session, payload: ProjectCreate) -> Project:
        project = Project(**payload.model_dump())
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def update_project(db: Session, project_id: UUID, payload: ProjectUpdate) -> Project:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise LookupError("Project not found")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(project, key, value)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def archive_project(db: Session, project_id: UUID) -> None:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise LookupError("Project not found")
        project.is_active = False
        db.commit()
