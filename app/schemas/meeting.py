from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional

from app.schemas.user import UserResponse


class MeetingBase(BaseModel):
    """약속 기본 스키마"""
    title: str
    description: Optional[str] = None


class MeetingCreate(MeetingBase):
    """약속 생성 스키마"""
    pass


class MeetingUpdate(BaseModel):
    """약속 업데이트 스키마"""
    title: Optional[str] = None
    description: Optional[str] = None
    is_confirmed: Optional[bool] = None
    confirmed_datetime: Optional[datetime] = None


class MeetingResponse(MeetingBase):
    """약속 응답 스키마"""
    id: UUID
    creator_id: UUID
    share_code: str
    is_confirmed: bool
    confirmed_datetime: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    creator: Optional[UserResponse] = None

    class Config:
        from_attributes = True

