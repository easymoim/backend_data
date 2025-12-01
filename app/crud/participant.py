from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models.participant import Participant
from app.schemas.participant import ParticipantCreate, ParticipantUpdate


def get_participant(db: Session, participant_id: UUID) -> Optional[Participant]:
    """참가자 ID로 조회"""
    return db.query(Participant).filter(Participant.id == participant_id).first()


def get_participants_by_meeting(db: Session, meeting_id: UUID) -> List[Participant]:
    """모임별 참가자 목록 조회"""
    return db.query(Participant).filter(Participant.meeting_id == meeting_id).all()


def get_participants_by_user(db: Session, user_id: int) -> List[Participant]:
    """사용자별 참가한 모임 목록 조회"""
    return db.query(Participant).filter(Participant.user_id == user_id).all()


def create_participant(db: Session, participant: ParticipantCreate) -> Participant:
    """새 참가자 생성"""
    db_participant = Participant(
        meeting_id=participant.meeting_id,
        user_id=participant.user_id,
        location=participant.location,
    )
    db.add(db_participant)
    db.commit()
    db.refresh(db_participant)
    return db_participant


def update_participant(db: Session, participant_id: UUID, participant_update: ParticipantUpdate) -> Optional[Participant]:
    """참가자 정보 업데이트"""
    db_participant = get_participant(db, participant_id)
    if not db_participant:
        return None
    
    if participant_update.location is not None:
        db_participant.location = participant_update.location
    if participant_update.has_responded is not None:
        db_participant.has_responded = participant_update.has_responded
    if participant_update.is_invited is not None:
        db_participant.is_invited = participant_update.is_invited
    
    db.commit()
    db.refresh(db_participant)
    return db_participant


def delete_participant(db: Session, participant_id: UUID) -> bool:
    """참가자 삭제"""
    db_participant = get_participant(db, participant_id)
    if not db_participant:
        return False
    
    db.delete(db_participant)
    db.commit()
    return True

