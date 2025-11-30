from sqlalchemy import Column, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.database import Base


class PlaceVote(Base):
    """장소 투표 모델"""
    __tablename__ = "place_vote"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("participant.id"), nullable=False, index=True)
    meeting_id = Column(UUID(as_uuid=True), ForeignKey("meeting.id"), nullable=False, index=True)
    time_candidate_id = Column(UUID(as_uuid=True), ForeignKey("meeting_time_candidate.id"), nullable=False, index=True)
    
    # 투표 정보
    is_available = Column(Boolean, nullable=False, default=True)  # 가능 여부
    memo = Column(Text, nullable=True)  # 메모
    
    # 메타 정보
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    participant = relationship("Participant")
    meeting = relationship("Meeting")
    time_candidate = relationship("MeetingTimeCandidate")

