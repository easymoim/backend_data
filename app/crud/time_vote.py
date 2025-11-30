from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models.time_vote import TimeVote
from app.schemas.time_vote import TimeVoteCreate, TimeVoteUpdate
from app.crud.meeting_time_candidate import update_vote_count


def get_time_vote(db: Session, vote_id: UUID) -> Optional[TimeVote]:
    """투표 ID로 조회"""
    return db.query(TimeVote).filter(TimeVote.id == vote_id).first()


def get_time_votes_by_participant(db: Session, participant_id: UUID) -> List[TimeVote]:
    """참가자별 투표 목록 조회"""
    return db.query(TimeVote).filter(TimeVote.participant_id == participant_id).all()


def get_time_votes_by_candidate(db: Session, candidate_id: UUID) -> List[TimeVote]:
    """시간 후보별 투표 목록 조회"""
    return db.query(TimeVote).filter(TimeVote.time_candidate_id == candidate_id).all()


def get_time_vote_by_participant_and_candidate(
    db: Session, participant_id: UUID, candidate_id: UUID
) -> Optional[TimeVote]:
    """참가자와 시간 후보로 투표 조회"""
    return db.query(TimeVote).filter(
        TimeVote.participant_id == participant_id,
        TimeVote.time_candidate_id == candidate_id
    ).first()


def create_time_vote(db: Session, vote: TimeVoteCreate) -> TimeVote:
    """새 투표 생성 (이미 존재하면 업데이트)"""
    # 기존 투표 확인
    existing_vote = get_time_vote_by_participant_and_candidate(
        db, vote.participant_id, vote.time_candidate_id
    )
    
    if existing_vote:
        # 기존 투표 업데이트
        existing_vote.time_list = vote.time_list
        existing_vote.is_available = vote.is_available
        if hasattr(vote, 'memo'):
            existing_vote.memo = vote.memo
        db.commit()
        db.refresh(existing_vote)
        # 투표 수 업데이트
        update_vote_count(db, vote.time_candidate_id)
        return existing_vote
    
    # 새 투표 생성
    db_vote = TimeVote(
        participant_id=vote.participant_id,
        meeting_id=vote.meeting_id,
        time_candidate_id=vote.time_candidate_id,
        time_list=vote.time_list,
        is_available=vote.is_available,
        memo=getattr(vote, 'memo', None),
    )
    db.add(db_vote)
    db.commit()
    db.refresh(db_vote)
    # 투표 수 업데이트
    update_vote_count(db, vote.time_candidate_id)
    return db_vote


def update_time_vote(db: Session, vote_id: UUID, vote_update: TimeVoteUpdate) -> Optional[TimeVote]:
    """투표 정보 업데이트"""
    db_vote = get_time_vote(db, vote_id)
    if not db_vote:
        return None
    
    if vote_update.time_list is not None:
        db_vote.time_list = vote_update.time_list
    if vote_update.is_available is not None:
        db_vote.is_available = vote_update.is_available
    if vote_update.memo is not None:
        db_vote.memo = vote_update.memo
    
    db.commit()
    db.refresh(db_vote)
    # 투표 수 업데이트
    update_vote_count(db, db_vote.time_candidate_id)
    return db_vote


def delete_time_vote(db: Session, vote_id: UUID) -> bool:
    """투표 삭제"""
    db_vote = get_time_vote(db, vote_id)
    if not db_vote:
        return False
    
    candidate_id = db_vote.time_candidate_id
    db.delete(db_vote)
    db.commit()
    # 투표 수 업데이트
    update_vote_count(db, candidate_id)
    return True

