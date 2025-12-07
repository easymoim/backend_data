from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate


def get_review(db: Session, review_id: UUID) -> Optional[Review]:
    """리뷰 ID로 조회 (삭제되지 않은 리뷰만)"""
    return db.query(Review).filter(
        Review.id == review_id,
        Review.deleted_at.is_(None)
    ).first()


def get_reviews_by_meeting(db: Session, meeting_id: UUID, skip: int = 0, limit: int = 100) -> List[Review]:
    """모임별 리뷰 목록 조회 (삭제되지 않은 리뷰만)"""
    return db.query(Review).filter(
        Review.meeting_id == meeting_id,
        Review.deleted_at.is_(None)
    ).offset(skip).limit(limit).all()


def get_reviews_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Review]:
    """사용자별 리뷰 목록 조회 (삭제되지 않은 리뷰만)"""
    return db.query(Review).filter(
        Review.user_id == user_id,
        Review.deleted_at.is_(None)
    ).offset(skip).limit(limit).all()


def get_all_reviews(db: Session, skip: int = 0, limit: int = 100) -> List[Review]:
    """모든 리뷰 목록 조회 (삭제되지 않은 리뷰만)"""
    return db.query(Review).filter(
        Review.deleted_at.is_(None)
    ).offset(skip).limit(limit).all()


def create_review(db: Session, review: ReviewCreate) -> Review:
    """새 리뷰 생성"""
    db_review = Review(
        meeting_id=review.meeting_id,
        user_id=review.user_id,
        rating=review.rating,
        image_list=review.image_list,
        text=review.text,
        like_count=review.like_count or 0,
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


def update_review(db: Session, review_id: UUID, review_update: ReviewUpdate) -> Optional[Review]:
    """리뷰 정보 업데이트"""
    db_review = get_review(db, review_id)
    if not db_review:
        return None
    
    if review_update.rating is not None:
        db_review.rating = review_update.rating
    if review_update.image_list is not None:
        db_review.image_list = review_update.image_list
    if review_update.text is not None:
        db_review.text = review_update.text
    if review_update.like_count is not None:
        db_review.like_count = review_update.like_count
    
    db.commit()
    db.refresh(db_review)
    return db_review


def delete_review(db: Session, review_id: UUID) -> bool:
    """리뷰 소프트 삭제"""
    db_review = get_review(db, review_id)
    if not db_review:
        return False
    
    # 소프트 삭제: deleted_at에 현재 시간 설정
    from datetime import datetime
    db_review.deleted_at = datetime.utcnow()
    db.commit()
    db.refresh(db_review)
    return True


def increment_like_count(db: Session, review_id: UUID) -> Optional[Review]:
    """리뷰 좋아요 수 증가"""
    db_review = get_review(db, review_id)
    if not db_review:
        return None
    
    db_review.like_count += 1
    db.commit()
    db.refresh(db_review)
    return db_review


def decrement_like_count(db: Session, review_id: UUID) -> Optional[Review]:
    """리뷰 좋아요 수 감소"""
    db_review = get_review(db, review_id)
    if not db_review:
        return None
    
    if db_review.like_count > 0:
        db_review.like_count -= 1
        db.commit()
        db.refresh(db_review)
    
    return db_review

