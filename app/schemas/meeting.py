from pydantic import BaseModel, field_serializer
from datetime import datetime
from uuid import UUID
from typing import Optional, List

from app.schemas.user import UserResponse
from app.models.meeting import LocationChoiceType


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

    @field_serializer('location_choice_type')
    def serialize_location_choice_type(self, value: Optional[LocationChoiceType], _info) -> Optional[str]:
        """Enum을 문자열로 변환"""
        if value is None:
            return None
        if isinstance(value, LocationChoiceType):
            return value.value
        return str(value) if value else None

    class Config:
        from_attributes = True

