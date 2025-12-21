"""
장소 추천 스키마
"""

from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class PlaceRecommendationRequest(BaseModel):
    """장소 추천 요청 스키마"""
    meeting_id: UUID
    top_n: int = 3  # 추천할 장소 수


class RecommendedPlace(BaseModel):
    """추천된 개별 장소"""
    rank: int
    place_id: str
    place_name: str
    reason: str
    match_score: Optional[float] = None
    matched_preferences: Optional[List[str]] = None
    address: Optional[str] = None
    address_jibun: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    place_url: Optional[str] = None
    category: Optional[str] = None
    distance: Optional[int] = None


class PlaceRecommendationResponse(BaseModel):
    """장소 추천 응답 스키마"""
    meeting_id: UUID
    recommendations: List[RecommendedPlace]
    summary: Optional[str] = None
    center_location: Optional[str] = None  # 중간 위치 (예: 강남역, 홍대 등)
    model_used: Optional[str] = None
    search_keywords: Optional[List[str]] = None
    total_candidates: Optional[int] = None
    place_candidate_id: Optional[str] = None  # DB에 저장된 place_candidate ID

