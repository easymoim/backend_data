from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import crud
from app.schemas.place import PlaceCreate, PlaceUpdate, PlaceResponse

router = APIRouter()


@router.post("/", response_model=PlaceResponse, status_code=status.HTTP_201_CREATED)
def create_place(place: PlaceCreate, db: Session = Depends(get_db)):
    """새 장소 생성"""
    # 이미 존재하는 장소인지 확인
    db_place = crud.place.get_place(db, place_id=place.id)
    if db_place:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 장소입니다."
        )
    
    return crud.place.create_place(db=db, place=place)


@router.get("/", response_model=List[PlaceResponse])
def read_places(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """모든 장소 목록 조회"""
    places = crud.place.get_all_places(db, skip=skip, limit=limit)
    return places


@router.get("/{place_id}", response_model=PlaceResponse)
def read_place(place_id: str, db: Session = Depends(get_db)):
    """장소 조회"""
    db_place = crud.place.get_place(db, place_id=place_id)
    if db_place is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="장소를 찾을 수 없습니다."
        )
    return db_place


@router.put("/{place_id}", response_model=PlaceResponse)
def update_place(place_id: str, place_update: PlaceUpdate, db: Session = Depends(get_db)):
    """장소 정보 업데이트"""
    db_place = crud.place.update_place(db, place_id=place_id, place_update=place_update)
    if db_place is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="장소를 찾을 수 없습니다."
        )
    return db_place


@router.delete("/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_place(place_id: str, db: Session = Depends(get_db)):
    """장소 삭제"""
    success = crud.place.delete_place(db, place_id=place_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="장소를 찾을 수 없습니다."
        )
    return None

