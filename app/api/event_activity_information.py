from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.database import get_db
from app import crud
from app.schemas.event_activity_information import (
    EventActivityInformationResponse,
)

router = APIRouter()


@router.get("/", response_model=List[EventActivityInformationResponse])
def read_event_activity_informations(
    skip: int = Query(0, ge=0, description="건너뛸 레코드 수"),
    limit: int = Query(100, ge=1, le=1000, description="반환할 최대 레코드 수"),
    category: Optional[str] = Query(None, description="카테고리 필터"),
    city_name: Optional[str] = Query(None, description="도시명 필터"),
    guname: Optional[str] = Query(None, description="구 이름 필터"),
    start_date: Optional[datetime] = Query(None, description="시작 날짜 필터 (정확한 일치)"),
    start_date_from: Optional[datetime] = Query(None, description="시작 날짜 범위 시작 (이상)"),
    start_date_to: Optional[datetime] = Query(None, description="시작 날짜 범위 종료 (이하)"),
    db: Session = Depends(get_db),
):
    """이벤트/활동 정보 목록 조회 (필터링 옵션 포함)"""
    # 필터 조건에 따라 다른 함수 호출
    if start_date:
        # 정확한 날짜로 필터링
        events = crud.event_activity_information.get_event_activity_informations_by_start_date(
            db, start_date=start_date, skip=skip, limit=limit
        )
    elif start_date_from or start_date_to:
        # 날짜 범위로 필터링
        events = crud.event_activity_information.get_event_activity_informations_by_start_date_range(
            db, start_date_from=start_date_from, start_date_to=start_date_to, skip=skip, limit=limit
        )
    elif category:
        events = crud.event_activity_information.get_event_activity_informations_by_category(
            db, category=category, skip=skip, limit=limit
        )
    elif city_name:
        events = crud.event_activity_information.get_event_activity_informations_by_city(
            db, city_name=city_name, skip=skip, limit=limit
        )
    elif guname:
        events = crud.event_activity_information.get_event_activity_informations_by_guname(
            db, guname=guname, skip=skip, limit=limit
        )
    else:
        events = crud.event_activity_information.get_all_event_activity_informations(
            db, skip=skip, limit=limit
        )
    return events


@router.get("/{event_id}", response_model=EventActivityInformationResponse)
def read_event_activity_information(
    event_id: UUID, db: Session = Depends(get_db)
):
    """이벤트/활동 정보 조회"""
    db_event = crud.event_activity_information.get_event_activity_information(
        db, event_id=event_id
    )
    if db_event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="이벤트/활동 정보를 찾을 수 없습니다.",
        )
    return db_event

