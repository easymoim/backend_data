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


def get_place_vote_by_participant_and_meeting(
    db: Session, participant_id: UUID, meeting_id: UUID
) -> Optional[PlaceVote]:
    """참가자와 모임으로 장소 투표 조회"""
    return db.query(PlaceVote).filter(
        PlaceVote.participant_id == participant_id,
        PlaceVote.meeting_id == meeting_id
    ).first()


def create_place_vote(db: Session, vote: PlaceVoteCreate) -> PlaceVote:
    """새 장소 투표 생성 (이미 존재하면 업데이트)"""
    # 기존 투표 확인 (participant_id와 meeting_id 조합)
    existing_vote = db.query(PlaceVote).filter(
        PlaceVote.participant_id == vote.participant_id,
        PlaceVote.meeting_id == vote.meeting_id
    ).first()
    
    if existing_vote:
        # 기존 투표 업데이트
        existing_vote.place_list = vote.place_list
        db.commit()
        db.refresh(existing_vote)
        return existing_vote
    
    # 새 투표 생성
    db_vote = PlaceVote(
        participant_id=vote.participant_id,
        meeting_id=vote.meeting_id,
        place_list=vote.place_list,
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
    
    if vote_update.place_list is not None:
        db_vote.place_list = vote_update.place_list
    
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

