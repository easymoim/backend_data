from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from typing import Optional

from app.models.user import OAuthProvider


class UserBase(BaseModel):
    """사용자 기본 스키마"""
    email: EmailStr
    nickname: Optional[str] = None
    profile_image_url: Optional[str] = None


class UserCreate(UserBase):
    """사용자 생성 스키마"""
    oauth_provider: OAuthProvider
    oauth_id: str


class UserUpdate(BaseModel):
    """사용자 업데이트 스키마"""
    nickname: Optional[str] = None
    profile_image_url: Optional[str] = None


class UserResponse(UserBase):
    """사용자 응답 스키마"""
    id: UUID
    oauth_provider: OAuthProvider
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

