from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models.meeting import Meeting, LocationChoiceType
from app.schemas.meeting import MeetingCreate, MeetingUpdate


def get_meeting(db: Session, meeting_id: UUID) -> Optional[Meeting]:
    """모임 ID로 조회 (삭제되지 않은 모임만)"""
    return db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.deleted_at.is_(None)
    ).first()


def get_meetings_by_creator(db: Session, creator_id: int, skip: int = 0, limit: int = 100) -> List[Meeting]:
    """생성자별 모임 목록 조회 (삭제되지 않은 모임만)"""
    return db.query(Meeting).filter(
        Meeting.creator_id == creator_id,
        Meeting.deleted_at.is_(None)
    ).offset(skip).limit(limit).all()


def get_all_meetings(db: Session, skip: int = 0, limit: int = 100) -> List[Meeting]:
    """모든 모임 목록 조회 (삭제되지 않은 모임만)"""
    return db.query(Meeting).filter(
        Meeting.deleted_at.is_(None)
    ).offset(skip).limit(limit).all()


def get_meeting_by_share_code(db: Session, share_code: str) -> Optional[Meeting]:
    """공유 코드로 모임 조회 (삭제되지 않은 모임만)"""
    return db.query(Meeting).filter(
        Meeting.share_code == share_code,
        Meeting.deleted_at.is_(None)
    ).first()


def create_meeting(db: Session, meeting: MeetingCreate, creator_id: int) -> Meeting:
    """새 모임 생성"""
    # location_choice_type 문자열을 Enum으로 변환
    location_choice_type_enum = None
    if meeting.location_choice_type:
        try:
            location_choice_type_enum = LocationChoiceType(meeting.location_choice_type)
        except ValueError:
            # 유효하지 않은 값인 경우 None으로 설정
            location_choice_type_enum = None
    
    db_meeting = Meeting(
        name=meeting.name,
        purpose=meeting.purpose,
        creator_id=creator_id,
        is_one_place=meeting.is_one_place,
        location_choice_type=location_choice_type_enum,
        location_choice_value=meeting.location_choice_value,
        preference_place=meeting.preference_place,
        deadline=meeting.deadline,
        expected_participant_count=meeting.expected_participant_count,
        share_code=meeting.share_code,
        status=meeting.status,
        available_times=meeting.available_times,
    )
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return db_meeting


def update_meeting(db: Session, meeting_id: UUID, meeting_update: MeetingUpdate) -> Optional[Meeting]:
    """모임 정보 업데이트"""
    db_meeting = get_meeting(db, meeting_id)
    if not db_meeting:
        return None
    
    if meeting_update.name is not None:
        db_meeting.name = meeting_update.name
    if meeting_update.purpose is not None:
        db_meeting.purpose = meeting_update.purpose
    if meeting_update.is_one_place is not None:
        db_meeting.is_one_place = meeting_update.is_one_place
    if meeting_update.location_choice_type is not None:
        try:
            db_meeting.location_choice_type = LocationChoiceType(meeting_update.location_choice_type)
        except ValueError:
            # 유효하지 않은 값인 경우 None으로 설정
            db_meeting.location_choice_type = None
    if meeting_update.location_choice_value is not None:
        db_meeting.location_choice_value = meeting_update.location_choice_value
    if meeting_update.preference_place is not None:
        db_meeting.preference_place = meeting_update.preference_place
    if meeting_update.deadline is not None:
        db_meeting.deadline = meeting_update.deadline
    if meeting_update.expected_participant_count is not None:
        db_meeting.expected_participant_count = meeting_update.expected_participant_count
    if meeting_update.status is not None:
        db_meeting.status = meeting_update.status
    if meeting_update.available_times is not None:
        db_meeting.available_times = meeting_update.available_times
    if meeting_update.confirmed_time is not None:
        db_meeting.confirmed_time = meeting_update.confirmed_time
    if meeting_update.confirmed_location is not None:
        db_meeting.confirmed_location = meeting_update.confirmed_location
    if meeting_update.confirmed_at is not None:
        db_meeting.confirmed_at = meeting_update.confirmed_at
    
    db.commit()
    db.refresh(db_meeting)
    return db_meeting


def delete_meeting(db: Session, meeting_id: UUID) -> bool:
    """모임 소프트 삭제"""
    db_meeting = get_meeting(db, meeting_id)
    if not db_meeting:
        return False
    
    # 소프트 삭제: deleted_at에 현재 시간 설정
    from datetime import datetime
    db_meeting.deleted_at = datetime.utcnow()
    db.commit()
    db.refresh(db_meeting)
    return True

