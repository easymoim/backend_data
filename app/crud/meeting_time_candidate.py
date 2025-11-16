from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models.meeting_time_candidate import MeetingTimeCandidate
from app.schemas.meeting_time_candidate import MeetingTimeCandidateCreate


def get_time_candidate(db: Session, candidate_id: UUID) -> Optional[MeetingTimeCandidate]:
    """시간 후보 ID로 조회"""
    return db.query(MeetingTimeCandidate).filter(MeetingTimeCandidate.id == candidate_id).first()


def get_time_candidates_by_meeting(db: Session, meeting_id: UUID) -> List[MeetingTimeCandidate]:
    """약속별 시간 후보 목록 조회"""
    return db.query(MeetingTimeCandidate).filter(
        MeetingTimeCandidate.meeting_id == meeting_id
    ).order_by(MeetingTimeCandidate.candidate_time).all()


def create_time_candidate(db: Session, candidate: MeetingTimeCandidateCreate) -> MeetingTimeCandidate:
    """새 시간 후보 생성"""
    db_candidate = MeetingTimeCandidate(
        meeting_id=candidate.meeting_id,
        candidate_time=candidate.candidate_time,
        vote_count=0,
    )
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate


def delete_time_candidate(db: Session, candidate_id: UUID) -> bool:
    """시간 후보 삭제"""
    db_candidate = get_time_candidate(db, candidate_id)
    if not db_candidate:
        return False
    
    db.delete(db_candidate)
    db.commit()
    return True


def update_vote_count(db: Session, candidate_id: UUID) -> Optional[MeetingTimeCandidate]:
    """투표 수 업데이트 (투표 생성/삭제 시 호출)"""
    db_candidate = get_time_candidate(db, candidate_id)
    if not db_candidate:
        return None
    
    # 실제 투표 수 계산
    vote_count = len(db_candidate.votes)
    db_candidate.vote_count = vote_count
    
    db.commit()
    db.refresh(db_candidate)
    return db_candidate

