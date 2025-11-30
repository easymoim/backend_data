"""
데이터 수집 및 분석 서비스

모임 참가자들의 정보를 수집하고, 중심 위치와 검색 키워드를 도출합니다.

1단계: 데이터 수집 및 분석 (Data Collection & Analysis)
- 참석자와 모임 관련 정보 로드
- 중심 위치 계산
- 선호도 집계 및 키워드 변환
"""

from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from .schemas import (
    MeetingContext,
    CenterLocation,
    ParticipantLocation,
    PlacePreference,
    SearchKeyword,
    LocationChoiceType,
)
from .keyword_generator import KeywordGenerator
from .kakao_client import KakaoLocalClient
from .station_utils import get_station_coordinates, get_district_from_station


class MeetingDataCollector:
    """
    모임 데이터 수집 및 분석 서비스
    
    이 클래스는 1단계(데이터 수집 및 분석)의 핵심 로직을 담당합니다.
    """
    
    def __init__(
        self, 
        db: Optional[Session] = None,
        kakao_client: Optional[KakaoLocalClient] = None,
    ):
        """
        Args:
            db: SQLAlchemy 데이터베이스 세션
            kakao_client: 카카오 API 클라이언트
        """
        self.db = db
        self.kakao_client = kakao_client
        self.keyword_generator = KeywordGenerator()
    
    # ============================================================
    # 메인 API
    # ============================================================
    
    async def collect_and_analyze(
        self, 
        meeting_id: UUID
    ) -> tuple[MeetingContext, list[SearchKeyword]]:
        """
        모임 ID로 데이터를 수집하고 분석하여 검색 키워드 생성
        
        Args:
            meeting_id: 모임 ID
            
        Returns:
            (MeetingContext, 검색 키워드 리스트) 튜플
        """
        # 1. 모임 및 참가자 정보 로드
        context = await self.load_meeting_context(meeting_id)
        
        # 2. 중심 위치 계산
        if context.participant_locations:
            center = await self.calculate_center_location(
                context.participant_locations
            )
            context.center_location = center
        
        # 3. 검색 키워드 생성
        keywords = self.keyword_generator.generate_keywords(context)
        
        return context, keywords
    
    async def analyze_from_data(
        self,
        purpose: str,
        participant_locations: list[dict],
        preferences: list[PlacePreference],
        expected_count: int = 4,
        is_multi_stage: bool = False,
        candidate_times: Optional[list[str]] = None,
        # 장소 선택 방식 관련
        location_choice_type: str = "center",
        preferred_district: Optional[str] = None,
        district_votes: Optional[dict[str, int]] = None,
        preferred_station: Optional[str] = None,
        station_votes: Optional[dict[str, int]] = None,
    ) -> tuple[MeetingContext, list[SearchKeyword]]:
        """
        직접 데이터를 전달받아 분석 (DB 없이 사용 가능)
        
        3가지 장소 선택 방식 지원:
        - center: 중간위치 찾기 (참가자 위치 기반)
        - district: 선호 지역 선택 (구/동 투표)
        - station: 선호 지하철역 (역 근처)
        
        Args:
            purpose: 모임 목적 (dining, cafe, drink, etc)
            participant_locations: 참가자 위치 정보 리스트
            preferences: 참가자 선호도 리스트
            expected_count: 예상 참가자 수
            is_multi_stage: 1차/2차 등 여러 단계 여부
            candidate_times: 후보 시간 리스트
            location_choice_type: 장소 선택 방식 ("center", "district", "station")
            preferred_district: 선호 지역 (district 방식)
            district_votes: 지역별 투표 수 (district 방식)
            preferred_station: 선호 지하철역 (station 방식)
            station_votes: 역별 투표 수 (station 방식)
            
        Returns:
            (MeetingContext, 검색 키워드 리스트) 튜플
        """
        from uuid import uuid4
        
        choice_type = LocationChoiceType(location_choice_type)
        
        # ParticipantLocation 객체로 변환
        locations = [
            ParticipantLocation(
                participant_id=uuid4(),
                address=loc.get("address"),
                latitude=loc.get("latitude"),
                longitude=loc.get("longitude"),
                district=loc.get("district"),
            )
            for loc in participant_locations
        ]
        
        # 선호도 집계
        aggregated = self.keyword_generator.aggregate_preferences(preferences)
        
        # 장소 선택 방식에 따른 중심 위치 계산
        center = await self._calculate_location_by_choice_type(
            choice_type=choice_type,
            participant_locations=locations,
            preferred_district=preferred_district,
            preferred_station=preferred_station,
        )
        
        # MeetingContext 생성
        context = MeetingContext(
            meeting_id=uuid4(),
            purpose=purpose,
            location_choice_type=choice_type,
            center_location=center,
            participant_locations=locations,
            # 선호 지역/역 정보
            preferred_district=preferred_district,
            district_votes=district_votes,
            preferred_station=preferred_station,
            station_votes=station_votes,
            # 선호도
            aggregated_preferences=aggregated,
            expected_participant_count=expected_count,
            is_multi_stage=is_multi_stage,
            candidate_times=candidate_times or [],
        )
        
        # 키워드 생성
        keywords = self.keyword_generator.generate_keywords(context)
        
        return context, keywords
    
    async def _calculate_location_by_choice_type(
        self,
        choice_type: LocationChoiceType,
        participant_locations: list[ParticipantLocation],
        preferred_district: Optional[str] = None,
        preferred_station: Optional[str] = None,
    ) -> Optional[CenterLocation]:
        """
        장소 선택 방식에 따른 중심 위치 계산
        
        Args:
            choice_type: 장소 선택 방식
            participant_locations: 참가자 위치 리스트
            preferred_district: 선호 지역
            preferred_station: 선호 지하철역
            
        Returns:
            CenterLocation
        """
        if choice_type == LocationChoiceType.CENTER_LOCATION:
            # 중간위치 방식: 참가자 위치의 중심점
            return await self.calculate_center_location(participant_locations)
        
        elif choice_type == LocationChoiceType.PREFERENCE_AREA:
            # 선호 지역 방식: 해당 지역의 중심
            if preferred_district:
                return await self._get_district_center(preferred_district)
            return None
        
        elif choice_type == LocationChoiceType.PREFERENCE_SUBWAY:
            # 선호 지하철역 방식: 역 좌표
            if preferred_station and self.kakao_client:
                return await get_station_coordinates(preferred_station, self.kakao_client)
            elif preferred_station:
                # 카카오 클라이언트 없으면 지역구만 추출
                district = get_district_from_station(preferred_station)
                return CenterLocation(
                    latitude=0.0,
                    longitude=0.0,
                    district=district,
                )
            return None
        
        return None
    
    async def _get_district_center(self, district: str) -> Optional[CenterLocation]:
        """
        지역구의 중심 좌표 조회
        
        Args:
            district: 지역구 이름 (예: "강남구")
            
        Returns:
            CenterLocation
        """
        if not self.kakao_client:
            return CenterLocation(
                latitude=0.0,
                longitude=0.0,
                district=district,
            )
        
        # 카카오 API로 지역 검색
        try:
            result = await self.kakao_client.search_address(f"서울 {district}")
            documents = result.get("documents", [])
            
            if documents:
                doc = documents[0]
                return CenterLocation(
                    latitude=float(doc["y"]),
                    longitude=float(doc["x"]),
                    address=doc.get("address_name"),
                    district=district,
                )
        except Exception as e:
            print(f"지역 중심 좌표 조회 실패 '{district}': {e}")
        
        return CenterLocation(
            latitude=0.0,
            longitude=0.0,
            district=district,
        )
    
    # ============================================================
    # 데이터 로드 메서드
    # ============================================================
    
    async def load_meeting_context(self, meeting_id: UUID) -> MeetingContext:
        """
        데이터베이스에서 모임 컨텍스트 로드
        
        Args:
            meeting_id: 모임 ID
            
        Returns:
            MeetingContext 객체
        """
        if not self.db:
            raise ValueError("데이터베이스 세션이 필요합니다.")
        
        # 지연 임포트 (순환 참조 방지)
        from app.models import Meeting, Participant, MeetingTimeCandidate
        
        # 모임 조회
        meeting = self.db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            raise ValueError(f"모임을 찾을 수 없습니다: {meeting_id}")
        
        # 참가자 조회
        participants = self.db.query(Participant).filter(
            Participant.meeting_id == meeting_id
        ).all()
        
        # 시간 후보 조회
        time_candidates = self.db.query(MeetingTimeCandidate).filter(
            MeetingTimeCandidate.meeting_id == meeting_id
        ).all()
        
        # ParticipantLocation 리스트 생성
        participant_locations = []
        for p in participants:
            if p.location:
                loc = ParticipantLocation(
                    participant_id=p.id,
                    address=p.location,
                )
                participant_locations.append(loc)
        
        # MeetingContext 생성
        context = MeetingContext(
            meeting_id=meeting.id,
            purpose=meeting.purpose.value if meeting.purpose else "dining",
            title=meeting.title,
            description=meeting.description,
            participant_locations=participant_locations,
            expected_participant_count=len(participants) or 4,
            candidate_times=[
                tc.candidate_time.isoformat() 
                for tc in time_candidates
            ],
        )
        
        return context
    
    # ============================================================
    # 중심 위치 계산
    # ============================================================
    
    async def calculate_center_location(
        self, 
        locations: list[ParticipantLocation]
    ) -> Optional[CenterLocation]:
        """
        참가자들의 위치로부터 중심 위치 계산
        
        Args:
            locations: 참가자 위치 리스트
            
        Returns:
            중심 위치 CenterLocation 객체
        """
        if not locations:
            return None
        
        # 좌표가 있는 참가자들 필터링
        coords = [
            (loc.latitude, loc.longitude)
            for loc in locations
            if loc.latitude is not None and loc.longitude is not None
        ]
        
        # 좌표가 없으면 주소로 변환 시도
        if not coords and self.kakao_client:
            for loc in locations:
                if loc.address:
                    center = await self.kakao_client.get_address_coordinates(
                        loc.address
                    )
                    if center:
                        coords.append((center.latitude, center.longitude))
        
        if not coords:
            # 지역구만이라도 추출
            districts = [loc.district for loc in locations if loc.district]
            if districts:
                # 가장 많이 나온 지역구 사용
                from collections import Counter
                most_common = Counter(districts).most_common(1)[0][0]
                return CenterLocation(
                    latitude=0.0,
                    longitude=0.0,
                    district=most_common,
                )
            return None
        
        # 좌표 평균 계산 (단순 중심점)
        avg_lat = sum(c[0] for c in coords) / len(coords)
        avg_lon = sum(c[1] for c in coords) / len(coords)
        
        # 중심 좌표의 지역구 조회
        district = None
        if self.kakao_client:
            district = await self.kakao_client.get_region_from_coordinates(
                avg_lat, avg_lon
            )
        
        return CenterLocation(
            latitude=avg_lat,
            longitude=avg_lon,
            district=district,
        )
    
    def calculate_center_simple(
        self, 
        coordinates: list[tuple[float, float]]
    ) -> tuple[float, float]:
        """
        좌표 리스트의 단순 중심점 계산 (동기 버전)
        
        Args:
            coordinates: (위도, 경도) 튜플 리스트
            
        Returns:
            (중심 위도, 중심 경도) 튜플
        """
        if not coordinates:
            raise ValueError("좌표가 필요합니다.")
        
        avg_lat = sum(c[0] for c in coordinates) / len(coordinates)
        avg_lon = sum(c[1] for c in coordinates) / len(coordinates)
        
        return (avg_lat, avg_lon)
    
    # ============================================================
    # 선호도 집계
    # ============================================================
    
    def aggregate_preferences(
        self, 
        preferences: list[PlacePreference]
    ) -> dict[str, dict[str, int]]:
        """
        참가자들의 선호도 집계 (KeywordGenerator 위임)
        
        Args:
            preferences: 참가자 선호도 리스트
            
        Returns:
            집계된 선호도 딕셔너리
        """
        return self.keyword_generator.aggregate_preferences(preferences)
    
    def get_top_preferences(
        self,
        aggregated: dict[str, dict[str, int]],
        top_n: int = 1
    ) -> dict[str, list[str]]:
        """
        각 카테고리별 상위 N개 선호도 반환
        
        Args:
            aggregated: 집계된 선호도
            top_n: 각 카테고리별 반환할 항목 수
            
        Returns:
            카테고리별 상위 항목 리스트
        """
        result = {}
        for category in ["food_types", "atmospheres", "conditions"]:
            top_items = self.keyword_generator.get_top_items(
                aggregated, category, top_n
            )
            result[category] = [item[0] for item in top_items]
        return result


