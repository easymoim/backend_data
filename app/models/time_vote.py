from sqlalchemy import Column, Boolean, ForeignKey, DateTime, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.database import Base


class TimeVote(Base):
    """시간 투표 모델"""
    __tablename__ = "time_vote"
    __table_args__ = (
        UniqueConstraint('participant_id', 'time_candidate_id', name='uq_participant_time_candidate'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("participant.id"), nullable=False, index=True)
    meeting_id = Column(UUID(as_uuid=True), ForeignKey("meeting.id"), nullable=False, index=True)
    time_candidate_id = Column(UUID(as_uuid=True), ForeignKey("meeting_time_candidate.id"), nullable=False, index=True)
    time_list = Column(ARRAY(Text), nullable=False)  # 투표한 시간 목록 (예: ["2025-11-01 02:00", "2025-11-01 03:00"])
    
    # 투표 정보
    is_available = Column(Boolean, nullable=False, default=True)  # 가능 여부 (True: 가능, False: 불가능)
    memo = Column(Text, nullable=True)  # 메모
    
    # 메타 정보
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    participant = relationship("Participant", back_populates="time_votes")
    meeting = relationship("Meeting")
    time_candidate = relationship("MeetingTimeCandidate", back_populates="votes")

