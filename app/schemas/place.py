"""
장소 스키마 (LLM 추천 중 주최자가 선택한 장소)
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PlaceBase(BaseModel):
    """장소 기본 스키마"""
    name: str
    category: Optional[str] = None
    address: Optional[str] = None


class PlaceCreate(PlaceBase):
    """장소 생성 스키마"""
    id: str  # 카카오 Place ID
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    place_url: Optional[str] = None
    rating: Optional[float] = None
    thumbnail: Optional[str] = None


class PlaceResponse(PlaceBase):
    """장소 응답 스키마"""
    id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    place_url: Optional[str] = None
    rating: Optional[float] = None
    thumbnail: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

