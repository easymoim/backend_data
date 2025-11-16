from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.time_vote import TimeVoteResponse


class MeetingTimeCandidateBase(BaseModel):
    """약속 시간 후보 기본 스키마"""
    candidate_time: datetime


class MeetingTimeCandidateCreate(MeetingTimeCandidateBase):
    """약속 시간 후보 생성 스키마"""
    meeting_id: UUID


class MeetingTimeCandidateResponse(MeetingTimeCandidateBase):
    """약속 시간 후보 응답 스키마"""
    id: UUID
    meeting_id: UUID
    vote_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class MeetingTimeCandidateWithVotes(MeetingTimeCandidateResponse):
    """투표 정보를 포함한 시간 후보 응답 스키마"""
    votes: Optional[List["TimeVoteResponse"]] = None

