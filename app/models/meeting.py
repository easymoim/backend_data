from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, Enum, Integer
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


class Meeting(Base):
    """약속 모델"""
    __tablename__ = "meetings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    purpose = Column(Enum(MeetingPurpose), nullable=False)
    
    # 약속 생성자
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 약속 상태
    is_confirmed = Column(Boolean, default=False)  # 약속 확정 여부
    confirmed_at = Column(DateTime, nullable=True)  # 확정된 약속 시간
    confirmed_location = Column(String(255), nullable=True)  # 확정된 장소
    
    # 메타 정보
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    creator = relationship("User", back_populates="meetings")
    participants = relationship("Participant", back_populates="meeting", cascade="all, delete-orphan")
    time_candidates = relationship("MeetingTimeCandidate", back_populates="meeting", cascade="all, delete-orphan")

