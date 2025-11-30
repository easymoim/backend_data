from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.database import Base


class Participant(Base):
    """참가자 모델"""
    __tablename__ = "participant"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    meeting_id = Column(UUID(as_uuid=True), ForeignKey("meeting.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True, index=True)  # 비로그인 사용자도 가능
    
    # 참가자 정보
    nickname = Column(String(255), nullable=True)  # 닉네임
    oauth_key = Column(String(255), nullable=True)  # 카카오 고유 id
    
    # 참가 상태
    is_invited = Column(Boolean, default=False)
    has_responded = Column(Boolean, default=False)  # 응답 여부
    preference_place = Column(JSON, nullable=True)  # {"mood": "대화 나누기 좋은", "food": "한식", "condition": "주차"}
    location = Column(String(255), nullable=True)  # 장소
    
    # 메타 정보
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    meeting = relationship("Meeting", back_populates="participants")
    user = relationship("User", back_populates="participants")
    time_votes = relationship("TimeVote", back_populates="participant", cascade="all, delete-orphan")

