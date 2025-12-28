from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional, List

from app.models.meeting import MeetingPurpose, LocationChoiceType
from app.schemas.user import UserResponse


class MeetingBase(BaseModel):
    """모임 기본 스키마"""
    name: str
    purpose: List[str]  # string[] 형식


class MeetingCreate(MeetingBase):
    """모임 생성 스키마"""
    is_one_place: Optional[bool] = None
    location_choice_type: Optional[str] = None
    location_choice_value: Optional[str] = None
    preference_place: Optional[dict] = None
    deadline: Optional[datetime] = None
    expected_participant_count: Optional[int] = None
    share_code: Optional[str] = None
    status: Optional[str] = None
    available_times: Optional[List[datetime]] = None  # 주최자가 선택한 가능한 시간 목록


class MeetingUpdate(BaseModel):
    """모임 업데이트 스키마"""
    name: Optional[str] = None
    purpose: Optional[List[str]] = None
    is_one_place: Optional[bool] = None
    location_choice_type: Optional[str] = None
    location_choice_value: Optional[str] = None
    preference_place: Optional[dict] = None
    deadline: Optional[datetime] = None
    expected_participant_count: Optional[int] = None
    status: Optional[str] = None
    available_times: Optional[List[datetime]] = None  # 주최자가 선택한 가능한 시간 목록
    confirmed_time: Optional[datetime] = None
    confirmed_location: Optional[str] = None
    confirmed_at: Optional[datetime] = None


class MeetingResponse(MeetingBase):
    """모임 응답 스키마"""
    id: UUID
    creator_id: int
    is_one_place: Optional[bool] = None
    location_choice_type: Optional[str] = None
    location_choice_value: Optional[str] = None
    preference_place: Optional[dict] = None
    deadline: Optional[datetime] = None
    expected_participant_count: Optional[int] = None
    share_code: Optional[str] = None
    status: Optional[str] = None
    available_times: Optional[List[datetime]] = None  # 주최자가 선택한 가능한 시간 목록
    confirmed_time: Optional[datetime] = None
    confirmed_location: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    creator: Optional[UserResponse] = None

    class Config:
        from_attributes = True
        orm_mode = True
        use_enum_values = True


class ParticipantStats(BaseModel):
    """참가자 통계 스키마"""
    total: int
    responded: int


class MeetingSummaryItem(BaseModel):
    """모임 요약 항목 스키마"""
    id: UUID
    title: str  # name 필드를 title로 매핑
    purpose: str  # purpose는 List[str]이지만 첫 번째 값만 사용하거나 문자열로 변환
    status: Optional[str] = None
    creator_id: int
    deadline: Optional[datetime] = None
    expected_participant_count: Optional[int] = None
    participant_stats: ParticipantStats
    is_host: bool

    class Config:
        from_attributes = True
        orm_mode = True
        use_enum_values = True


class MeetingSummaryResponse(BaseModel):
    """모임 요약 응답 스키마"""
    meetings: List[MeetingSummaryItem]
