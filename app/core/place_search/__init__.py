"""
장소 검색 모듈

이 모듈은 모임 참가자들의 정보를 기반으로 최적의 장소를 검색하는 기능을 제공합니다.

주요 구성:
- kakao_client: 카카오 로컬 API 클라이언트
- data_collector: 데이터 수집 및 분석 (1단계)
- keyword_generator: 검색 키워드 생성
- place_searcher: 장소 검색 및 필터링 (2단계)
- llm_recommender: LLM 기반 장소 추천 (3단계)
- station_utils: 지하철역 유틸리티
- schemas: 데이터 스키마 정의

장소 선택 방식:
- center: 중간위치 찾기 (참가자 위치 기반)
- district: 선호 지역 선택 (구/동 투표)
- station: 선호 지하철역 (역 근처)
"""

from .kakao_client import KakaoLocalClient
from .data_collector import MeetingDataCollector, analyze_meeting_data, collect_meeting_data
from .keyword_generator import KeywordGenerator
from .place_searcher import PlaceSearcher, search_places_by_keywords, quick_search
from .llm_recommender import (
    LLMRecommender,
    recommend_places,
    full_recommendation_pipeline,
)
from .station_utils import (
    get_station_coordinates,
    get_district_from_station,
)
from .schemas import (
    # 장소 선택 방식
    LocationChoiceType,
    # 선호도 관련
    PlacePreference,
    MeetingContext,
    SearchKeyword,
    CenterLocation,
    KakaoPlaceResult,
    FoodType,
    AtmosphereType,
    ConditionType,
    ParticipantLocation,
    # LLM 추천 관련
    PlaceCandidate,
    PlaceRecommendation,
    LLMRecommendationResult,
    LLMPromptContext,
)

__all__ = [
    # 클라이언트 & 서비스
    "KakaoLocalClient",
    "MeetingDataCollector", 
    "KeywordGenerator",
    "PlaceSearcher",
    "LLMRecommender",
    # 편의 함수
    "search_places_by_keywords",
    "quick_search",
    "recommend_places",
    "full_recommendation_pipeline",
    "analyze_meeting_data",
    "collect_meeting_data",
    # 지하철역 유틸리티
    "get_station_coordinates",
    "get_district_from_station",
    # 스키마
    "LocationChoiceType",
    "PlacePreference",
    "MeetingContext",
    "SearchKeyword",
    "CenterLocation",
    "KakaoPlaceResult",
    "FoodType",
    "AtmosphereType",
    "ConditionType",
    "ParticipantLocation",
    # LLM 추천 관련
    "PlaceCandidate",
    "PlaceRecommendation",
    "LLMRecommendationResult",
    "LLMPromptContext",
]

