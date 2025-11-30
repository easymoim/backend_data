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

