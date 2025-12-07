from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.database import Base


class Review(Base):
    """모임 리뷰 모델"""
    __tablename__ = "review"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    meeting_id = Column(UUID(as_uuid=True), ForeignKey("meeting.id"), nullable=False)  # 모임 ID
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)  # 리뷰 작성자 ID
    
    rating = Column(Integer, nullable=True)  # 평가 점수
    image_list = Column(ARRAY(String), nullable=True)  # 이미지 URL 리스트 [image1, image2, ...]
    text = Column(Text, nullable=True)  # 리뷰 텍스트
    like_count = Column(Integer, default=0, nullable=False)  # 좋아요 수
    
    # 메타 정보
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)  # 소프트 삭제 시간

    # 관계
    meeting = relationship("Meeting", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

