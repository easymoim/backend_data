from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app import crud
from app.schemas.meeting_time_candidate import (
    MeetingTimeCandidateCreate,
    MeetingTimeCandidateResponse,
)

router = APIRouter()


@router.post("/", response_model=MeetingTimeCandidateResponse, status_code=status.HTTP_201_CREATED)
def create_time_candidate(candidate: MeetingTimeCandidateCreate, db: Session = Depends(get_db)):
    """새 시간 후보 생성"""
    # 모임 존재 확인
    db_meeting = crud.meeting.get_meeting(db, meeting_id=candidate.meeting_id)
    if not db_meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="모임을 찾을 수 없습니다."
        )
    
    return crud.meeting_time_candidate.create_time_candidate(db=db, candidate=candidate)


@router.get("/meeting/{meeting_id}", response_model=List[MeetingTimeCandidateResponse])
def read_time_candidates_by_meeting(meeting_id: UUID, db: Session = Depends(get_db)):
    """모임별 시간 후보 목록 조회"""
    candidates = crud.meeting_time_candidate.get_time_candidates_by_meeting(db, meeting_id=meeting_id)
    return candidates


@router.get("/{candidate_id}", response_model=MeetingTimeCandidateResponse)
def read_time_candidate(candidate_id: UUID, db: Session = Depends(get_db)):
    """시간 후보 조회"""
    db_candidate = crud.meeting_time_candidate.get_time_candidate(db, candidate_id=candidate_id)
    if db_candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="시간 후보를 찾을 수 없습니다."
        )
    return db_candidate


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_time_candidate(candidate_id: UUID, db: Session = Depends(get_db)):
    """시간 후보 삭제"""
    success = crud.meeting_time_candidate.delete_time_candidate(db, candidate_id=candidate_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="시간 후보를 찾을 수 없습니다."
        )
    return None

