from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, event
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import secrets
from datetime import datetime

from app.database import Base


def generate_share_code():
    """고유한 공유 코드 생성 (8자리 영숫자)"""
    return secrets.token_urlsafe(6)[:8].upper()


class Meeting(Base):
    """약속 모델"""
    __tablename__ = "meetings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # 약속 생성자
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # 공유 링크 (고유한 초대 코드)
    share_code = Column(String(50), unique=True, nullable=True, index=True)
    
    # 약속 상태
    is_confirmed = Column(Boolean, default=False)  # 약속 확정 여부
    confirmed_datetime = Column(DateTime)  # 확정된 약속 시간
    
    # 메타 정보
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    creator = relationship("User", back_populates="meetings")
    participants = relationship("Participant", back_populates="meeting", cascade="all, delete-orphan")
    time_candidates = relationship("MeetingTimeCandidate", back_populates="meeting", cascade="all, delete-orphan")


@event.listens_for(Meeting, "before_insert")
def generate_share_code_if_needed(mapper, connection, target):
    """Meeting 생성 전 share_code가 없으면 자동 생성"""
    if target.share_code is None:
        target.share_code = generate_share_code()

