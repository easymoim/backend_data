from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models.place_vote import PlaceVote
from app.schemas.place_vote import PlaceVoteCreate, PlaceVoteUpdate


def get_place_vote(db: Session, vote_id: UUID) -> Optional[PlaceVote]:
    """장소 투표 ID로 조회"""
    return db.query(PlaceVote).filter(PlaceVote.id == vote_id).first()


def get_place_votes_by_participant(db: Session, participant_id: UUID) -> List[PlaceVote]:
    """참가자별 장소 투표 목록 조회"""
    return db.query(PlaceVote).filter(PlaceVote.participant_id == participant_id).all()


def get_place_votes_by_meeting(db: Session, meeting_id: UUID) -> List[PlaceVote]:
    """모임별 장소 투표 목록 조회"""
    return db.query(PlaceVote).filter(PlaceVote.meeting_id == meeting_id).all()


def get_place_votes_by_time_candidate(db: Session, time_candidate_id: UUID) -> List[PlaceVote]:
    """시간 후보별 장소 투표 목록 조회"""
    return db.query(PlaceVote).filter(PlaceVote.time_candidate_id == time_candidate_id).all()


def create_place_vote(db: Session, vote: PlaceVoteCreate) -> PlaceVote:
    """새 장소 투표 생성 (이미 존재하면 업데이트)"""
    # 기존 투표 확인 (participant_id와 time_candidate_id 조합)
    existing_vote = db.query(PlaceVote).filter(
        PlaceVote.participant_id == vote.participant_id,
        PlaceVote.time_candidate_id == vote.time_candidate_id
    ).first()
    
    if existing_vote:
        # 기존 투표 업데이트
        if vote.is_available is not None:
            existing_vote.is_available = vote.is_available
        if vote.memo is not None:
            existing_vote.memo = vote.memo
        db.commit()
        db.refresh(existing_vote)
        return existing_vote
    
    # 새 투표 생성
    db_vote = PlaceVote(
        participant_id=vote.participant_id,
        meeting_id=vote.meeting_id,
        time_candidate_id=vote.time_candidate_id,
        is_available=vote.is_available,
        memo=vote.memo,
    )
    db.add(db_vote)
    db.commit()
    db.refresh(db_vote)
    return db_vote


def update_place_vote(
    db: Session, vote_id: UUID, vote_update: PlaceVoteUpdate
) -> Optional[PlaceVote]:
    """장소 투표 정보 업데이트"""
    db_vote = get_place_vote(db, vote_id)
    if not db_vote:
        return None
    
    if vote_update.is_available is not None:
        db_vote.is_available = vote_update.is_available
    if vote_update.memo is not None:
        db_vote.memo = vote_update.memo
    
    db.commit()
    db.refresh(db_vote)
    return db_vote


def delete_place_vote(db: Session, vote_id: UUID) -> bool:
    """장소 투표 삭제"""
    db_vote = get_place_vote(db, vote_id)
    if not db_vote:
        return False
    
    db.delete(db_vote)
    db.commit()
    return True

