from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.place import Place
from app.schemas.place import PlaceCreate, PlaceUpdate


def get_place(db: Session, place_id: str) -> Optional[Place]:
    """장소 ID로 조회"""
    return db.query(Place).filter(Place.id == place_id).first()


def get_all_places(db: Session, skip: int = 0, limit: int = 100) -> List[Place]:
    """모든 장소 목록 조회"""
    return db.query(Place).offset(skip).limit(limit).all()


def create_place(db: Session, place: PlaceCreate) -> Place:
    """새 장소 생성"""
    db_place = Place(
        id=place.id,
        name=place.name,
        category=place.category,
        address=place.address,
        location=place.location,
        rating=place.rating,
        thumbnail=place.thumbnail,
    )
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    return db_place


def update_place(db: Session, place_id: str, place_update: PlaceUpdate) -> Optional[Place]:
    """장소 정보 업데이트"""
    db_place = get_place(db, place_id)
    if not db_place:
        return None
    
    if place_update.name is not None:
        db_place.name = place_update.name
    if place_update.category is not None:
        db_place.category = place_update.category
    if place_update.address is not None:
        db_place.address = place_update.address
    if place_update.location is not None:
        db_place.location = place_update.location
    if place_update.rating is not None:
        db_place.rating = place_update.rating
    if place_update.thumbnail is not None:
        db_place.thumbnail = place_update.thumbnail
    
    db.commit()
    db.refresh(db_place)
    return db_place


def delete_place(db: Session, place_id: str) -> bool:
    """장소 삭제"""
    db_place = get_place(db, place_id)
    if not db_place:
        return False
    
    db.delete(db_place)
    db.commit()
    return True

