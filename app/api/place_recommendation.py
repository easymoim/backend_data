"""
장소 추천 API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
import os

from app.database import get_db
from app import crud
from app.schemas.place_recommendation import (
    PlaceRecommendationRequest,
    PlaceRecommendationResponse,
    RecommendedPlace,
)
from app.schemas.place_candidate import PlaceCandidateUpdate
from app.core.place_search import full_recommendation_pipeline
from app.models import PlaceCandidate
from app.models.place_candidate import LocationType

router = APIRouter()


@router.post("/recommend", response_model=PlaceRecommendationResponse)
async def recommend_places(
    request: PlaceRecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    모임 정보를 기반으로 장소 추천
    
    1. meeting과 participants 정보를 가져옴
    2. 장소 추천 파이프라인 실행
    3. 추천 결과를 place_candidate 테이블에 저장
    4. 추천 결과 반환
    """
    # 1. 모임 정보 조회
    meeting = crud.meeting.get_meeting(db, meeting_id=request.meeting_id)
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="모임을 찾을 수 없습니다."
        )
    
    # 2. 참가자 정보 조회
    participants = crud.participant.get_participants_by_meeting(
        db, meeting_id=request.meeting_id
    )
    
    if not participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="참가자 정보가 없습니다."
        )
    
    # 3. 입력 데이터 추출
    input_data = _extract_input_from_db(meeting, participants)
    
    # 4. 장소 추천 파이프라인 실행
    # 환경변수에서 API 키 가져오기
    kakao_api_key = os.getenv("KAKAO_REST_API_KEY")
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    if not kakao_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="KAKAO_REST_API_KEY 환경변수가 설정되지 않았습니다."
        )
    
    if not gemini_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GEMINI_API_KEY 환경변수가 설정되지 않았습니다."
        )
    
    try:
        result = await full_recommendation_pipeline(
            purpose=input_data["purpose"],
            locations=input_data["locations"],
            preferences=input_data["preferences"],
            expected_count=input_data["expected_count"],
            top_n=request.top_n,
            kakao_api_key=kakao_api_key,
            gemini_api_key=gemini_api_key,
            location_choice_type=input_data["location_choice_type"],
            preferred_district=input_data.get("preferred_district"),
            district_votes=input_data.get("district_votes"),
            preferred_station=input_data.get("preferred_station"),
            station_votes=input_data.get("station_votes"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"장소 추천 중 오류가 발생했습니다: {str(e)}"
        )
    
    recommendations_data = result["recommendations"]
    keywords = result["keywords"]
    places = result["places"]
    
    # 5. place_candidate 테이블에 저장
    location_json = {
        "recommendations": [
            {
                "rank": rec.rank,
                "place_id": rec.place_id,
                "place_name": rec.place_name,
                "reason": rec.reason,
                "match_score": rec.match_score,
                "matched_preferences": rec.matched_preferences,
                "address": rec.address,
                "address_jibun": rec.address_jibun,
                "latitude": rec.latitude,
                "longitude": rec.longitude,
                "phone": rec.phone,
                "place_url": rec.place_url,
                "category": rec.category,
                "distance": rec.distance,
            }
            for rec in recommendations_data.recommendations
        ],
        "summary": recommendations_data.summary,
        "model_used": recommendations_data.model_used,
        "search_keywords": [kw.keyword for kw in keywords],
        "total_candidates": len(places),
    }
    
    candidate_id = (
        recommendations_data.recommendations[0].place_id 
        if recommendations_data.recommendations else "unknown"
    )
    
    # DB에 저장 (기존 데이터가 있으면 업데이트)
    existing_candidate = crud.place_candidate.get_place_candidate(
        db, candidate_id=candidate_id
    )
    
    if existing_candidate:
        # 업데이트 - location_type은 반드시 소문자여야 함
        location_type_value = str(input_data["location_choice_type"]).lower()
        update_data = PlaceCandidateUpdate(
            location=location_json,
            preference_subway=[input_data.get("preferred_station")] if input_data.get("preferred_station") else None,
            preference_area=[input_data.get("preferred_district")] if input_data.get("preferred_district") else None,
            location_type=location_type_value,
        )
        place_candidate = crud.place_candidate.update_place_candidate(
            db,
            candidate_id=candidate_id,
            candidate_update=update_data
        )
    else:
        # 새로 생성 - location_type은 반드시 소문자여야 함 (DB enum이 소문자만 허용)
        raw_location_type = input_data["location_choice_type"]
        location_type_value = str(raw_location_type).lower() if raw_location_type else "center_location"
        
        # 디버그 로그
        print(f"[DEBUG] raw_location_type: {raw_location_type}")
        print(f"[DEBUG] location_type_value (after lower): {location_type_value}")
        
        place_candidate = PlaceCandidate(
            id=candidate_id,
            meeting_id=request.meeting_id,
            location=location_json,
            preference_subway=[input_data.get("preferred_station")] if input_data.get("preferred_station") else None,
            preference_area=[input_data.get("preferred_district")] if input_data.get("preferred_district") else None,
            location_type=location_type_value,
        )
        db.add(place_candidate)
    
    db.commit()
    db.refresh(place_candidate)
    
    # 6. 응답 생성
    return PlaceRecommendationResponse(
        meeting_id=request.meeting_id,
        recommendations=[
            RecommendedPlace(
                rank=rec.rank,
                place_id=rec.place_id,
                place_name=rec.place_name,
                reason=rec.reason,
                match_score=rec.match_score,
                matched_preferences=rec.matched_preferences,
                address=rec.address,
                address_jibun=rec.address_jibun,
                latitude=rec.latitude,
                longitude=rec.longitude,
                phone=rec.phone,
                place_url=rec.place_url,
                category=rec.category,
                distance=rec.distance,
            )
            for rec in recommendations_data.recommendations
        ],
        summary=recommendations_data.summary,
        center_location=recommendations_data.center_location,
        model_used=recommendations_data.model_used,
        search_keywords=[kw.keyword for kw in keywords],
        total_candidates=len(places),
        place_candidate_id=candidate_id,
    )


def _extract_input_from_db(meeting, participants: List) -> dict:
    """
    DB 데이터에서 추천 파이프라인 인풋 추출
    """
    # 1. 장소 선택 방식
    if meeting.location_choice_type:
        raw_value = meeting.location_choice_type.value if hasattr(meeting.location_choice_type, "value") else meeting.location_choice_type
        location_choice_type = str(raw_value).lower()
    else:
        location_choice_type = "center_location"
    
    # 2. 참가자 위치 정보
    locations = []
    for p in participants:
        if p.location:
            locations.append({
                "address": p.location,
                "district": None,
            })
    
    # 3. 참가자 선호도
    preferences = []
    for p in participants:
        if p.preference_place:
            pref = p.preference_place if isinstance(p.preference_place, dict) else {}
            
            # food_types 추출
            food = pref.get("food", [])
            food_types = food if isinstance(food, list) else [food] if food else []
            
            # atmospheres 추출
            mood = pref.get("mood", [])
            atmospheres = mood if isinstance(mood, list) else [mood] if mood else []
            
            # conditions 추출
            condition = pref.get("condition", [])
            conditions = condition if isinstance(condition, list) else [condition] if condition else []
            
            preferences.append({
                "food_types": food_types,
                "atmospheres": atmospheres,
                "conditions": conditions,
            })
    
    # 4. 모임 전체 선호도 (참가자 선호도가 없으면 사용)
    if meeting.preference_place and not preferences:
        pref = meeting.preference_place
        food = pref.get("food", [])
        food_types = food if isinstance(food, list) else [food] if food else []
        mood = pref.get("mood", [])
        atmospheres = mood if isinstance(mood, list) else [mood] if mood else []
        condition = pref.get("condition", [])
        conditions = condition if isinstance(condition, list) else [condition] if condition else []
        
        preferences.append({
            "food_types": food_types,
            "atmospheres": atmospheres,
            "conditions": conditions,
        })
    
    # 기본 선호도 설정 (선호도가 하나도 없으면)
    if not preferences:
        preferences = [{"food_types": ["한식"], "atmospheres": [], "conditions": []}]
    
    # 5. 선호 지역/역 정보
    preferred_district = None
    preferred_station = None
    district_votes = None
    station_votes = None
    
    if meeting.location_choice_value:
        if location_choice_type == "preference_area":
            preferred_district = meeting.location_choice_value
        elif location_choice_type == "preference_subway":
            preferred_station = meeting.location_choice_value
    
    # 6. 모임 목적
    purpose = "dining"  # 기본값
    if meeting.purpose:
        if isinstance(meeting.purpose, list) and meeting.purpose:
            purpose = meeting.purpose[0]
        elif isinstance(meeting.purpose, str):
            purpose = meeting.purpose
    
    return {
        "purpose": purpose,
        "locations": locations,
        "preferences": preferences,
        "expected_count": meeting.expected_participant_count or len(participants) or 4,
        "location_choice_type": location_choice_type,
        "preferred_district": preferred_district,
        "district_votes": district_votes,
        "preferred_station": preferred_station,
        "station_votes": station_votes,
    }

