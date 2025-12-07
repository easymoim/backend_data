"""
장소 후보 스키마
"""

from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional, List

from app.models.place_candidate import LocationType


class PlaceRecommendationItem(BaseModel):
    """개별 장소 추천 항목 (location JSON 내부 구조)"""
    rank: int
    place_id: str
    place_name: str
    reason: str
    match_score: Optional[float] = None
    matched_preferences: Optional[List[str]] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    place_url: Optional[str] = None
    category: Optional[str] = None
    distance: Optional[int] = None


class PlaceCandidateLocation(BaseModel):
    """place_candidate.location JSON 구조"""
    recommendations: List[PlaceRecommendationItem]
    summary: Optional[str] = None
    model_used: Optional[str] = None
    search_keywords: Optional[List[str]] = None
    total_candidates: Optional[int] = None


class PlaceCandidateBase(BaseModel):
    """장소 후보 기본 스키마"""
    preference_subway: Optional[List[str]] = None  # ["서울역", "종각"]
    preference_area: Optional[List[str]] = None    # ["강남구", "마포구"]
    food: Optional[dict] = None                    # {"korean": 3, "japanese": 2}
    condition: Optional[dict] = None               # {"parking": 2, "late_night": 1}
    location_type: Optional[LocationType] = None


class PlaceCandidateCreate(PlaceCandidateBase):
    """장소 후보 생성 스키마"""
    id: str  # 카카오 Place ID
    meeting_id: UUID
    location: Optional[dict] = None  # LLM 추천 결과 JSON


class PlaceCandidateResponse(PlaceCandidateBase):
    """장소 후보 응답 스키마"""
    id: str
    meeting_id: UUID
    location: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PlaceCandidateWithParsedLocation(PlaceCandidateResponse):
    """location을 파싱한 형태의 응답"""
    parsed_location: Optional[PlaceCandidateLocation] = None
    
    @classmethod
    def from_response(cls, response: PlaceCandidateResponse) -> "PlaceCandidateWithParsedLocation":
        """PlaceCandidateResponse에서 변환"""
        data = response.model_dump()
        
        if response.location:
            data["parsed_location"] = PlaceCandidateLocation(**response.location)
        
        return cls(**data)
