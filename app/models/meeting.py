"""
모임 모델
"""

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, Enum, Integer, JSON, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

from app.database import Base


class MeetingPurpose(str, enum.Enum):
    """약속 목적"""
    DINING = "dining"
    CAFE = "cafe"
    DRINK = "drink"
    ETC = "etc"


class LocationChoiceType(str, enum.Enum):
    """장소 선택 방식"""
    CENTER_LOCATION = "center_location"       # 중간위치 찾기
    PREFERENCE_AREA = "preference_area"       # 선호 지역 선택
    PREFERENCE_SUBWAY = "preference_subway"   # 선호 지하철역


class Meeting(Base):
    """약속 모델"""
    __tablename__ = "meeting"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(200), nullable=False)  # 모임 이름 (예: "이지모임")
    
    # 약속 생성자
    creator_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # 모임 목적 (배열) - ['dining', 'drink']
    purpose = Column(ARRAY(String), nullable=True)
    
    # 1차/2차 여부
    is_one_place = Column(Boolean, default=True)  # True: 한 곳에서 해결, False: 1차/2차 등 여러 장소
    
    # 장소 선택 방식
    location_choice_type = Column(
        String(50), 
        nullable=True
    )
    
    # 선택된 지역/역 (JSON 또는 직접입력값)
    # {"강남구", "강동구", "마포구"} 또는 {"강남역", "홍대입구역"} 또는 직접입력값
    location_choice_value = Column(String(255), nullable=True)
    
    # 모임 선호도 (JSON)
    # {"mood": "대화 나누기 좋은", "food": "한식", "condition": "주차"}
    preference_place = Column(JSON, nullable=True)
    
    # 마감 시간
    deadline = Column(DateTime, nullable=True)
    
    # 예상 참가자 수
    expected_participant_count = Column(Integer, nullable=True, default=4)
    
    # 공유 코드
    share_code = Column(String(50), nullable=True, unique=True)
    
    # 약속 확정 관련
    confirmed_time = Column(DateTime, nullable=True)  # 확정된 약속 시간
    confirmed_location = Column(String(255), nullable=True)  # 확정된 장소 (Place ID 또는 장소명)
    confirmed_at = Column(DateTime, nullable=True)  # 주최자가 "확정하기!" 누른 시간
    
    # 메타 정보
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    creator = relationship("User", back_populates="meetings")
    participants = relationship("Participant", back_populates="meeting", cascade="all, delete-orphan")
    time_candidates = relationship("MeetingTimeCandidate", back_populates="meeting", cascade="all, delete-orphan")
    place_candidates = relationship("PlaceCandidate", back_populates="meeting", cascade="all, delete-orphan")
