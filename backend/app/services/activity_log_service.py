from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.activity_log_repository import create_log


def record(
    db: Session,
    actor_id: UUID | None,
    action: str,
    entity_type: str,
    entity_id: UUID | None,
    details: str = "",
):
    return create_log(db, actor_id, action, entity_type, entity_id, details)
