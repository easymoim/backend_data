from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.database import Base


class Participant(Base):
    """참가자 모델"""
    __tablename__ = "participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    meeting_id = Column(UUID(as_uuid=True), ForeignKey("meetings.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    
    # 비로그인 참가자 정보
    name = Column(String(100))  # 로그인 사용자는 None, 비로그인 사용자는 이름 입력
    email = Column(String(255))  # 비로그인 사용자용 (선택)
    
    # 참가 상태
    is_invited = Column(Boolean, default=False)
    has_responded = Column(Boolean, default=False)  # 응답 여부
    
    # 메타 정보
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    meeting = relationship("Meeting", back_populates="participants")
    user = relationship("User", back_populates="participants")
    time_votes = relationship("TimeVote", back_populates="participant", cascade="all, delete-orphan")

