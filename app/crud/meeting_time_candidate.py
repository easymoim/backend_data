from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models.meeting_time_candidate import MeetingTimeCandidate
from app.schemas.meeting_time_candidate import MeetingTimeCandidateCreate


def get_time_candidate(db: Session, candidate_id: UUID) -> Optional[MeetingTimeCandidate]:
    """시간 후보 ID로 조회"""
    return db.query(MeetingTimeCandidate).filter(MeetingTimeCandidate.id == candidate_id).first()


def get_time_candidates_by_meeting(db: Session, meeting_id: UUID) -> List[MeetingTimeCandidate]:
    """모임별 시간 후보 목록 조회"""
    return db.query(MeetingTimeCandidate).filter(
        MeetingTimeCandidate.meeting_id == meeting_id
    ).order_by(MeetingTimeCandidate.candidate_time).all()


def create_time_candidate(db: Session, candidate: MeetingTimeCandidateCreate) -> MeetingTimeCandidate:
    """새 시간 후보 생성"""
    db_candidate = MeetingTimeCandidate(
        meeting_id=candidate.meeting_id,
        candidate_time=candidate.candidate_time,
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
    """투표 수 업데이트 (투표 생성/삭제 시 호출) - candidate_time JSON 업데이트"""
    from app.models.time_vote import TimeVote
    from sqlalchemy import func
    
    db_candidate = get_time_candidate(db, candidate_id)
    if not db_candidate:
        return None
    
    # candidate_time JSON에서 모든 시간 키 가져오기
    candidate_time = db_candidate.candidate_time.copy() if db_candidate.candidate_time else {}
    
    # 각 시간별로 가능한 투표 수 계산 (is_available=True이고 time_list에 해당 시간이 포함된 투표)
    for time_string in candidate_time.keys():
        # time_list에 해당 시간이 포함되고 is_available=True인 투표 수 계산
        available_votes = db.query(TimeVote).filter(
            TimeVote.time_candidate_id == candidate_id,
            TimeVote.is_available == True,
            func.array_to_string(TimeVote.time_list, ',').contains(time_string)
        ).count()
        candidate_time[time_string] = available_votes
    
    # candidate_time JSON 업데이트
    db_candidate.candidate_time = candidate_time
    
    db.commit()
    db.refresh(db_candidate)
    return db_candidate

