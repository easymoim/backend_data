from sqlalchemy import Column, ForeignKey, DateTime, ARRAY, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.database import Base


class PlaceVote(Base):
    """장소 투표 모델"""
    __tablename__ = "place_vote"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("participant.id", ondelete="CASCADE"), nullable=False, index=True)
    meeting_id = Column(UUID(as_uuid=True), ForeignKey("meeting.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 투표 정보
    place_list = Column(ARRAY(String), nullable=False)  # 장소 목록 (text[])
    
    # 메타 정보
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    participant = relationship("Participant")
    meeting = relationship("Meeting")

