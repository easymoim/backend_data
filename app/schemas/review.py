from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.schemas.user import UserResponse


class ReviewBase(BaseModel):
    """리뷰 기본 스키마"""
    rating: Optional[int] = Field(None, ge=1, le=5, description="평가 점수 (1-5)")
    image_list: Optional[List[str]] = Field(None, description="이미지 URL 리스트")
    text: Optional[str] = Field(None, description="리뷰 텍스트")
    like_count: Optional[int] = Field(0, description="좋아요 수")


class ReviewCreate(ReviewBase):
    """리뷰 생성 스키마"""
    meeting_id: UUID = Field(..., description="모임 ID")
    user_id: int = Field(..., description="리뷰 작성자 ID")


class ReviewUpdate(BaseModel):
    """리뷰 업데이트 스키마"""
    rating: Optional[int] = Field(None, ge=1, le=5, description="평가 점수 (1-5)")
    image_list: Optional[List[str]] = Field(None, description="이미지 URL 리스트")
    text: Optional[str] = Field(None, description="리뷰 텍스트")
    like_count: Optional[int] = Field(None, description="좋아요 수")


class ReviewResponse(ReviewBase):
    """리뷰 응답 스키마"""
    id: UUID
    meeting_id: UUID
    user_id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    user: Optional[UserResponse] = None

    class Config:
        orm_mode = True

