from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    role: str
    avatar_url: str | None = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
