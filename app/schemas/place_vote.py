from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class PlaceVoteBase(BaseModel):
    """장소 투표 기본 스키마"""
    participant_id: UUID
    meeting_id: UUID
    place_list: List[str]  # 장소 목록 (text[])


class PlaceVoteCreate(PlaceVoteBase):
    """장소 투표 생성 스키마"""
    pass


class PlaceVoteUpdate(BaseModel):
    """장소 투표 업데이트 스키마"""
    place_list: Optional[List[str]] = None


class PlaceVoteResponse(PlaceVoteBase):
    """장소 투표 응답 스키마"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

