from uuid import UUID

from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog


def create_log(
    db: Session,
    actor_id: UUID | None,
    action: str,
    entity_type: str,
    entity_id: UUID | None,
    details: str = "",
):
    log = ActivityLog(
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )
    db.add(log)
    db.commit()
    return log
