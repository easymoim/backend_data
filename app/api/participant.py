from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app import crud
from app.schemas.participant import ParticipantCreate, ParticipantUpdate, ParticipantResponse

router = APIRouter()


@router.post("/", response_model=ParticipantResponse, status_code=status.HTTP_201_CREATED)
def create_participant(participant: ParticipantCreate, db: Session = Depends(get_db)):
    """새 참가자 생성"""
    # 모임 존재 확인
    db_meeting = crud.meeting.get_meeting(db, meeting_id=participant.meeting_id)
    if not db_meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="모임을 찾을 수 없습니다."
        )
    
    # 사용자 존재 확인 (user_id가 있는 경우)
    if participant.user_id:
        db_user = crud.user.get_user(db, user_id=participant.user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
    
    return crud.participant.create_participant(db=db, participant=participant)


@router.get("/meeting/{meeting_id}", response_model=List[ParticipantResponse])
def read_participants_by_meeting(meeting_id: UUID, db: Session = Depends(get_db)):
    """모임별 참가자 목록 조회"""
    participants = crud.participant.get_participants_by_meeting(db, meeting_id=meeting_id)
    return participants


@router.get("/user/{user_id}", response_model=List[ParticipantResponse])
def read_participants_by_user(user_id: int, db: Session = Depends(get_db)):
    """사용자별 참가한 모임 목록 조회"""
    participants = crud.participant.get_participants_by_user(db, user_id=user_id)
    return participants


@router.get("/{participant_id}", response_model=ParticipantResponse)
def read_participant(participant_id: UUID, db: Session = Depends(get_db)):
    """참가자 조회"""
    db_participant = crud.participant.get_participant(db, participant_id=participant_id)
    if db_participant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="참가자를 찾을 수 없습니다."
        )
    return db_participant


@router.put("/{participant_id}", response_model=ParticipantResponse)
def update_participant(participant_id: UUID, participant_update: ParticipantUpdate, db: Session = Depends(get_db)):
    """참가자 정보 업데이트"""
    db_participant = crud.participant.update_participant(
        db, participant_id=participant_id, participant_update=participant_update
    )
    if db_participant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="참가자를 찾을 수 없습니다."
        )
    return db_participant


@router.delete("/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_participant(participant_id: UUID, db: Session = Depends(get_db)):
    """참가자 삭제"""
    success = crud.participant.delete_participant(db, participant_id=participant_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="참가자를 찾을 수 없습니다."
        )
    return None

