from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app import crud
from app.schemas.place_candidate import (
    PlaceCandidateCreate,
    PlaceCandidateUpdate,
    PlaceCandidateResponse,
)

router = APIRouter()


@router.post("/", response_model=PlaceCandidateResponse, status_code=status.HTTP_201_CREATED)
def create_place_candidate(candidate: PlaceCandidateCreate, db: Session = Depends(get_db)):
    """새 장소 후보 생성"""
    # 모임 존재 확인
    db_meeting = crud.meeting.get_meeting(db, meeting_id=candidate.meeting_id)
    if not db_meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="모임을 찾을 수 없습니다."
        )
    
    return crud.place_candidate.create_place_candidate(db=db, candidate=candidate)


@router.get("/meeting/{meeting_id}", response_model=List[PlaceCandidateResponse])
def read_place_candidates_by_meeting(meeting_id: UUID, db: Session = Depends(get_db)):
    """모임별 장소 후보 목록 조회"""
    candidates = crud.place_candidate.get_place_candidates_by_meeting(db, meeting_id=meeting_id)
    return candidates


@router.get("/{candidate_id}", response_model=PlaceCandidateResponse)
def read_place_candidate(candidate_id: str, db: Session = Depends(get_db)):
    """장소 후보 조회"""
    db_candidate = crud.place_candidate.get_place_candidate(db, candidate_id=candidate_id)
    if db_candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="장소 후보를 찾을 수 없습니다."
        )
    return db_candidate


@router.put("/{candidate_id}", response_model=PlaceCandidateResponse)
def update_place_candidate(
    candidate_id: str, candidate_update: PlaceCandidateUpdate, db: Session = Depends(get_db)
):
    """장소 후보 정보 업데이트"""
    db_candidate = crud.place_candidate.update_place_candidate(
        db, candidate_id=candidate_id, candidate_update=candidate_update
    )
    if db_candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="장소 후보를 찾을 수 없습니다."
        )
    return db_candidate


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_place_candidate(candidate_id: str, db: Session = Depends(get_db)):
    """장소 후보 삭제"""
    success = crud.place_candidate.delete_place_candidate(db, candidate_id=candidate_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="장소 후보를 찾을 수 없습니다."
        )
    return None

