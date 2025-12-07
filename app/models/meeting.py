from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

from app.database import Base


class LocationChoiceType(str, enum.Enum):
    """장소 선택 타입"""
    CENTER_LOCATION = "center_location"
    PREFERENCE_AREA = "preference_area"
    PREFERENCE_SUBWAY = "preference_subway"


class Meeting(Base):
    """모임 모델"""
    __tablename__ = "meeting"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)  # 모임 이름
    creator_id = Column(Integer, ForeignKey("user.id"), nullable=False)  # Host
    
    # 모임 목적 (string[])
    purpose = Column(ARRAY(String), nullable=False)  # ['dining', 'drink']
    
    # 장소 관련 설정
    is_one_place = Column(Boolean, nullable=True)  # 한 곳에서 해결 여부
    location_choice_type = Column(String(50), nullable=True)  # center_location, preference_area, preference_subway (Enum을 문자열로 저장)
    location_choice_value = Column(String(255), nullable=True)  # {"강남구", "강동구", "마포구"} || {"강남역", "설대입구역", "구디역"} || {직접입력한값}
    preference_place = Column(JSON, nullable=True)  # {"mood": "대화 나누기 좋은", "food": "한식", "condition": "주차"}
    
    # 모임 설정
    deadline = Column(DateTime, nullable=True)  # 마감 시간
    expected_participant_count = Column(Integer, nullable=True)  # 예상 참가 인원
    share_code = Column(String(255), nullable=True, unique=True, index=True)  # 공유 코드
    status = Column(String(50), nullable=True)  # 모임 상태
    available_times = Column(ARRAY(DateTime), nullable=True)  # 주최자가 선택한 가능한 시간 목록 (예: ["2025-11-10 09:00", "2025-11-10 10:00", "2025-11-11 08:00"])
    
    # 모임 확정 정보
    confirmed_time = Column(DateTime, nullable=True)  # 확정된 모임 시간
    confirmed_location = Column(String(255), nullable=True)  # 확정된 장소
    confirmed_at = Column(DateTime, nullable=True)  # 주최자가 "확정하기!" 누른 시간
    
    # 메타 정보
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)  # 소프트 삭제 시간

    # 관계
    creator = relationship("User", back_populates="meetings")
    participants = relationship("Participant", back_populates="meeting", cascade="all, delete-orphan")
    time_candidates = relationship("MeetingTimeCandidate", back_populates="meeting", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="meeting", cascade="all, delete-orphan")

