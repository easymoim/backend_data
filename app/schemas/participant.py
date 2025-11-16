from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional


class ParticipantBase(BaseModel):
    """참가자 기본 스키마"""
    location: Optional[str] = None


class ParticipantCreate(ParticipantBase):
    """참가자 생성 스키마"""
    meeting_id: UUID
    user_id: Optional[int] = None


class ParticipantUpdate(BaseModel):
    """참가자 업데이트 스키마"""
    location: Optional[str] = None
    has_responded: Optional[bool] = None
    is_invited: Optional[bool] = None


class ParticipantResponse(ParticipantBase):
    """참가자 응답 스키마"""
    id: UUID
    meeting_id: UUID
    user_id: Optional[int] = None
    is_invited: bool
    has_responded: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

