from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app import crud
from app.schemas.meeting import MeetingCreate, MeetingUpdate, MeetingResponse

router = APIRouter()


@router.post("/", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
def create_meeting(meeting: MeetingCreate, creator_id: int, db: Session = Depends(get_db)):
    """새 모임 생성"""
    # 생성자 존재 확인
    db_user = crud.user.get_user(db, user_id=creator_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="생성자를 찾을 수 없습니다."
        )
    
    return crud.meeting.create_meeting(db=db, meeting=meeting, creator_id=creator_id)


@router.get("/", response_model=List[MeetingResponse])
def read_meetings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """모든 모임 목록 조회"""
    meetings = crud.meeting.get_all_meetings(db, skip=skip, limit=limit)
    return meetings


@router.get("/creator/{creator_id}", response_model=List[MeetingResponse])
def read_meetings_by_creator(creator_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """생성자별 모임 목록 조회"""
    meetings = crud.meeting.get_meetings_by_creator(db, creator_id=creator_id, skip=skip, limit=limit)
    return meetings


@router.get("/share-code/{share_code}", response_model=MeetingResponse)
def read_meeting_by_share_code(share_code: str, db: Session = Depends(get_db)):
    """공유 코드로 모임 조회"""
    db_meeting = crud.meeting.get_meeting_by_share_code(db, share_code=share_code)
    if db_meeting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="모임을 찾을 수 없습니다."
        )
    return db_meeting


@router.get("/{meeting_id}", response_model=MeetingResponse)
def read_meeting(meeting_id: UUID, db: Session = Depends(get_db)):
    """모임 조회"""
    db_meeting = crud.meeting.get_meeting(db, meeting_id=meeting_id)
    if db_meeting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="모임을 찾을 수 없습니다."
        )
    return db_meeting


@router.put("/{meeting_id}", response_model=MeetingResponse)
def update_meeting(meeting_id: UUID, meeting_update: MeetingUpdate, db: Session = Depends(get_db)):
    """모임 정보 업데이트"""
    db_meeting = crud.meeting.update_meeting(db, meeting_id=meeting_id, meeting_update=meeting_update)
    if db_meeting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="모임을 찾을 수 없습니다."
        )
    return db_meeting


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meeting(meeting_id: UUID, db: Session = Depends(get_db)):
    """모임 삭제"""
    success = crud.meeting.delete_meeting(db, meeting_id=meeting_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="모임을 찾을 수 없습니다."
        )
    return None

