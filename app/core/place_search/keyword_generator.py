"""
검색 키워드 생성기

모임 컨텍스트와 선호도 정보를 기반으로 카카오 API 검색에 사용할 키워드를 생성합니다.
"""

from typing import Optional
from collections import Counter

from .schemas import (
    MeetingContext,
    SearchKeyword,
    FoodType,
    AtmosphereType,
    ConditionType,
    PlacePreference,
)


class KeywordGenerator:
    """검색 키워드 생성기"""
    
    # ============================================================
    # 한글 매핑 테이블
    # ============================================================
    
    FOOD_TYPE_KR: dict[FoodType, str] = {
        FoodType.KOREAN: "한식",
        FoodType.JAPANESE: "일식",
        FoodType.CHINESE: "중식",
        FoodType.WESTERN: "양식",
        FoodType.ASIAN: "아시안",
        FoodType.MEAT: "고기",
        FoodType.SEAFOOD: "해산물",
        FoodType.CHICKEN: "치킨",
        FoodType.PIZZA: "피자",
        FoodType.CAFE: "카페",
        FoodType.BAR: "술집",
        FoodType.ETC: "맛집",
    }
    
    # 분위기 → 검색 가능한 키워드로 매핑
    # 카카오 API는 "지역 + 분위기" 또는 "지역 + 상황 + 맛집" 형태로 검색 가능
    ATMOSPHERE_KR: dict[AtmosphereType, str] = {
        AtmosphereType.QUIET: "조용한",  # 단독 사용시 효과 낮음
        AtmosphereType.LIVELY: "회식",   # "회식"으로 변환 (2786개)
        AtmosphereType.ROMANTIC: "데이트",  # "데이트"로 변환 (2067개)
        AtmosphereType.MODERN: "분위기 좋은",  # (1180개)
        AtmosphereType.TRADITIONAL: "전통",
        AtmosphereType.COZY: "분위기 좋은",  # 아늑한 → 분위기 좋은
        AtmosphereType.SPACIOUS: "넓은",
        AtmosphereType.PRIVATE: "프라이빗",  # (101개)
    }
    
    # 분위기별 검색 가능한 키워드 조합
    ATMOSPHERE_SEARCH_KEYWORDS: dict[AtmosphereType, list[str]] = {
        AtmosphereType.QUIET: ["조용한", "분위기 좋은"],
        AtmosphereType.LIVELY: ["회식", "단체"],
        AtmosphereType.ROMANTIC: ["데이트 맛집", "분위기 좋은"],
        AtmosphereType.MODERN: ["분위기 좋은", "인스타"],
        AtmosphereType.TRADITIONAL: ["전통", "한옥"],
        AtmosphereType.COZY: ["분위기 좋은", "아늑한"],
        AtmosphereType.SPACIOUS: ["넓은", "단체"],
        AtmosphereType.PRIVATE: ["프라이빗", "룸"],
    }
    
    CONDITION_KR: dict[ConditionType, str] = {
        ConditionType.PARKING: "주차가능",
        ConditionType.PRIVATE_ROOM: "룸",
        ConditionType.GROUP_FRIENDLY: "단체",
        ConditionType.PET_FRIENDLY: "애견동반",
        ConditionType.WHEELCHAIR: "휠체어",
        ConditionType.RESERVATION: "예약",
        ConditionType.LATE_NIGHT: "심야영업",
    }
    
    PURPOSE_KR: dict[str, list[str]] = {
        "dining": ["맛집", "식당", "레스토랑"],
        "cafe": ["카페", "디저트", "브런치"],
        "drink": ["술집", "바", "호프"],
        "etc": ["모임장소", "맛집"],
    }
    
    # ============================================================
    # 키워드 생성 메서드
    # ============================================================
    
    def generate_keywords(
        self, 
        context: MeetingContext,
        max_keywords: int = 5
    ) -> list[SearchKeyword]:
        """
        모임 컨텍스트를 기반으로 검색 키워드 리스트 생성
        
        Args:
            context: 모임 컨텍스트 정보
            max_keywords: 최대 키워드 수
            
        Returns:
            우선순위가 부여된 검색 키워드 리스트
        """
        keywords: list[SearchKeyword] = []
        
        # 지역 정보 추출
        district = self._get_district(context)
        
        # 집계된 선호도에서 상위 항목 추출
        top_food = self._get_top_preference(context, "food_types")
        top_atmosphere = self._get_top_preference(context, "atmospheres")
        top_condition = self._get_top_preference(context, "conditions")
        
        # 목적별 기본 키워드
        purpose_keywords = self.PURPOSE_KR.get(context.purpose, ["맛집"])
        
        # 음식 종류 한글 변환
        food_kr = self.FOOD_TYPE_KR.get(FoodType(top_food), "") if top_food else ""
        
        # ============================================================
        # 카카오 API는 형용사(조용한, 분위기좋은)를 이해하지 못함
        # 검색 가능한 키워드 위주로 생성
        # ============================================================
        
        # 1. 메인 키워드: 지역 + 음식 종류 + 맛집 (가장 기본, 필수)
        if food_kr:
            # "강남구 한식 맛집" 형태
            main_keyword = self._build_keyword(district, None, f"{food_kr} 맛집")
            keywords.append(SearchKeyword(
                keyword=main_keyword,
                priority=1,
                category="main"
            ))
        
        # 2. 분위기 키워드: 지역 + 분위기/상황 + 맛집 (검색 가능한 형태)
        # 예: "강남 데이트 맛집", "강남 회식", "강남 분위기 좋은"
        if top_atmosphere:
            atm_type = AtmosphereType(top_atmosphere)
            atm_keywords = self.ATMOSPHERE_SEARCH_KEYWORDS.get(atm_type, [])
            
            for i, atm_kw in enumerate(atm_keywords[:1]):  # 상위 1개만
                # "데이트 맛집" 형태는 그대로, 아니면 단독 사용
                if "맛집" in atm_kw:
                    atm_keyword = self._build_keyword(district, None, atm_kw)
                else:
                    atm_keyword = self._build_keyword(district, None, atm_kw)
                
                keywords.append(SearchKeyword(
                    keyword=atm_keyword,
                    priority=2,
                    category="atmosphere"
                ))
        
        # 3. 조건 키워드: 지역 + 조건 + 음식 (검색 가능한 조건만)
        if top_condition:
            cond_kr = self.CONDITION_KR.get(ConditionType(top_condition), "")
            food_or_purpose = food_kr if food_kr else purpose_keywords[0]
            # "강남구 주차 한식" 또는 "강남구 룸 한식" 형태
            cond_keyword = self._build_keyword(district, cond_kr, food_or_purpose)
            keywords.append(SearchKeyword(
                keyword=cond_keyword,
                priority=2,
                category="condition"
            ))
        
        # 4. 인원수 기반 키워드 (대인원인 경우)
        if context.expected_participant_count >= 8:
            if food_kr:
                # "강남구 단체 한식" 형태
                group_keyword = self._build_keyword(district, "단체", food_kr)
            else:
                group_keyword = self._build_keyword(district, "단체", "모임장소")
            keywords.append(SearchKeyword(
                keyword=group_keyword,
                priority=2,
                category="group"
            ))
            
            # 회식 키워드 추가
            keywords.append(SearchKeyword(
                keyword=self._build_keyword(district, None, "회식"),
                priority=2,
                category="group"
            ))
        
        # 5. 지역 + 맛집 (일반적인 검색)
        general_keyword = self._build_keyword(district, None, "맛집")
        keywords.append(SearchKeyword(
            keyword=general_keyword,
            priority=3,
            category="general"
        ))
        
        # 6. 2순위 음식 종류가 있으면 추가
        second_food = self._get_second_preference(context, "food_types")
        if second_food and second_food != top_food:
            second_food_kr = self.FOOD_TYPE_KR.get(FoodType(second_food), "")
            if second_food_kr:
                second_keyword = self._build_keyword(district, None, f"{second_food_kr} 맛집")
                keywords.append(SearchKeyword(
                    keyword=second_keyword,
                    priority=3,
                    category="food_secondary"
                ))
        
        # 7. 목적 기반 키워드 (dining→식당, cafe→카페)
        for i, purpose_kw in enumerate(purpose_keywords[:1]):
            purpose_keyword = self._build_keyword(district, None, purpose_kw)
            keywords.append(SearchKeyword(
                keyword=purpose_keyword,
                priority=4 + i,
                category="purpose"
            ))
        
        # 중복 제거 및 정렬
        keywords = self._deduplicate_keywords(keywords)
        keywords.sort(key=lambda k: k.priority)
        
        return keywords[:max_keywords]
    
    def generate_keywords_from_preferences(
        self,
        preferences: list[PlacePreference],
        district: Optional[str] = None,
        purpose: str = "dining",
        participant_count: int = 4,
    ) -> list[SearchKeyword]:
        """
        참가자들의 선호도 리스트로부터 직접 키워드 생성
        
        Args:
            preferences: 참가자들의 선호도 리스트
            district: 지역구 이름
            purpose: 모임 목적
            participant_count: 참가자 수
            
        Returns:
            검색 키워드 리스트
        """
        # 선호도 집계
        aggregated = self.aggregate_preferences(preferences)
        
        # MeetingContext 생성
        from uuid import uuid4
        context = MeetingContext(
            meeting_id=uuid4(),
            purpose=purpose,
            aggregated_preferences=aggregated,
            expected_participant_count=participant_count,
        )
        
        if district:
            from .schemas import CenterLocation
            context.center_location = CenterLocation(
                latitude=0.0,
                longitude=0.0,
                district=district,
            )
        
        return self.generate_keywords(context)
    
    # ============================================================
    # 선호도 집계 메서드
    # ============================================================
    
    def aggregate_preferences(
        self, 
        preferences: list[PlacePreference]
    ) -> dict[str, dict[str, int]]:
        """
        여러 참가자의 선호도를 집계
        
        Args:
            preferences: 참가자들의 선호도 리스트
            
        Returns:
            카테고리별 항목 카운트 딕셔너리
            예: {
                "food_types": {"korean": 3, "japanese": 2},
                "atmospheres": {"quiet": 4},
                "conditions": {"parking": 2}
            }
        """
        food_counter: Counter = Counter()
        atmosphere_counter: Counter = Counter()
        condition_counter: Counter = Counter()
        
        for pref in preferences:
            for food in pref.food_types:
                food_counter[food.value] += 1
            for atm in pref.atmospheres:
                atmosphere_counter[atm.value] += 1
            for cond in pref.conditions:
                condition_counter[cond.value] += 1
        
        return {
            "food_types": dict(food_counter),
            "atmospheres": dict(atmosphere_counter),
            "conditions": dict(condition_counter),
        }
    
    def get_top_items(
        self, 
        aggregated: dict[str, dict[str, int]], 
        category: str, 
        top_n: int = 1
    ) -> list[tuple[str, int]]:
        """
        집계된 선호도에서 상위 N개 항목 반환
        
        Args:
            aggregated: 집계된 선호도
            category: 카테고리 (food_types, atmospheres, conditions)
            top_n: 반환할 상위 항목 수
            
        Returns:
            (항목, 카운트) 튜플 리스트
        """
        category_data = aggregated.get(category, {})
        sorted_items = sorted(category_data.items(), key=lambda x: x[1], reverse=True)
        return sorted_items[:top_n]
    
    # ============================================================
    # 헬퍼 메서드
    # ============================================================
    
    def _get_district(self, context: MeetingContext) -> Optional[str]:
        """컨텍스트에서 지역구 추출"""
        if context.center_location and context.center_location.district:
            return context.center_location.district
        return None
    
    def _get_top_preference(
        self, 
        context: MeetingContext, 
        category: str
    ) -> Optional[str]:
        """컨텍스트의 집계된 선호도에서 최상위 항목 추출"""
        if not context.aggregated_preferences:
            return None
        
        category_data = context.aggregated_preferences.get(category, {})
        if not category_data:
            return None
        
        top_item = max(category_data.items(), key=lambda x: x[1])
        return top_item[0]
    
    def _get_second_preference(
        self, 
        context: MeetingContext, 
        category: str
    ) -> Optional[str]:
        """컨텍스트의 집계된 선호도에서 2순위 항목 추출"""
        if not context.aggregated_preferences:
            return None
        
        category_data = context.aggregated_preferences.get(category, {})
        if len(category_data) < 2:
            return None
        
        sorted_items = sorted(category_data.items(), key=lambda x: x[1], reverse=True)
        return sorted_items[1][0]
    
    def _build_keyword(
        self, 
        district: Optional[str], 
        modifier: Optional[str], 
        main: str
    ) -> str:
        """키워드 문자열 조합"""
        parts = []
        if district:
            parts.append(district)
        if modifier:
            parts.append(modifier)
        parts.append(main)
        return " ".join(parts)
    
    def _deduplicate_keywords(
        self, 
        keywords: list[SearchKeyword]
    ) -> list[SearchKeyword]:
        """키워드 중복 제거 (우선순위 높은 것 유지)"""
        seen: dict[str, SearchKeyword] = {}
        for kw in keywords:
            if kw.keyword not in seen:
                seen[kw.keyword] = kw
            elif kw.priority < seen[kw.keyword].priority:
                seen[kw.keyword] = kw
        return list(seen.values())


