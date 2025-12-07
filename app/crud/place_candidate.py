from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models.place_candidate import PlaceCandidate, LocationType
from app.schemas.place_candidate import PlaceCandidateCreate, PlaceCandidateUpdate


def get_place_candidate(db: Session, candidate_id: str) -> Optional[PlaceCandidate]:
    """장소 후보 ID로 조회"""
    return db.query(PlaceCandidate).filter(PlaceCandidate.id == candidate_id).first()


def get_place_candidates_by_meeting(db: Session, meeting_id: UUID) -> List[PlaceCandidate]:
    """모임별 장소 후보 목록 조회"""
    return db.query(PlaceCandidate).filter(PlaceCandidate.meeting_id == meeting_id).all()


def create_place_candidate(db: Session, candidate: PlaceCandidateCreate) -> PlaceCandidate:
    """새 장소 후보 생성"""
    # location_type 문자열을 Enum으로 변환
    location_type_enum = None
    if candidate.location_type:
        try:
            location_type_enum = LocationType(candidate.location_type)
        except ValueError:
            # 유효하지 않은 값인 경우 None으로 설정
            location_type_enum = None
    
    db_candidate = PlaceCandidate(
        id=candidate.id,
        meeting_id=candidate.meeting_id,
        location=candidate.location,
        preference_subway=candidate.preference_subway,
        preference_area=candidate.preference_area,
        food=candidate.food,
        condition=candidate.condition,
        location_type=location_type_enum,
    )
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate


def update_place_candidate(
    db: Session, candidate_id: str, candidate_update: PlaceCandidateUpdate
) -> Optional[PlaceCandidate]:
    """장소 후보 정보 업데이트"""
    db_candidate = get_place_candidate(db, candidate_id)
    if not db_candidate:
        return None
    
    if candidate_update.location is not None:
        db_candidate.location = candidate_update.location
    if candidate_update.preference_subway is not None:
        db_candidate.preference_subway = candidate_update.preference_subway
    if candidate_update.preference_area is not None:
        db_candidate.preference_area = candidate_update.preference_area
    if candidate_update.food is not None:
        db_candidate.food = candidate_update.food
    if candidate_update.condition is not None:
        db_candidate.condition = candidate_update.condition
    if candidate_update.location_type is not None:
        try:
            db_candidate.location_type = LocationType(candidate_update.location_type)
        except ValueError:
            # 유효하지 않은 값인 경우 None으로 설정
            db_candidate.location_type = None
    
    db.commit()
    db.refresh(db_candidate)
    return db_candidate


def delete_place_candidate(db: Session, candidate_id: str) -> bool:
    """장소 후보 삭제"""
    db_candidate = get_place_candidate(db, candidate_id)
    if not db_candidate:
        return False
    
    db.delete(db_candidate)
    db.commit()
    return True