# ============================================================
# 편의 함수
# ============================================================

async def collect_meeting_data(
    meeting_id: UUID,
    db: Session,
    kakao_api_key: Optional[str] = None,
) -> tuple[MeetingContext, list[SearchKeyword]]:
    """
    모임 데이터 수집 및 분석 편의 함수
    
    Args:
        meeting_id: 모임 ID
        db: 데이터베이스 세션
        kakao_api_key: 카카오 REST API 키 (선택)
        
    Returns:
        (MeetingContext, 검색 키워드 리스트) 튜플
    """
    kakao_client = None
    if kakao_api_key:
        kakao_client = KakaoLocalClient(api_key=kakao_api_key)
    
    collector = MeetingDataCollector(db=db, kakao_client=kakao_client)
    return await collector.collect_and_analyze(meeting_id)


async def analyze_meeting_data(
    purpose: str,
    locations: list[dict],
    preferences: list[dict],
    expected_count: int = 4,
    kakao_api_key: Optional[str] = None,
    # 장소 선택 방식
    location_choice_type: str = "center_location",
    preferred_district: Optional[str] = None,
    district_votes: Optional[dict[str, int]] = None,
    preferred_station: Optional[str] = None,
    station_votes: Optional[dict[str, int]] = None,
) -> tuple[MeetingContext, list[SearchKeyword]]:
    """
    직접 데이터로 분석하는 편의 함수 (DB 없이 사용)
    
    3가지 장소 선택 방식 지원:
    - center_location: 중간위치 찾기 (참가자 위치 기반)
    - preference_area: 선호 지역 선택 (구/동 투표)
    - preference_subway: 선호 지하철역 (역 근처)
    
    Args:
        purpose: 모임 목적
        locations: 참가자 위치 리스트
        preferences: 참가자 선호도 리스트 (딕셔너리 형태)
        expected_count: 예상 참가자 수
        kakao_api_key: 카카오 REST API 키 (선택)
        location_choice_type: 장소 선택 방식 ("center", "district", "station")
        preferred_district: 선호 지역 (예: "강남구")
        district_votes: 지역별 투표 수
        preferred_station: 선호 지하철역 (예: "강남")
        station_votes: 역별 투표 수
        
    Returns:
        (MeetingContext, 검색 키워드 리스트) 튜플
        
    Example (중간위치 방식):
        >>> context, keywords = await analyze_meeting_data(
        ...     purpose="dining",
        ...     locations=[{"address": "서울 강남구 역삼동"}],
        ...     preferences=[{"food_types": ["korean"]}],
        ...     location_choice_type="center",
        ... )
        
    Example (선호 지역 방식):
        >>> context, keywords = await analyze_meeting_data(
        ...     purpose="dining",
        ...     locations=[],
        ...     preferences=[{"food_types": ["korean"]}],
        ...     location_choice_type="district",
        ...     preferred_district="강남구",
        ...     district_votes={"강남구": 3, "서초구": 2},
        ... )
        
    Example (선호 지하철역 방식):
        >>> context, keywords = await analyze_meeting_data(
        ...     purpose="dining",
        ...     locations=[],
        ...     preferences=[{"food_types": ["korean"]}],
        ...     location_choice_type="station",
        ...     preferred_station="홍대입구",
        ...     station_votes={"홍대입구": 4, "강남": 2},
        ... )
    """
    kakao_client = None
    if kakao_api_key:
        kakao_client = KakaoLocalClient(api_key=kakao_api_key)
    
    # 딕셔너리를 PlacePreference로 변환
    from .schemas import FoodType, AtmosphereType, ConditionType
    
    pref_objects = []
    for pref in preferences:
        pref_objects.append(PlacePreference(
            food_types=[FoodType(f) for f in pref.get("food_types", [])],
            atmospheres=[AtmosphereType(a) for a in pref.get("atmospheres", [])],
            conditions=[ConditionType(c) for c in pref.get("conditions", [])],
        ))
    
    collector = MeetingDataCollector(kakao_client=kakao_client)
    return await collector.analyze_from_data(
        purpose=purpose,
        participant_locations=locations,
        preferences=pref_objects,
        expected_count=expected_count,
        location_choice_type=location_choice_type,
        preferred_district=preferred_district,
        district_votes=district_votes,
        preferred_station=preferred_station,
        station_votes=station_votes,
    )

