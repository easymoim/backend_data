from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app import crud
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse

router = APIRouter()


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review: ReviewCreate,
    db: Session = Depends(get_db)
):
    """새 리뷰 생성"""
    return crud.review.create_review(db=db, review=review)


@router.get("/", response_model=List[ReviewResponse])
def read_reviews(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """모든 리뷰 목록 조회"""
    reviews = crud.review.get_all_reviews(db, skip=skip, limit=limit)
    return reviews


@router.get("/{review_id}", response_model=ReviewResponse)
def read_review(
    review_id: UUID,
    db: Session = Depends(get_db)
):
    """리뷰 ID로 조회"""
    db_review = crud.review.get_review(db, review_id=review_id)
    if db_review is None:
        raise HTTPException(status_code=404, detail="리뷰를 찾을 수 없습니다")
    return db_review


@router.get("/meeting/{meeting_id}", response_model=List[ReviewResponse])
def read_reviews_by_meeting(
    meeting_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """모임별 리뷰 목록 조회"""
    reviews = crud.review.get_reviews_by_meeting(db, meeting_id=meeting_id, skip=skip, limit=limit)
    return reviews


@router.get("/user/{user_id}", response_model=List[ReviewResponse])
def read_reviews_by_user(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """사용자별 리뷰 목록 조회"""
    reviews = crud.review.get_reviews_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return reviews


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: UUID,
    review_update: ReviewUpdate,
    db: Session = Depends(get_db)
):
    """리뷰 정보 업데이트"""
    db_review = crud.review.update_review(db, review_id=review_id, review_update=review_update)
    if db_review is None:
        raise HTTPException(status_code=404, detail="리뷰를 찾을 수 없습니다")
    return db_review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: UUID,
    db: Session = Depends(get_db)
):
    """리뷰 삭제 (소프트 삭제)"""
    success = crud.review.delete_review(db, review_id=review_id)
    if not success:
        raise HTTPException(status_code=404, detail="리뷰를 찾을 수 없습니다")
    return None


@router.post("/{review_id}/like", response_model=ReviewResponse)
def like_review(
    review_id: UUID,
    db: Session = Depends(get_db)
):
    """리뷰 좋아요"""
    db_review = crud.review.increment_like_count(db, review_id=review_id)
    if db_review is None:
        raise HTTPException(status_code=404, detail="리뷰를 찾을 수 없습니다")
    return db_review


@router.delete("/{review_id}/like", response_model=ReviewResponse)
def unlike_review(
    review_id: UUID,
    db: Session = Depends(get_db)
):
    """리뷰 좋아요 취소"""
    db_review = crud.review.decrement_like_count(db, review_id=review_id)
    if db_review is None:
        raise HTTPException(status_code=404, detail="리뷰를 찾을 수 없습니다")
    return db_review

