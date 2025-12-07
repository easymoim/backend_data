"""
장소 모델

LLM이 추천해준 것 중에서 주최자가 선택한 장소 저장
"""

from sqlalchemy import Column, String, DateTime, Text, Float
from datetime import datetime

from app.database import Base


class Place(Base):
    """선택된 장소 모델"""
    __tablename__ = "place"

    # PK는 카카오 API Place ID 사용
    id = Column(String(50), primary_key=True, index=True)
    
    # 장소 기본 정보
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    
    # 위치 정보 (위도, 경도)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # 추가 정보
    phone = Column(String(50), nullable=True)
    place_url = Column(Text, nullable=True)
    rating = Column(Float, nullable=True)
    thumbnail = Column(Text, nullable=True)
    
    # 메타 정보
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
