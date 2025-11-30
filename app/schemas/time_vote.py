from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import List


class TimeVoteBase(BaseModel):
    """시간 투표 기본 스키마"""
    time_list: List[str]  # 투표한 시간 목록 (예: ["2025-11-01 02:00", "2025-11-01 03:00"])
    is_available: bool = True  # True: 가능, False: 불가능
    memo: str | None = None  # 메모


class TimeVoteCreate(TimeVoteBase):
    """시간 투표 생성 스키마"""
    participant_id: UUID
    meeting_id: UUID
    time_candidate_id: UUID


class TimeVoteUpdate(BaseModel):
    """시간 투표 업데이트 스키마"""
    time_list: List[str] | None = None
    is_available: bool | None = None
    memo: str | None = None


class TimeVoteResponse(TimeVoteBase):
    """시간 투표 응답 스키마"""
    id: UUID
    participant_id: UUID
    meeting_id: UUID
    time_candidate_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

