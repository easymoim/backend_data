from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import crud
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.meeting import MeetingSummaryResponse

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """새 사용자 생성"""
    # 이메일 중복 확인
    db_user = crud.user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 이메일입니다."
        )
    
    # OAuth 중복 확인
    db_user = crud.user.get_user_by_oauth(
        db, oauth_provider=user.oauth_provider, oauth_id=user.oauth_id
    )
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 OAuth 계정입니다."
        )
    
    return crud.user.create_user(db=db, user=user)


@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """사용자 조회"""
    db_user = crud.user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    return db_user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """사용자 정보 업데이트"""
    db_user = crud.user.update_user(db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    return db_user


@router.get("/{user_id}/meetings/summary", response_model=MeetingSummaryResponse)
def get_meetings_summary(user_id: int, db: Session = Depends(get_db)):
    """사용자의 모임 요약 조회 (호스트/참가자 모두 포함)"""
    try:
        # 사용자 존재 확인
        db_user = crud.user.get_user(db, user_id=user_id)
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
        
        # 모임 요약 조회
        meetings_data = crud.meeting.get_meetings_summary_by_user(db, user_id=user_id)
        
        return {"meetings": meetings_data}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"❌ 에러 발생: {str(e)}")
        print(f"상세 에러:\n{error_detail}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"모임 요약 조회 중 오류가 발생했습니다: {str(e)}"
        )

