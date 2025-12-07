from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app import crud
from app.schemas.place_vote import PlaceVoteCreate, PlaceVoteUpdate, PlaceVoteResponse

router = APIRouter()


@router.post("/", response_model=PlaceVoteResponse, status_code=status.HTTP_201_CREATED)
def create_place_vote(vote: PlaceVoteCreate, db: Session = Depends(get_db)):
    """새 장소 투표 생성 (이미 존재하면 업데이트)"""
    # 참가자 존재 확인
    db_participant = crud.participant.get_participant(db, participant_id=vote.participant_id)
    if not db_participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="참가자를 찾을 수 없습니다."
        )
    
    # 시간 후보 존재 확인
    db_candidate = crud.meeting_time_candidate.get_time_candidate(
        db, candidate_id=vote.time_candidate_id
    )
    if not db_candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="시간 후보를 찾을 수 없습니다."
        )
    
    # 모임 ID 일치 확인
    if (
        db_participant.meeting_id != vote.meeting_id
        or db_candidate.meeting_id != vote.meeting_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="참가자, 시간 후보, 모임 ID가 일치하지 않습니다."
        )
    
    return crud.place_vote.create_place_vote(db=db, vote=vote)


@router.get("/participant/{participant_id}", response_model=List[PlaceVoteResponse])
def read_place_votes_by_participant(participant_id: UUID, db: Session = Depends(get_db)):
    """참가자별 장소 투표 목록 조회"""
    votes = crud.place_vote.get_place_votes_by_participant(db, participant_id=participant_id)
    return votes


@router.get("/meeting/{meeting_id}", response_model=List[PlaceVoteResponse])
def read_place_votes_by_meeting(meeting_id: UUID, db: Session = Depends(get_db)):
    """모임별 장소 투표 목록 조회"""
    votes = crud.place_vote.get_place_votes_by_meeting(db, meeting_id=meeting_id)
    return votes


@router.get("/{vote_id}", response_model=PlaceVoteResponse)
def read_place_vote(vote_id: UUID, db: Session = Depends(get_db)):
    """장소 투표 조회"""
    db_vote = crud.place_vote.get_place_vote(db, vote_id=vote_id)
    if db_vote is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="장소 투표를 찾을 수 없습니다."
        )
    return db_vote


@router.put("/{vote_id}", response_model=PlaceVoteResponse)
def update_place_vote(
    vote_id: UUID, vote_update: PlaceVoteUpdate, db: Session = Depends(get_db)
):
    """장소 투표 정보 업데이트"""
    db_vote = crud.place_vote.update_place_vote(db, vote_id=vote_id, vote_update=vote_update)
    if db_vote is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="장소 투표를 찾을 수 없습니다."
        )
    return db_vote


@router.delete("/{vote_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_place_vote(vote_id: UUID, db: Session = Depends(get_db)):
    """장소 투표 삭제"""
    success = crud.place_vote.delete_place_vote(db, vote_id=vote_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="장소 투표를 찾을 수 없습니다."
        )
    return None

