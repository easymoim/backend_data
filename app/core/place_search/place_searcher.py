"""
장소 검색 및 필터링 서비스

2단계: 장소 검색 및 필터링 (Place Search & Filtering)
- 다중 키워드로 카카오 API 검색
- 결과 병합 및 중복 제거
- 후보군 관리

API 문서: https://developers.kakao.com/docs/latest/ko/local/dev-guide#search-by-keyword
"""

import asyncio
from typing import Optional
from uuid import UUID

from .kakao_client import KakaoLocalClient
from .schemas import (
    SearchKeyword,
    KakaoPlaceResult,
    CenterLocation,
    MeetingContext,
)
from .keyword_generator import KeywordGenerator
from .data_collector import MeetingDataCollector


class PlaceSearcher:
    """
    장소 검색 서비스
    
    키워드 리스트로 카카오 API를 호출하고 결과를 병합/중복제거합니다.
    """
    
    def __init__(self, kakao_client: Optional[KakaoLocalClient] = None):
        """
        Args:
            kakao_client: 카카오 API 클라이언트. 없으면 자동 생성
        """
        self.kakao_client = kakao_client or KakaoLocalClient()
        self.keyword_generator = KeywordGenerator()
    
    # ============================================================
    # 메인 검색 API
    # ============================================================
    
    async def search_places(
        self,
        keywords: list[SearchKeyword],
        center: Optional[CenterLocation] = None,
        radius: int = 5000,
        max_results_per_keyword: int = 15,
    ) -> list[KakaoPlaceResult]:
        """
        여러 키워드로 장소 검색 후 결과 병합
        
        Args:
            keywords: 검색 키워드 리스트
            center: 중심 위치 (있으면 거리순 정렬 가능)
            radius: 검색 반경 (미터, 최대 20000)
            max_results_per_keyword: 키워드당 최대 결과 수
            
        Returns:
            중복 제거된 장소 결과 리스트
        """
        all_results: list[KakaoPlaceResult] = []
        
        # 각 키워드로 병렬 검색
        tasks = [
            self._search_single_keyword(
                keyword=kw.keyword,
                center=center,
                radius=radius,
                size=max_results_per_keyword,
            )
            for kw in keywords
        ]
        
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 수집 (에러는 무시)
        for results in results_list:
            if isinstance(results, list):
                all_results.extend(results)
        
        # 중복 제거 (place_id 기준)
        unique_results = self._deduplicate_places(all_results)
        
        return unique_results
    
    async def search_by_context(
        self,
        context: MeetingContext,
        radius: int = 5000,
        max_keywords: int = 5,
        max_results_per_keyword: int = 15,
    ) -> list[KakaoPlaceResult]:
        """
        MeetingContext로 직접 검색
        
        Args:
            context: 모임 컨텍스트
            radius: 검색 반경
            max_keywords: 사용할 최대 키워드 수
            max_results_per_keyword: 키워드당 최대 결과 수
            
        Returns:
            장소 검색 결과 리스트
        """
        # 키워드 생성
        keywords = self.keyword_generator.generate_keywords(
            context, 
            max_keywords=max_keywords
        )
        
        # 검색 실행
        return await self.search_places(
            keywords=keywords,
            center=context.center_location,
            radius=radius,
            max_results_per_keyword=max_results_per_keyword,
        )
    
    async def search_simple(
        self,
        query: str,
        district: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius: int = 5000,
        size: int = 15,
    ) -> list[KakaoPlaceResult]:
        """
        단일 키워드로 간단 검색
        
        Args:
            query: 검색 키워드
            district: 지역구 (키워드에 추가)
            latitude: 중심 위도
            longitude: 중심 경도
            radius: 검색 반경
            size: 결과 개수
            
        Returns:
            장소 검색 결과 리스트
        """
        # 지역구가 있으면 키워드에 추가
        search_query = f"{district} {query}" if district else query
        
        center = None
        if latitude and longitude:
            center = CenterLocation(
                latitude=latitude,
                longitude=longitude,
                district=district,
            )
        
        return await self._search_single_keyword(
            keyword=search_query,
            center=center,
            radius=radius,
            size=size,
        )
    
    # ============================================================
    # 전체 파이프라인 (1단계 + 2단계)
    # ============================================================
    
    async def full_search_pipeline(
        self,
        purpose: str,
        locations: list[dict],
        preferences: list[dict],
        expected_count: int = 4,
        radius: int = 5000,
        max_keywords: int = 5,
        # 장소 선택 방식
        location_choice_type: str = "center_location",
        preferred_district: Optional[str] = None,
        district_votes: Optional[dict[str, int]] = None,
        preferred_station: Optional[str] = None,
        station_votes: Optional[dict[str, int]] = None,
    ) -> dict:
        """
        전체 검색 파이프라인 실행 (데이터 수집 → 키워드 생성 → 장소 검색)
        
        3가지 장소 선택 방식 지원:
        - center: 중간위치 찾기 (참가자 위치 기반)
        - district: 선호 지역 선택 (구/동 투표)
        - station: 선호 지하철역 (역 근처)
        
        Args:
            purpose: 모임 목적 (dining, cafe, drink, etc)
            locations: 참가자 위치 리스트 (center 방식일 때 필요)
            preferences: 참가자 선호도 리스트
            expected_count: 예상 참가자 수
            radius: 검색 반경
            max_keywords: 최대 키워드 수
            location_choice_type: 장소 선택 방식 ("center", "district", "station")
            preferred_district: 선호 지역 (예: "강남구") - district 방식
            district_votes: 지역별 투표 수 - district 방식
            preferred_station: 선호 지하철역 (예: "강남") - station 방식
            station_votes: 역별 투표 수 - station 방식
            
        Returns:
            {
                "context": MeetingContext,
                "keywords": list[SearchKeyword],
                "places": list[KakaoPlaceResult],
            }
        """
        from .data_collector import analyze_meeting_data
        
        # 1단계: 데이터 수집 및 분석 (장소 선택 방식에 따라 처리)
        context, keywords = await analyze_meeting_data(
            purpose=purpose,
            locations=locations,
            preferences=preferences,
            expected_count=expected_count,
            kakao_api_key=self.kakao_client.api_key,
            location_choice_type=location_choice_type,
            preferred_district=preferred_district,
            district_votes=district_votes,
            preferred_station=preferred_station,
            station_votes=station_votes,
        )
        
        # 2단계: 장소 검색
        places = await self.search_places(
            keywords=keywords[:max_keywords],
            center=context.center_location,
            radius=radius,
        )
        
        return {
            "context": context,
            "keywords": keywords,
            "places": places,
        }
    
    # ============================================================
    # 카테고리 기반 검색
    # ============================================================
    
    async def search_by_category(
        self,
        category_code: str,
        center: CenterLocation,
        radius: int = 5000,
        size: int = 15,
    ) -> list[KakaoPlaceResult]:
        """
        카테고리 코드로 장소 검색
        
        Args:
            category_code: 카테고리 그룹 코드
                - FD6: 음식점
                - CE7: 카페
                - AT4: 관광명소
                - AD5: 숙박
            center: 중심 위치 (필수)
            radius: 검색 반경
            size: 결과 개수
            
        Returns:
            장소 검색 결과 리스트
        """
        response = await self.kakao_client.search_by_category(
            category_group_code=category_code,
            x=str(center.longitude),
            y=str(center.latitude),
            radius=radius,
            size=size,
        )
        
        return self.kakao_client.parse_place_results(response)
    
    async def search_restaurants(
        self,
        center: CenterLocation,
        radius: int = 5000,
        size: int = 15,
    ) -> list[KakaoPlaceResult]:
        """음식점 카테고리 검색"""
        return await self.search_by_category("FD6", center, radius, size)
    
    async def search_cafes(
        self,
        center: CenterLocation,
        radius: int = 5000,
        size: int = 15,
    ) -> list[KakaoPlaceResult]:
        """카페 카테고리 검색"""
        return await self.search_by_category("CE7", center, radius, size)
    
    # ============================================================
    # 헬퍼 메서드
    # ============================================================
    
    async def _search_single_keyword(
        self,
        keyword: str,
        center: Optional[CenterLocation] = None,
        radius: int = 5000,
        size: int = 15,
    ) -> list[KakaoPlaceResult]:
        """
        단일 키워드로 카카오 API 검색
        
        Args:
            keyword: 검색 키워드
            center: 중심 위치
            radius: 검색 반경
            size: 결과 개수
            
        Returns:
            장소 검색 결과 리스트
        """
        try:
            # 좌표가 유효한 경우에만 사용 (0.0은 무효한 좌표로 간주)
            x = None
            y = None
            if center and center.latitude != 0.0 and center.longitude != 0.0:
                x = str(center.longitude)
                y = str(center.latitude)
            
            response = await self.kakao_client.search_by_keyword(
                query=keyword,
                x=x,
                y=y,
                radius=radius,
                size=size,
            )
            
            return self.kakao_client.parse_place_results(response)
            
        except Exception as e:
            # 개별 키워드 검색 실패는 로깅만 하고 빈 리스트 반환
            print(f"키워드 검색 실패 '{keyword}': {e}")
            return []
    
    def _deduplicate_places(
        self, 
        places: list[KakaoPlaceResult]
    ) -> list[KakaoPlaceResult]:
        """
        장소 ID 기준으로 중복 제거
        
        Args:
            places: 장소 리스트
            
        Returns:
            중복 제거된 장소 리스트
        """
        seen: dict[str, KakaoPlaceResult] = {}
        for place in places:
            if place.id not in seen:
                seen[place.id] = place
        return list(seen.values())
    
    def filter_by_category(
        self,
        places: list[KakaoPlaceResult],
        category_keywords: list[str],
    ) -> list[KakaoPlaceResult]:
        """
        카테고리 이름으로 필터링
        
        Args:
            places: 장소 리스트
            category_keywords: 포함할 카테고리 키워드 리스트 (예: ["한식", "고기"])
            
        Returns:
            필터링된 장소 리스트
        """
        if not category_keywords:
            return places
        
        return [
            place for place in places
            if any(kw in place.category_name for kw in category_keywords)
        ]
    
    def sort_by_distance(
        self, 
        places: list[KakaoPlaceResult]
    ) -> list[KakaoPlaceResult]:
        """
        거리순으로 정렬 (distance 필드가 있는 경우)
        
        Args:
            places: 장소 리스트
            
        Returns:
            거리순 정렬된 장소 리스트
        """
        def get_distance(place: KakaoPlaceResult) -> float:
            if place.distance:
                try:
                    return float(place.distance)
                except ValueError:
                    pass
            return float('inf')
        
        return sorted(places, key=get_distance)


