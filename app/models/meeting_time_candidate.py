from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class MeetingTimeCandidate(Base):
    """약속 시간 후보 모델"""
    __tablename__ = "meeting_time_candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    meeting_id = Column(UUID(as_uuid=True), ForeignKey("meetings.id"), nullable=False, index=True)
    
    # 시간 후보
    candidate_datetime = Column(DateTime, nullable=False)  # 후보 시간
    
    # 관계
    meeting = relationship("Meeting", back_populates="time_candidates")
    votes = relationship("TimeVote", back_populates="time_candidate", cascade="all, delete-orphan")

