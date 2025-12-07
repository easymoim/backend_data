from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.database import Base


class MeetingTimeCandidate(Base):
    """모임 시간 후보 모델"""
    __tablename__ = "meeting_time_candidate"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    meeting_id = Column(UUID(as_uuid=True), ForeignKey("meeting.id"), nullable=False, index=True)
    
    # 각 시간별 투표 수 (JSON 형식: {"2025-11-01 02:00": 3, "2025-11-01 03:00": 2})
    candidate_time = Column(JSON, nullable=False)
    
    # 메타 정보
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    meeting = relationship("Meeting", back_populates="time_candidates")
    votes = relationship("TimeVote", back_populates="time_candidate", cascade="all, delete-orphan")

