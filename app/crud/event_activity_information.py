from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.models.event_activity_information import EventActivityInformation
from app.schemas.event_activity_information import (
    EventActivityInformationCreate,
    EventActivityInformationUpdate,
)


def get_event_activity_information(
    db: Session, event_id: UUID
) -> Optional[EventActivityInformation]:
    """이벤트 ID로 조회"""
    return db.query(EventActivityInformation).filter(EventActivityInformation.id == event_id).first()


def get_all_event_activity_informations(
    db: Session, skip: int = 0, limit: int = 100
) -> List[EventActivityInformation]:
    """모든 이벤트/활동 정보 목록 조회"""
    return db.query(EventActivityInformation).offset(skip).limit(limit).all()


def get_event_activity_informations_by_category(
    db: Session, category: str, skip: int = 0, limit: int = 100
) -> List[EventActivityInformation]:
    """카테고리로 이벤트/활동 정보 조회"""
    return (
        db.query(EventActivityInformation)
        .filter(EventActivityInformation.category == category)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_event_activity_informations_by_city(
    db: Session, city_name: str, skip: int = 0, limit: int = 100
) -> List[EventActivityInformation]:
    """도시명으로 이벤트/활동 정보 조회"""
    return (
        db.query(EventActivityInformation)
        .filter(EventActivityInformation.city_name == city_name)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_event_activity_informations_by_guname(
    db: Session, guname: str, skip: int = 0, limit: int = 100
) -> List[EventActivityInformation]:
    """구 이름으로 이벤트/활동 정보 조회"""
    return (
        db.query(EventActivityInformation)
        .filter(EventActivityInformation.guname == guname)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_event_activity_informations_by_start_date(
    db: Session, start_date: datetime, skip: int = 0, limit: int = 100
) -> List[EventActivityInformation]:
    """시작 날짜로 이벤트/활동 정보 조회"""
    return (
        db.query(EventActivityInformation)
        .filter(EventActivityInformation.start_date == start_date)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_event_activity_informations_by_start_date_range(
    db: Session, start_date_from: Optional[datetime] = None, start_date_to: Optional[datetime] = None, skip: int = 0, limit: int = 100
) -> List[EventActivityInformation]:
    """시작 날짜 범위로 이벤트/활동 정보 조회"""
    query = db.query(EventActivityInformation)
    
    if start_date_from:
        query = query.filter(EventActivityInformation.start_date >= start_date_from)
    if start_date_to:
        query = query.filter(EventActivityInformation.start_date <= start_date_to)
    
    return query.offset(skip).limit(limit).all()


def create_event_activity_information(
    db: Session, event: EventActivityInformationCreate
) -> EventActivityInformation:
    """새 이벤트/활동 정보 생성"""
    db_event = EventActivityInformation(
        category=event.category,
        city_name=event.city_name,
        guname=event.guname,
        title=event.title,
        date=event.date,
        place=event.place,
        organization_name=event.organization_name,
        use_target=event.use_target,
        use_fee=event.use_fee,
        inquiry=event.inquiry,
        program_info=event.program_info,
        organization_link=event.organization_link,
        thumbnail_image=event.thumbnail_image,
        host_type=event.host_type,
        start_date=event.start_date,
        end_date=event.end_date,
        longitude=event.longitude,
        latitude=event.latitude,
        is_free=event.is_free,
        hompage_link=event.hompage_link,
        program_time=event.program_time,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def update_event_activity_information(
    db: Session,
    event_id: UUID,
    event_update: EventActivityInformationUpdate,
) -> Optional[EventActivityInformation]:
    """이벤트/활동 정보 업데이트"""
    db_event = get_event_activity_information(db, event_id)
    if not db_event:
        return None

    if event_update.category is not None:
        db_event.category = event_update.category
    if event_update.city_name is not None:
        db_event.city_name = event_update.city_name
    if event_update.guname is not None:
        db_event.guname = event_update.guname
    if event_update.title is not None:
        db_event.title = event_update.title
    if event_update.date is not None:
        db_event.date = event_update.date
    if event_update.place is not None:
        db_event.place = event_update.place
    if event_update.organization_name is not None:
        db_event.organization_name = event_update.organization_name
    if event_update.use_target is not None:
        db_event.use_target = event_update.use_target
    if event_update.use_fee is not None:
        db_event.use_fee = event_update.use_fee
    if event_update.inquiry is not None:
        db_event.inquiry = event_update.inquiry
    if event_update.program_info is not None:
        db_event.program_info = event_update.program_info
    if event_update.organization_link is not None:
        db_event.organization_link = event_update.organization_link
    if event_update.thumbnail_image is not None:
        db_event.thumbnail_image = event_update.thumbnail_image
    if event_update.host_type is not None:
        db_event.host_type = event_update.host_type
    if event_update.start_date is not None:
        db_event.start_date = event_update.start_date
    if event_update.end_date is not None:
        db_event.end_date = event_update.end_date
    if event_update.latitude is not None:
        db_event.latitude = event_update.latitude
    if event_update.longitude is not None:
        db_event.longitude = event_update.longitude
    if event_update.is_free is not None:
        db_event.is_free = event_update.is_free
    if event_update.hompage_link is not None:
        db_event.hompage_link = event_update.hompage_link
    if event_update.program_time is not None:
        db_event.program_time = event_update.program_time

    db.commit()
    db.refresh(db_event)
    return db_event


def delete_event_activity_information(db: Session, event_id: UUID) -> bool:
    """이벤트/활동 정보 삭제"""
    db_event = get_event_activity_information(db, event_id)
    if not db_event:
        return False

    db.delete(db_event)
    db.commit()
    return True

