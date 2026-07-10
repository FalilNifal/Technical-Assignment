import uuid

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.db.database import Base


class AISummary(Base):
    __tablename__ = "ai_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    generated_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    week_start = Column(Date, nullable=False)
    week_end = Column(Date, nullable=False)

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
    )

    member_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    prompt = Column(Text, nullable=False)
    response = Column(JSONB, nullable=False)

    model_name = Column(String(100), nullable=True)
    reports_used_count = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
