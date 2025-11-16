from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models.meeting import Meeting
from app.schemas.meeting import MeetingCreate, MeetingUpdate


def get_meeting(db: Session, meeting_id: UUID) -> Optional[Meeting]:
    """약속 ID로 조회"""
    return db.query(Meeting).filter(Meeting.id == meeting_id).first()


def get_meetings_by_creator(db: Session, creator_id: int, skip: int = 0, limit: int = 100) -> List[Meeting]:
    """생성자별 약속 목록 조회"""
    return db.query(Meeting).filter(Meeting.creator_id == creator_id).offset(skip).limit(limit).all()


def get_all_meetings(db: Session, skip: int = 0, limit: int = 100) -> List[Meeting]:
    """모든 약속 목록 조회"""
    return db.query(Meeting).offset(skip).limit(limit).all()


def create_meeting(db: Session, meeting: MeetingCreate, creator_id: int) -> Meeting:
    """새 약속 생성"""
    db_meeting = Meeting(
        title=meeting.title,
        description=meeting.description,
        purpose=meeting.purpose,
        creator_id=creator_id,
    )
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return db_meeting


def update_meeting(db: Session, meeting_id: UUID, meeting_update: MeetingUpdate) -> Optional[Meeting]:
    """약속 정보 업데이트"""
    db_meeting = get_meeting(db, meeting_id)
    if not db_meeting:
        return None
    
    if meeting_update.title is not None:
        db_meeting.title = meeting_update.title
    if meeting_update.description is not None:
        db_meeting.description = meeting_update.description
    if meeting_update.purpose is not None:
        db_meeting.purpose = meeting_update.purpose
    if meeting_update.is_confirmed is not None:
        db_meeting.is_confirmed = meeting_update.is_confirmed
    if meeting_update.confirmed_at is not None:
        db_meeting.confirmed_at = meeting_update.confirmed_at
    if meeting_update.confirmed_location is not None:
        db_meeting.confirmed_location = meeting_update.confirmed_location
    
    db.commit()
    db.refresh(db_meeting)
    return db_meeting


def delete_meeting(db: Session, meeting_id: UUID) -> bool:
    """약속 삭제"""
    db_meeting = get_meeting(db, meeting_id)
    if not db_meeting:
        return False
    
    db.delete(db_meeting)
    db.commit()
    return True

