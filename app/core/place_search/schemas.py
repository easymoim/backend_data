"""
장소 검색 관련 스키마 정의
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from uuid import UUID


# ============================================================
# 선호도 관련 Enum
# ============================================================

class FoodType(str, Enum):
    """음식 종류"""
    KOREAN = "korean"           # 한식
    JAPANESE = "japanese"       # 일식
    CHINESE = "chinese"         # 중식
    WESTERN = "western"         # 양식
    ASIAN = "asian"             # 아시안
    MEAT = "meat"               # 고기/구이
    SEAFOOD = "seafood"         # 해산물
    CHICKEN = "chicken"         # 치킨
    PIZZA = "pizza"             # 피자
    CAFE = "cafe"               # 카페/디저트
    BAR = "bar"                 # 술집/바
    ETC = "etc"                 # 기타


class AtmosphereType(str, Enum):
    """분위기"""
    QUIET = "quiet"                     # 조용한
    LIVELY = "lively"                   # 활기찬
    ROMANTIC = "romantic"               # 로맨틱한
    MODERN = "modern"                   # 모던한
    TRADITIONAL = "traditional"         # 전통적인
    COZY = "cozy"                       # 아늑한
    SPACIOUS = "spacious"               # 넓은
    PRIVATE = "private"                 # 프라이빗


class ConditionType(str, Enum):
    """조건"""
    PARKING = "parking"                 # 주차 가능
    PRIVATE_ROOM = "private_room"       # 룸/개인실
    GROUP_FRIENDLY = "group_friendly"   # 단체 가능
    PET_FRIENDLY = "pet_friendly"       # 반려동물 동반
    WHEELCHAIR = "wheelchair"           # 휠체어 이용
    RESERVATION = "reservation"         # 예약 가능
    LATE_NIGHT = "late_night"           # 심야 영업


# ============================================================
# 데이터 모델
# ============================================================

class PlacePreference(BaseModel):
    """참가자 장소 선호도"""
    food_types: list[FoodType] = Field(default_factory=list, description="선호 음식 종류")
    atmospheres: list[AtmosphereType] = Field(default_factory=list, description="선호 분위기")
    conditions: list[ConditionType] = Field(default_factory=list, description="필요 조건")


class CenterLocation(BaseModel):
    """중심 위치 정보"""
    latitude: float = Field(..., description="위도")
    longitude: float = Field(..., description="경도")
    address: Optional[str] = Field(None, description="주소")
    district: Optional[str] = Field(None, description="지역구 (예: 강남구)")
    
    @property
    def coordinates(self) -> tuple[float, float]:
        """(위도, 경도) 튜플 반환"""
        return (self.latitude, self.longitude)


class ParticipantLocation(BaseModel):
    """참가자 위치 정보"""
    participant_id: UUID
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    district: Optional[str] = None  # 지역구


class MeetingContext(BaseModel):
    """모임 컨텍스트 정보 (검색에 필요한 모든 정보를 담음)"""
    meeting_id: UUID
    purpose: str = Field(..., description="모임 목적 (dining, cafe, drink, etc)")
    title: Optional[str] = None
    description: Optional[str] = None
    
    # 위치 정보
    center_location: Optional[CenterLocation] = None
    participant_locations: list[ParticipantLocation] = Field(default_factory=list)
    
    # 선호도 집계 결과
    aggregated_preferences: Optional[dict] = Field(
        default=None, 
        description="집계된 선호도 (food_types, atmospheres, conditions 각각의 카운트)"
    )
    
    # 모임 조건
    expected_participant_count: int = Field(default=4, description="예상 참가자 수")
    is_multi_stage: bool = Field(default=False, description="1차, 2차 등 여러 단계 여부")
    
    # 시간 정보
    candidate_times: list[str] = Field(default_factory=list, description="후보 시간들")


class SearchKeyword(BaseModel):
    """검색 키워드"""
    keyword: str = Field(..., description="검색 키워드")
    priority: int = Field(default=1, description="우선순위 (1이 가장 높음)")
    category: Optional[str] = Field(None, description="키워드 카테고리")


class KakaoPlaceResult(BaseModel):
    """카카오 장소 검색 결과"""
    id: str = Field(..., description="장소 ID")
    place_name: str = Field(..., description="장소명")
    category_name: str = Field(..., description="카테고리 이름")
    category_group_code: Optional[str] = Field(None, description="카테고리 그룹 코드")
    category_group_name: Optional[str] = Field(None, description="카테고리 그룹명")
    phone: Optional[str] = Field(None, description="전화번호")
    address_name: str = Field(..., description="지번 주소")
    road_address_name: Optional[str] = Field(None, description="도로명 주소")
    x: str = Field(..., description="경도 (longitude)")
    y: str = Field(..., description="위도 (latitude)")
    place_url: str = Field(..., description="장소 상세 페이지 URL")
    distance: Optional[str] = Field(None, description="중심좌표까지의 거리 (미터)")

    @property
    def latitude(self) -> float:
        return float(self.y)
    
    @property
    def longitude(self) -> float:
        return float(self.x)


class KeywordSearchParams(BaseModel):
    """카카오 키워드 검색 파라미터"""
    query: str = Field(..., description="검색 키워드")
    x: Optional[str] = Field(None, description="중심 좌표 경도")
    y: Optional[str] = Field(None, description="중심 좌표 위도")
    radius: int = Field(default=5000, description="검색 반경 (미터, 최대 20000)")
    page: int = Field(default=1, description="페이지 번호 (1~45)")
    size: int = Field(default=15, description="한 페이지에 보여질 문서 수 (1~15)")
    sort: str = Field(default="accuracy", description="정렬 기준 (accuracy, distance)")


# ============================================================
# LLM 추천 관련 스키마
# ============================================================

class PlaceCandidate(BaseModel):
    """LLM에 전달할 장소 후보 정보 (검색 결과 + 추가 정보)"""
    id: str = Field(..., description="장소 ID (카카오)")
    place_name: str = Field(..., description="장소명")
    category: str = Field(..., description="카테고리 (예: 음식점 > 한식 > 한정식)")
    address: str = Field(..., description="주소")
    phone: Optional[str] = Field(None, description="전화번호")
    distance: Optional[int] = Field(None, description="중심점에서의 거리 (미터)")
    place_url: str = Field(..., description="카카오맵 상세 URL")
    
    # 블로그/웹 검색으로 수집한 추가 정보
    blog_snippets: list[str] = Field(default_factory=list, description="블로그 리뷰 요약")
    extracted_keywords: list[str] = Field(default_factory=list, description="추출된 키워드 (분위기, 특징)")
    has_reviews: bool = Field(default=False, description="리뷰 존재 여부")
    
    # 추가 정보 (가능한 경우)
    rating: Optional[float] = Field(None, description="평점")
    review_count: Optional[int] = Field(None, description="리뷰 수")
    price_range: Optional[str] = Field(None, description="가격대")
    
    @classmethod
    def from_kakao_result(cls, result: "KakaoPlaceResult") -> "PlaceCandidate":
        """KakaoPlaceResult에서 PlaceCandidate 생성"""
        return cls(
            id=result.id,
            place_name=result.place_name,
            category=result.category_name,
            address=result.road_address_name or result.address_name,
            phone=result.phone,
            distance=int(result.distance) if result.distance else None,
            place_url=result.place_url,
        )
    
    @classmethod
    async def from_kakao_result_with_details(
        cls, 
        result: "KakaoPlaceResult",
        kakao_client: "KakaoLocalClient",
        district: Optional[str] = None,
    ) -> "PlaceCandidate":
        """KakaoPlaceResult에서 PlaceCandidate 생성 + 상세 정보 수집"""
        candidate = cls.from_kakao_result(result)
        
        # 블로그 검색으로 추가 정보 수집
        try:
            details = await kakao_client.get_place_details(
                place_name=result.place_name,
                district=district,
            )
            candidate.blog_snippets = details.get("blog_snippets", [])
            candidate.extracted_keywords = details.get("keywords", [])
            candidate.has_reviews = details.get("has_reviews", False)
        except Exception:
            pass
        
        return candidate


class PlaceRecommendation(BaseModel):
    """LLM이 추천한 장소"""
    place_id: str = Field(..., description="장소 ID")
    place_name: str = Field(..., description="장소명")
    rank: int = Field(..., description="추천 순위 (1이 최고)")
    reason: str = Field(..., description="추천 이유")
    match_score: Optional[float] = Field(None, description="모임 조건 매칭 점수 (0-100)")
    
    # 매칭 상세
    matched_preferences: list[str] = Field(
        default_factory=list, 
        description="매칭된 선호도 항목들"
    )
    considerations: list[str] = Field(
        default_factory=list,
        description="고려사항/주의점"
    )


class LLMRecommendationResult(BaseModel):
    """LLM 추천 결과 전체"""
    model_config = {"protected_namespaces": ()}  # model_ 네임스페이스 충돌 방지
    
    recommendations: list[PlaceRecommendation] = Field(
        ..., 
        description="추천 장소 리스트 (순위순)"
    )
    summary: str = Field(..., description="전체 추천 요약")
    
    # 메타 정보
    meeting_context_summary: str = Field(..., description="모임 조건 요약")
    total_candidates: int = Field(..., description="검토한 총 후보 수")
    model_used: str = Field(default="gemini", description="사용된 LLM 모델")


class LLMPromptContext(BaseModel):
    """LLM 프롬프트에 전달할 컨텍스트"""
    # 모임 정보
    meeting_purpose: str = Field(..., description="모임 목적")
    participant_count: int = Field(..., description="참가자 수")
    meeting_title: Optional[str] = Field(None, description="모임 제목")
    meeting_description: Optional[str] = Field(None, description="모임 설명")
    
    # 위치 정보
    center_district: Optional[str] = Field(None, description="중심 지역")
    
    # 선호도 요약
    preferred_food_types: list[str] = Field(default_factory=list, description="선호 음식 종류")
    preferred_atmospheres: list[str] = Field(default_factory=list, description="선호 분위기")
    required_conditions: list[str] = Field(default_factory=list, description="필요 조건")
    
    # 장소 후보
    candidates: list[PlaceCandidate] = Field(default_factory=list, description="장소 후보 리스트")
    
    @classmethod
    def from_meeting_context(
        cls, 
        context: "MeetingContext",
        candidates: list[PlaceCandidate]
    ) -> "LLMPromptContext":
        """MeetingContext에서 LLMPromptContext 생성"""
        # 선호도에서 상위 항목 추출
        prefs = context.aggregated_preferences or {}
        
        food_types = list(prefs.get("food_types", {}).keys())[:3]
        atmospheres = list(prefs.get("atmospheres", {}).keys())[:3]
        conditions = list(prefs.get("conditions", {}).keys())[:3]
        
        return cls(
            meeting_purpose=context.purpose,
            participant_count=context.expected_participant_count,
            meeting_title=context.title,
            meeting_description=context.description,
            center_district=context.center_location.district if context.center_location else None,
            preferred_food_types=food_types,
            preferred_atmospheres=atmospheres,
            required_conditions=conditions,
            candidates=candidates,
        )