# ============================================================
# 편의 함수
# ============================================================

def generate_search_keywords(
    district: Optional[str] = None,
    food_type: Optional[str] = None,
    atmosphere: Optional[str] = None,
    condition: Optional[str] = None,
    purpose: str = "dining",
    participant_count: int = 4,
) -> list[str]:
    """
    간단한 파라미터로 검색 키워드 리스트 생성
    
    Args:
        district: 지역구 (예: "강남구")
        food_type: 음식 종류 (예: "korean")
        atmosphere: 분위기 (예: "quiet")
        condition: 조건 (예: "parking")
        purpose: 모임 목적
        participant_count: 참가자 수
        
    Returns:
        검색 키워드 문자열 리스트
        
    Example:
        >>> generate_search_keywords(
        ...     district="용산구",
        ...     food_type="korean",
        ...     atmosphere="quiet",
        ...     participant_count=10
        ... )
        ['용산구 조용한 한식', '용산구 단체 모임장소', '용산구 맛집', ...]
    """
    generator = KeywordGenerator()
    
    # PlacePreference 생성
    pref = PlacePreference(
        food_types=[FoodType(food_type)] if food_type else [],
        atmospheres=[AtmosphereType(atmosphere)] if atmosphere else [],
        conditions=[ConditionType(condition)] if condition else [],
    )
    
    keywords = generator.generate_keywords_from_preferences(
        preferences=[pref],
        district=district,
        purpose=purpose,
        participant_count=participant_count,
    )
    
    return [kw.keyword for kw in keywords]

