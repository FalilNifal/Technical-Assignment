from sqlalchemy.orm import Session
from app.models.ai_summary import AiSummary


def save_summary(db: Session, summary: AiSummary) -> AiSummary:
    db.add(summary)
    db.commit()
    db.refresh(summary)
    return summary
