from sqlalchemy import Column, String, DateTime, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

from app.database import Base


class OAuthProvider(str, enum.Enum):
    """OAuth 제공자"""
    GOOGLE = "google"
    KAKAO = "kakao"


class User(Base):
    """사용자 모델"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    nickname = Column(String(100))
    profile_image_url = Column(String(500))
    
    # OAuth 정보
    oauth_provider = Column(Enum(OAuthProvider), nullable=False)
    oauth_id = Column(String(255), nullable=False, unique=True)
    
    # 메타 정보
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    meetings = relationship("Meeting", back_populates="creator", cascade="all, delete-orphan")
    participants = relationship("Participant", back_populates="user", cascade="all, delete-orphan")

