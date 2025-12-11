from pydantic import BaseModel
from typing import Optional, Dict, Any
from uuid import UUID
from app.models.place_candidate import LocationType


class PlaceCandidateBase(BaseModel):
    """장소 후보 기본 스키마"""
    meeting_id: UUID
    location: Optional[str] = None
    preference_subway: Optional[Dict[str, Any]] = None
    preference_area: Optional[Dict[str, Any]] = None
    food: Optional[str] = None
    condition: Optional[str] = None
    location_type: Optional[str] = None  # center_location, preference_area, preference_subway


class PlaceCandidateCreate(PlaceCandidateBase):
    """장소 후보 생성 스키마"""
    id: str  # API Place ID


class PlaceCandidateUpdate(BaseModel):
    """장소 후보 업데이트 스키마"""
    location: Optional[str] = None
    preference_subway: Optional[Dict[str, Any]] = None
    preference_area: Optional[Dict[str, Any]] = None
    food: Optional[str] = None
    condition: Optional[str] = None
    location_type: Optional[str] = None


class PlaceCandidateResponse(PlaceCandidateBase):
    """장소 후보 응답 스키마"""
    id: str

    class Config:
        orm_mode = True
        use_enum_values = True
