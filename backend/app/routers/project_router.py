from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import require_manager_or_admin
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.schemas.common_schema import MessageResponse
from app.schemas.project_schema import ProjectCreate, ProjectOut, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return ProjectService.list_projects(db)


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db), _=Depends(require_manager_or_admin)):
    return ProjectService.create_project(db, payload)


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(project_id: UUID, payload: ProjectUpdate, db: Session = Depends(get_db), _=Depends(require_manager_or_admin)):
    try:
        return ProjectService.update_project(db, project_id, payload)
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


@router.delete("/{project_id}", response_model=MessageResponse)
def archive_project(project_id: UUID, db: Session = Depends(get_db), _=Depends(require_manager_or_admin)):
    try:
        ProjectService.archive_project(db, project_id)
        return {"message": "Project archived"}
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
