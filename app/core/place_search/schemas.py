"""
장소 검색 관련 스키마 정의
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from uuid import UUID


# ============================================================
# 장소 선택 방식 Enum
# ============================================================

class LocationChoiceType(str, Enum):
    """장소 선택 방식"""
    CENTER_LOCATION = "center_location"       # 중간위치 찾기 (참가자 위치 기반)
    PREFERENCE_AREA = "preference_area"       # 선호 지역 선택 (구/동 투표)
    PREFERENCE_SUBWAY = "preference_subway"   # 선호 지하철역 (역 근처)


class StationInfo(BaseModel):
    """지하철역 정보"""
    name: str = Field(..., description="역명")
    daily_passengers: int = Field(default=0, description="일평균 승객수")
    weight: int = Field(default=1, description="가중치 (인기도)")
    latitude: Optional[float] = Field(None, description="위도")
    longitude: Optional[float] = Field(None, description="경도")


# ============================================================
# 선호도 관련 Enum
# ============================================================

class FoodType(str, Enum):
    """음식 종류"""
    KOREAN = "한식"
    JAPANESE = "일식"
    CHINESE = "중식"
    WESTERN = "양식"
    ASIAN = "아시안"
    SNACK = "분식"
    MEAT = "고기"
    SEAFOOD = "해산물"
    CHICKEN = "치킨"
    PIZZA = "피자"
    BURGER = "햄버거"
    CAFE = "카페"
    DESSERT = "디저트"
    BAR = "술집"
    ETC = "기타"


class AtmosphereType(str, Enum):
    """분위기"""
    QUIET = "조용한"
    LIVELY = "활기찬"
    ROMANTIC = "로맨틱한"
    MODERN = "모던한"
    TRADITIONAL = "전통적인"
    COZY = "아늑한"
    SPACIOUS = "넓은"
    PRIVATE = "프라이빗한"
    CASUAL = "캐주얼한"
    FORMAL = "격식있는"
    CONVERSATION_FRIENDLY = "대화 나누기 좋은"
    COMFORTABLE = "편안한"
    TRENDY = "트렌디한"
    NICE_ATMOSPHERE = "분위기 좋은"


class ConditionType(str, Enum):
    """조건"""
    PARKING = "주차"
    PRIVATE_ROOM = "개별룸"
    GROUP_SEATING = "단체석"
    PET_FRIENDLY = "반려동물"
    WHEELCHAIR = "휠체어"
    RESERVATION = "예약가능"
    LATE_NIGHT = "24시간"
    OUTDOOR_SEATING = "야외석"
    DELIVERY = "배달"
    TAKEOUT = "포장"


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
    
    # 장소 선택 방식
    location_choice_type: LocationChoiceType = Field(
        default=LocationChoiceType.CENTER_LOCATION,
        description="장소 선택 방식 (center_location: 중간위치, preference_area: 선호지역, preference_subway: 선호역)"
    )
    
    # 위치 정보 (중간위치 방식)
    center_location: Optional[CenterLocation] = None
    participant_locations: list[ParticipantLocation] = Field(default_factory=list)
    
    # 선호 지역 정보 (선호지역 방식)
    preferred_district: Optional[str] = Field(None, description="선호 지역 (예: 강남구)")
    district_votes: Optional[dict[str, int]] = Field(
        default=None,
        description="지역별 투표 수 (예: {'강남구': 3, '서초구': 2})"
    )
    
    # 선호 지하철역 정보 (선호역 방식)
    preferred_station: Optional[str] = Field(None, description="선호 지하철역 (예: 강남)")
    station_votes: Optional[dict[str, int]] = Field(
        default=None,
        description="역별 투표 수 (예: {'강남': 3, '홍대입구': 2})"
    )
    
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
    address: str = Field(..., description="도로명 주소")
    address_jibun: Optional[str] = Field(None, description="지번 주소")
    phone: Optional[str] = Field(None, description="전화번호")
    distance: Optional[int] = Field(None, description="중심점에서의 거리 (미터)")
    place_url: str = Field(..., description="카카오맵 상세 URL")
    
    # 좌표 정보 (지도 표시용)
    latitude: Optional[float] = Field(None, description="위도 (y좌표)")
    longitude: Optional[float] = Field(None, description="경도 (x좌표)")
    
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
            address_jibun=result.address_name,
            phone=result.phone,
            distance=int(result.distance) if result.distance else None,
            place_url=result.place_url,
            latitude=float(result.y),  # 위도
            longitude=float(result.x),  # 경도
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
    """LLM이 추천한 장소 (지도 표시에 필요한 정보 포함)"""
    place_id: str = Field(..., description="장소 ID (카카오)")
    place_name: str = Field(..., description="장소명")
    rank: int = Field(..., description="추천 순위 (1이 최고)")
    reason: str = Field(..., description="추천 이유")
    match_score: Optional[float] = Field(None, description="모임 조건 매칭 점수 (0-100)")
    
    # 지도 표시용 정보 (1차 검색 결과에서 매핑)
    address: Optional[str] = Field(None, description="도로명 주소")
    address_jibun: Optional[str] = Field(None, description="지번 주소")
    latitude: Optional[float] = Field(None, description="위도 (y좌표)")
    longitude: Optional[float] = Field(None, description="경도 (x좌표)")
    place_url: Optional[str] = Field(None, description="카카오맵 상세 URL")
    phone: Optional[str] = Field(None, description="전화번호")
    category: Optional[str] = Field(None, description="카테고리")
    distance: Optional[int] = Field(None, description="중심점에서의 거리 (미터)")
    
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
    
    # 선호도 요약 (가중치 포함)
    preferred_food_types: list[str] = Field(default_factory=list, description="선호 음식 종류")
    preferred_atmospheres: list[str] = Field(default_factory=list, description="선호 분위기")
    required_conditions: list[str] = Field(default_factory=list, description="필요 조건")
    
    # 선호도 가중치 (투표 수)
    food_type_weights: dict[str, int] = Field(default_factory=dict, description="음식 종류별 선호 인원")
    atmosphere_weights: dict[str, int] = Field(default_factory=dict, description="분위기별 선호 인원")
    condition_weights: dict[str, int] = Field(default_factory=dict, description="조건별 선호 인원")
    
    # 장소 후보
    candidates: list[PlaceCandidate] = Field(default_factory=list, description="장소 후보 리스트")
    
    @classmethod
    def from_meeting_context(
        cls, 
        context: "MeetingContext",
        candidates: list[PlaceCandidate]
    ) -> "LLMPromptContext":
        """MeetingContext에서 LLMPromptContext 생성"""
        # 선호도에서 항목과 가중치 추출 (투표 수 많은 순으로 정렬)
        prefs = context.aggregated_preferences or {}
        
        # 음식 종류 (가중치 높은 순)
        food_data = prefs.get("food_types", {})
        sorted_foods = sorted(food_data.items(), key=lambda x: x[1], reverse=True)
        food_types = [item[0] for item in sorted_foods[:5]]
        food_weights = dict(sorted_foods[:5])
        
        # 분위기 (가중치 높은 순)
        atm_data = prefs.get("atmospheres", {})
        sorted_atms = sorted(atm_data.items(), key=lambda x: x[1], reverse=True)
        atmospheres = [item[0] for item in sorted_atms[:5]]
        atm_weights = dict(sorted_atms[:5])
        
        # 조건 (가중치 높은 순)
        cond_data = prefs.get("conditions", {})
        sorted_conds = sorted(cond_data.items(), key=lambda x: x[1], reverse=True)
        conditions = [item[0] for item in sorted_conds[:5]]
        cond_weights = dict(sorted_conds[:5])
        
        return cls(
            meeting_purpose=context.purpose,
            participant_count=context.expected_participant_count,
            meeting_title=context.title,
            meeting_description=context.description,
            center_district=context.center_location.district if context.center_location else None,
            preferred_food_types=food_types,
            preferred_atmospheres=atmospheres,
            required_conditions=conditions,
            food_type_weights=food_weights,
            atmosphere_weights=atm_weights,
            condition_weights=cond_weights,
            candidates=candidates,
        )

