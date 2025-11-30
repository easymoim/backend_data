from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PlaceBase(BaseModel):
    """장소 기본 스키마"""
    name: str
    category: Optional[str] = None
    address: Optional[str] = None
    location: Optional[str] = None
    rating: Optional[float] = None
    thumbnail: Optional[str] = None


class PlaceCreate(PlaceBase):
    """장소 생성 스키마"""
    id: str  # API Place ID


class PlaceUpdate(BaseModel):
    """장소 업데이트 스키마"""
    name: Optional[str] = None
    category: Optional[str] = None
    address: Optional[str] = None
    location: Optional[str] = None
    rating: Optional[float] = None
    thumbnail: Optional[str] = None


class PlaceResponse(PlaceBase):
    """장소 응답 스키마"""
    id: str
    updated_at: datetime

    class Config:
        from_attributes = True

