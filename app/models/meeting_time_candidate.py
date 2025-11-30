from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.database import Base


class MeetingTimeCandidate(Base):
    """약속 시간 후보 모델"""
    __tablename__ = "meeting_time_candidate"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    meeting_id = Column(UUID(as_uuid=True), ForeignKey("meeting.id"), nullable=False, index=True)
    
    # 시간 후보 (JSON 형식: {"가능한 시간": "vote_count", "25.11.11.09:00": 3})
    candidate_time = Column(JSON, nullable=False)
    
    # 메타 정보
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    meeting = relationship("Meeting", back_populates="time_candidates")
    votes = relationship("TimeVote", back_populates="time_candidate", cascade="all, delete-orphan")