# ============================================================
# 편의 함수
# ============================================================

async def search_places_by_keywords(
    keywords: list[str],
    district: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius: int = 5000,
) -> list[KakaoPlaceResult]:
    """
    키워드 리스트로 장소 검색하는 편의 함수
    
    Args:
        keywords: 검색 키워드 문자열 리스트
        district: 지역구
        latitude: 중심 위도
        longitude: 중심 경도
        radius: 검색 반경
        
    Returns:
        장소 검색 결과 리스트
        
    Example:
        >>> places = await search_places_by_keywords(
        ...     keywords=["강남구 한식 맛집", "강남구 분위기 좋은 식당"],
        ...     latitude=37.4979,
        ...     longitude=127.0276,
        ... )
    """
    searcher = PlaceSearcher()
    
    search_keywords = [
        SearchKeyword(keyword=kw, priority=i+1)
        for i, kw in enumerate(keywords)
    ]
    
    center = None
    if latitude and longitude:
        center = CenterLocation(
            latitude=latitude,
            longitude=longitude,
            district=district,
        )
    
    return await searcher.search_places(
        keywords=search_keywords,
        center=center,
        radius=radius,
    )


async def quick_search(
    query: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius: int = 5000,
) -> list[KakaoPlaceResult]:
    """
    빠른 단일 키워드 검색
    
    Args:
        query: 검색 키워드
        latitude: 중심 위도
        longitude: 중심 경도
        radius: 검색 반경
        
    Returns:
        장소 검색 결과 리스트
    """
    searcher = PlaceSearcher()
    return await searcher.search_simple(
        query=query,
        latitude=latitude,
        longitude=longitude,
        radius=radius,
    )

