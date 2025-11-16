from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional

from app.models.meeting import MeetingPurpose
from app.schemas.user import UserResponse


class MeetingBase(BaseModel):
    """약속 기본 스키마"""
    title: str
    description: Optional[str] = None
    purpose: MeetingPurpose


class MeetingCreate(MeetingBase):
    """약속 생성 스키마"""
    pass


class MeetingUpdate(BaseModel):
    """약속 업데이트 스키마"""
    title: Optional[str] = None
    description: Optional[str] = None
    purpose: Optional[MeetingPurpose] = None
    is_confirmed: Optional[bool] = None
    confirmed_at: Optional[datetime] = None
    confirmed_location: Optional[str] = None


class MeetingResponse(MeetingBase):
    """약속 응답 스키마"""
    id: UUID
    creator_id: int
    is_confirmed: bool
    confirmed_at: Optional[datetime] = None
    confirmed_location: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    creator: Optional[UserResponse] = None

    class Config:
        from_attributes = True

