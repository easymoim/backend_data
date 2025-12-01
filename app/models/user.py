from sqlalchemy import Column, String, DateTime, Boolean, Enum, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class OAuthProvider(str, enum.Enum):
    """OAuth 제공자"""
    GOOGLE = "google"
    KAKAO = "kakao"


class User(Base):
    """사용자 모델"""
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    
    # OAuth 정보
    oauth_provider = Column(String(50), nullable=False)  # google, kakao (Enum을 문자열로 저장)
    oauth_id = Column(String(255), nullable=False, unique=True)
    
    # 메타 정보
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    meetings = relationship("Meeting", back_populates="creator", cascade="all, delete-orphan")
    participants = relationship("Participant", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")

