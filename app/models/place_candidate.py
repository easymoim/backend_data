"""
장소 후보 모델

장소 추천을 위한 검색 조건 및 LLM 추천 결과 저장
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class LocationType(str, enum.Enum):
    """장소 선택 방식"""
    CENTER_LOCATION = "center_location"       # 중간위치 찾기
    PREFERENCE_AREA = "preference_area"       # 선호 지역 선택
    PREFERENCE_SUBWAY = "preference_subway"   # 선호 지하철역


class PlaceCandidate(Base):
    """장소 후보 모델"""
    __tablename__ = "place_candidate"

    # PK는 카카오 API Place ID 사용
    id = Column(String(50), primary_key=True, index=True)
    meeting_id = Column(UUID(as_uuid=True), ForeignKey("meeting.id"), nullable=False, index=True)
    
    # LLM 추천 결과 (JSON)
    # {
    #   "recommendations": [
    #     {
    #       "rank": 1,
    #       "place_id": "12345678",
    #       "place_name": "강강술래 홍대점",
    #       "reason": "3명이 선호하는 한식, 활기찬 분위기...",
    #       "match_score": 85,
    #       "matched_preferences": ["한식", "활기찬"],
    #       "address": "서울 마포구 잔다리로6길 25",
    #       "latitude": 37.5523564,
    #       "longitude": 126.9205691,
    #       "phone": "02-3143-6635",
    #       "place_url": "http://place.map.kakao.com/18257217",
    #       "category": "한식",
    #       "distance": 575
    #     },
    #     ...
    #   ],
    #   "summary": "참가자들의 선호도를 종합적으로 고려하여...",
    #   "model_used": "gemini-2.0-flash",
    #   "search_keywords": ["마포구 한식 맛집", "마포구 회식"],
    #   "total_candidates": 45
    # }
    location = Column(JSON, nullable=True)
    
    # 검색 조건 - 선호 지하철역 (JSON)
    # ["서울역", "종각"]
    preference_subway = Column(JSON, nullable=True)
    
    # 검색 조건 - 선호 지역 (JSON)
    # ["강남구", "강동구", "마포구"]
    preference_area = Column(JSON, nullable=True)
    
    # 검색 조건 - 선호 음식 (JSON)
    # ["korean", "japanese"] 또는 {"korean": 3, "japanese": 2} (가중치 포함)
    food = Column(JSON, nullable=True)
    
    # 검색 조건 - 필요 조건 (JSON)
    # ["parking", "private_room"] 또는 {"parking": 2, "late_night": 1}
    condition = Column(JSON, nullable=True)
    
    # 장소 선택 방식
    location_type = Column(String(50), nullable=True)
    
    # 관계
    meeting = relationship("Meeting", back_populates="place_candidates")
