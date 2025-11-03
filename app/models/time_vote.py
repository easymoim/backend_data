from sqlalchemy import Column, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.database import Base


class TimeVote(Base):
    """시간 투표 모델"""
    __tablename__ = "time_votes"
    __table_args__ = (
        UniqueConstraint('participant_id', 'time_candidate_id', name='uq_participant_time_candidate'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("participants.id"), nullable=False, index=True)
    time_candidate_id = Column(UUID(as_uuid=True), ForeignKey("meeting_time_candidates.id"), nullable=False, index=True)
    
    # 투표 정보
    is_available = Column(Boolean, nullable=False, default=True)  # 가능 여부 (True: 가능, False: 불가능)
    
    # 메타 정보
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    participant = relationship("Participant", back_populates="time_votes")
    time_candidate = relationship("MeetingTimeCandidate", back_populates="votes")

