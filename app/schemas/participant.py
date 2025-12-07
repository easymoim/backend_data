"""
참가자 스키마
"""

from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional


class ParticipantBase(BaseModel):
    """참가자 기본 스키마"""
    nickname: Optional[str] = None
    location: Optional[str] = None
    preference_place: Optional[dict] = None  # {"mood": "...", "food": "한식", "condition": "주차"}


class ParticipantCreate(ParticipantBase):
    """참가자 생성 스키마"""
    meeting_id: UUID
    user_id: Optional[int] = None
    oauth_key: Optional[str] = None  # 카카오 고유 id


class ParticipantUpdate(BaseModel):
    """참가자 업데이트 스키마"""
    nickname: Optional[str] = None
    location: Optional[str] = None
    preference_place: Optional[dict] = None
    has_responded: Optional[bool] = None
    is_invited: Optional[bool] = None


class ParticipantResponse(ParticipantBase):
    """참가자 응답 스키마"""
    id: UUID
    meeting_id: UUID
    user_id: Optional[int] = None
    oauth_key: Optional[str] = None
    is_invited: bool
    has_responded: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
