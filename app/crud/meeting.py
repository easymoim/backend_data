from sqlalchemy.orm import Session
from sqlalchemy import text, or_, func
from typing import List, Optional, Dict, Any
from uuid import UUID
from app.models.meeting import Meeting, LocationChoiceType
from app.models.participant import Participant
from app.schemas.meeting import MeetingCreate, MeetingUpdate
from sqlalchemy import case


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
    ).order_by(Meeting.created_at.desc()).offset(skip).limit(limit).all()


def get_all_meetings(db: Session, skip: int = 0, limit: int = 100) -> List[Meeting]:
    """모든 모임 목록 조회 (삭제되지 않은 모임만)"""
    return db.query(Meeting).filter(
        Meeting.deleted_at.is_(None)
    ).order_by(Meeting.created_at.desc()).offset(skip).limit(limit).all()


def get_meeting_by_share_code(db: Session, share_code: str) -> Optional[Meeting]:
    """공유 코드로 모임 조회 (삭제되지 않은 모임만)"""
    return db.query(Meeting).filter(
        Meeting.share_code == share_code,
        Meeting.deleted_at.is_(None)
    ).first()


def create_meeting(db: Session, meeting: MeetingCreate, creator_id: int) -> Meeting:
    """새 모임 생성"""
    # location_choice_type 문자열을 Enum 객체로 변환 (SQLAlchemy가 자동 처리)
    location_choice_type_enum = None
    if meeting.location_choice_type:
        try:
            location_choice_type_enum = LocationChoiceType(meeting.location_choice_type)
        except ValueError:
            location_choice_type_enum = None
    
    db_meeting = Meeting(
        name=meeting.name,
        purpose=meeting.purpose,
        creator_id=creator_id,
        is_one_place=meeting.is_one_place,
        location_choice_type=location_choice_type_enum,  # Enum 객체 전달
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
    # refresh는 필요한 경우에만 (자동 생성된 필드가 필요한 경우)
    # UUID와 timestamp는 이미 설정되어 있으므로 refresh 생략 가능
    db.refresh(db_meeting)  # id, created_at, updated_at을 위해 유지
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
            # 문자열을 Enum 객체로 변환 (SQLAlchemy가 자동 처리)
            db_meeting.location_choice_type = LocationChoiceType(meeting_update.location_choice_type)
        except ValueError:
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


def get_meetings_summary_by_user(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """
    사용자의 모임 요약 조회 (호스트/참가자 모두 포함)
    - status가 "confirmed"가 아닌 모임만 조회
    - participant_stats 계산 포함
    """
    # 1. 사용자가 호스트인 모임들 조회
    # status가 "confirmed"가 아닌 모임만 조회 (None 포함)
    host_meetings = db.query(Meeting).filter(
        Meeting.creator_id == user_id,
        Meeting.deleted_at.is_(None),
        or_(Meeting.status.is_(None), Meeting.status != "confirmed")
    ).all()
    
    # 2. 사용자가 참가자인 모임들 조회 (Participant 테이블 조인)
    participant_meetings = db.query(Meeting).join(
        Participant, Meeting.id == Participant.meeting_id
    ).filter(
        Participant.user_id == user_id,
        Meeting.deleted_at.is_(None),
        or_(Meeting.status.is_(None), Meeting.status != "confirmed")
    ).all()
    
    # 3. 중복 제거 (호스트이면서 참가자일 수도 있음)
    all_meetings = {}
    for meeting in host_meetings:
        all_meetings[meeting.id] = (meeting, True)  # (meeting, is_host)
    
    for meeting in participant_meetings:
        if meeting.id not in all_meetings:
            all_meetings[meeting.id] = (meeting, False)  # 참가자만
    
    # 4. 모든 모임의 참가자 통계를 한 번에 조회 (N+1 쿼리 문제 해결)
    meeting_ids = [meeting.id for meeting, _ in all_meetings.values()]
    
    if not meeting_ids:
        return []
    
    # 참가자 통계를 한 번의 쿼리로 조회
    # PostgreSQL에서 boolean을 integer로 변환할 때 CASE 문 사용
    participant_stats_query = db.query(
        Participant.meeting_id,
        func.count(Participant.id).label('total'),
        func.sum(
            case(
                (Participant.has_responded == True, 1),
                else_=0
            )
        ).label('responded')
    ).filter(
        Participant.meeting_id.in_(meeting_ids)
    ).group_by(Participant.meeting_id).all()
    
    # 통계를 딕셔너리로 변환
    stats_dict = {
        meeting_id: {
            "total": total or 0,
            "responded": int(responded) if responded else 0
        }
        for meeting_id, total, responded in participant_stats_query
    }
    
    # 5. 결과 생성
    result = []
    for meeting, is_host in all_meetings.values():
        # 통계 가져오기 (없으면 기본값)
        stats = stats_dict.get(meeting.id, {"total": 0, "responded": 0})
        
        # purpose는 List[str]이지만 첫 번째 값만 사용 (또는 문자열로 변환)
        purpose_str = meeting.purpose[0] if meeting.purpose and len(meeting.purpose) > 0 else ""
        
        result.append({
            "id": meeting.id,
            "title": meeting.name,
            "purpose": purpose_str,
            "status": meeting.status,
            "creator_id": meeting.creator_id,
            "deadline": meeting.deadline,
            "expected_participant_count": meeting.expected_participant_count,
            "participant_stats": stats,
            "is_host": is_host
        })
    
    return result

