from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from app.models.user import OAuthProvider


class UserBase(BaseModel):
    """사용자 기본 스키마"""
    name: str
    email: EmailStr


class UserCreate(UserBase):
    """사용자 생성 스키마"""
    oauth_provider: OAuthProvider
    oauth_id: str


class UserUpdate(BaseModel):
    """사용자 업데이트 스키마"""
    name: Optional[str] = None


class UserResponse(UserBase):
    """사용자 응답 스키마"""
    id: int
    oauth_provider: str  # 문자열로 반환
    oauth_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        use_enum_values = True
