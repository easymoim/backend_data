from sqlalchemy import Column, String, DateTime, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Place(Base):
    """장소 모델 (LLM이 추천해준 것 중에서 주최자가 선택한 것이 담김)"""
    __tablename__ = "place"

    id = Column(String(255), primary_key=True, index=True)  # API Place ID 사용
    name = Column(String(255), nullable=False)
    category = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)  # 위도, 경도 등
    
    rating = Column(Float, nullable=True)
    thumbnail = Column(Text, nullable=True)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

