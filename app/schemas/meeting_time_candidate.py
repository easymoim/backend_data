from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional, List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.time_vote import TimeVoteResponse


class MeetingTimeCandidateBase(BaseModel):
    """모임 시간 후보 기본 스키마"""
    candidate_time: Dict[str, int]  # 각 시간별 투표 수 (예: {"2025-11-01 02:00": 3, "2025-11-01 03:00": 2})


class MeetingTimeCandidateCreate(MeetingTimeCandidateBase):
    """모임 시간 후보 생성 스키마"""
    meeting_id: UUID


class MeetingTimeCandidateResponse(MeetingTimeCandidateBase):
    """모임 시간 후보 응답 스키마"""
    id: UUID
    meeting_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class MeetingTimeCandidateWithVotes(MeetingTimeCandidateResponse):
    """투표 정보를 포함한 시간 후보 응답 스키마"""
    votes: Optional[List["TimeVoteResponse"]] = None

