"""
LLM 기반 장소 추천 모듈

3단계: LLM 기반 추천 및 선택 (LLM Recommendation & Selection)
- 모임 컨텍스트와 장소 후보를 기반으로 최적의 장소 추천
- Gemini API 사용 (REST API로 호출 - Vercel 서버리스 환경 호환)
"""

import json
import os
from typing import Optional

import httpx

from .schemas import (
    MeetingContext,
    KakaoPlaceResult,
    PlaceCandidate,
    PlaceRecommendation,
    LLMRecommendationResult,
    LLMPromptContext,
)


# 한글 매핑
FOOD_TYPE_KR = {
    "korean": "한식",
    "japanese": "일식",
    "chinese": "중식",
    "western": "양식",
    "asian": "아시안",
    "meat": "고기/구이",
    "seafood": "해산물",
    "chicken": "치킨",
    "pizza": "피자",
    "cafe": "카페/디저트",
    "bar": "술집/바",
    "etc": "기타",
}

ATMOSPHERE_KR = {
    "quiet": "조용한",
    "lively": "활기찬/왁자지껄한",
    "romantic": "로맨틱한/분위기 좋은",
    "modern": "모던한/세련된",
    "traditional": "전통적인",
    "cozy": "아늑한",
    "spacious": "넓은",
    "private": "프라이빗한",
}

CONDITION_KR = {
    "parking": "주차 가능",
    "private_room": "룸/개인실",
    "group_friendly": "단체 이용 가능",
    "pet_friendly": "반려동물 동반 가능",
    "wheelchair": "휠체어 이용 가능",
    "reservation": "예약 가능",
    "late_night": "심야 영업",
}

PURPOSE_KR = {
    "dining": "식사 모임",
    "cafe": "카페 모임",
    "drink": "술자리",
    "etc": "기타 모임",
}

LOCATION_CHOICE_KR = {
    "center_location": "중간위치",
    "preference_area": "선호지역",
    "preference_subway": "선호역 근처",
}


class LLMRecommender:
    """
    LLM 기반 장소 추천 서비스
    
    모임 컨텍스트와 장소 후보를 분석하여 최적의 장소를 추천합니다.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash"):
        """
        Args:
            api_key: Gemini API 키. 없으면 환경변수 GEMINI_API_KEY에서 가져옴
            model: 사용할 Gemini 모델
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        # Gemini REST API 엔드포인트
        self._api_base = "https://generativelanguage.googleapis.com/v1beta/models"
    
    def _validate_api_key(self):
        """API 키 유효성 검사"""
        if not self.api_key:
            raise ValueError(
                "Gemini API 키가 필요합니다. "
                "생성자에 api_key를 전달하거나 GEMINI_API_KEY 환경변수를 설정하세요."
            )
    
    # ============================================================
    # 메인 추천 API
    # ============================================================
    
    async def recommend(
        self,
        context: MeetingContext,
        places: list[KakaoPlaceResult],
        top_n: int = 3,
        collect_details: bool = True,
        max_detail_places: int = 10,
    ) -> LLMRecommendationResult:
        """
        모임 컨텍스트와 장소 후보를 기반으로 최적의 장소 추천
        
        Args:
            context: 모임 컨텍스트
            places: 장소 후보 리스트 (검색 결과)
            top_n: 추천할 장소 수
            collect_details: 블로그 검색으로 상세 정보 수집 여부
            max_detail_places: 상세 정보를 수집할 최대 장소 수
            
        Returns:
            LLMRecommendationResult
        """
        from .kakao_client import KakaoLocalClient
        
        district = context.center_location.district if context.center_location else None
        
        # 1. 장소 후보를 PlaceCandidate로 변환 (상세 정보 수집)
        if collect_details:
            kakao_client = KakaoLocalClient()
            candidates = await self._collect_candidates_with_details(
                places[:max_detail_places], 
                kakao_client, 
                district
            )
            # 나머지는 기본 정보만
            for p in places[max_detail_places:]:
                candidates.append(PlaceCandidate.from_kakao_result(p))
        else:
            candidates = [PlaceCandidate.from_kakao_result(p) for p in places]
        
        # 2. 프롬프트 컨텍스트 생성
        prompt_context = LLMPromptContext.from_meeting_context(context, candidates)
        
        # 3. 프롬프트 생성
        prompt = self._build_prompt(prompt_context, context, top_n)
        
        # 4. LLM 호출
        response = await self._call_llm(prompt)
        
        # 5. 응답 파싱
        result = self._parse_response(response, prompt_context, candidates)
        
        return result
    
    async def _collect_candidates_with_details(
        self,
        places: list[KakaoPlaceResult],
        kakao_client: "KakaoLocalClient",
        district: Optional[str],
    ) -> list[PlaceCandidate]:
        """상세 정보를 수집하여 PlaceCandidate 리스트 생성"""
        import asyncio
        
        async def collect_one(place: KakaoPlaceResult) -> PlaceCandidate:
            return await PlaceCandidate.from_kakao_result_with_details(
                place, kakao_client, district
            )
        
        # 병렬로 상세 정보 수집
        tasks = [collect_one(p) for p in places]
        candidates = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 에러 발생한 경우 기본 정보만 사용
        result = []
        for i, c in enumerate(candidates):
            if isinstance(c, Exception):
                result.append(PlaceCandidate.from_kakao_result(places[i]))
            else:
                result.append(c)
        
        return result
    
    async def recommend_from_pipeline_result(
        self,
        pipeline_result: dict,
        top_n: int = 3,
    ) -> LLMRecommendationResult:
        """
        PlaceSearcher.full_search_pipeline 결과로 추천
        
        Args:
            pipeline_result: full_search_pipeline 반환값
                {
                    "context": MeetingContext,
                    "keywords": list[SearchKeyword],
                    "places": list[KakaoPlaceResult],
                }
            top_n: 추천할 장소 수
            
        Returns:
            LLMRecommendationResult
        """
        return await self.recommend(
            context=pipeline_result["context"],
            places=pipeline_result["places"],
            top_n=top_n,
        )
    
    # ============================================================
    # 프롬프트 생성
    # ============================================================
    
    def _build_prompt(
        self, 
        prompt_context: LLMPromptContext, 
        meeting_context: MeetingContext,
        top_n: int
    ) -> str:
        """LLM 프롬프트 생성"""
        
        # 모임 정보 요약
        purpose_kr = PURPOSE_KR.get(prompt_context.meeting_purpose, prompt_context.meeting_purpose)
        
        # 장소 선택 방식 정보
        choice_type = meeting_context.location_choice_type
        choice_type_kr = LOCATION_CHOICE_KR.get(choice_type.value, choice_type.value)
        
        meeting_info = f"""
## 모임 정보
- **모임 유형**: {purpose_kr}
- **참가 인원**: {prompt_context.participant_count}명
- **장소 선택 방식**: {choice_type_kr}
"""
        
        # 장소 선택 방식별 추가 정보
        if choice_type == "center_location":
            meeting_info += f"- **중심 위치 지역**: {prompt_context.center_district or '미정'}\n"
        elif choice_type == "preference_area":
            meeting_info += f"- **선호 지역**: {meeting_context.preferred_district or '미정'}\n"
            if meeting_context.district_votes:
                votes_str = ", ".join([f"{k}({v}표)" for k, v in meeting_context.district_votes.items()])
                meeting_info += f"- **지역 투표 결과**: {votes_str}\n"
        elif choice_type == "preference_subway":
            meeting_info += f"- **선호 지하철역**: {meeting_context.preferred_station or '미정'}\n"
            if meeting_context.station_votes:
                votes_str = ", ".join([f"{k}역({v}표)" for k, v in meeting_context.station_votes.items()])
                meeting_info += f"- **역 투표 결과**: {votes_str}\n"
        
        if prompt_context.meeting_title:
            meeting_info += f"- **모임명**: {prompt_context.meeting_title}\n"
        if prompt_context.meeting_description:
            meeting_info += f"- **모임 설명**: {prompt_context.meeting_description}\n"
        
        # 선호도 정보 (가중치 포함)
        preferences_info = """
## 참가자 선호도 (선호 인원수 기준 정렬)
"""
        # 음식 선호도 (가중치 포함)
        if prompt_context.food_type_weights:
            food_list = []
            for food, count in prompt_context.food_type_weights.items():
                food_kr = FOOD_TYPE_KR.get(food, food)
                food_list.append(f"{food_kr}({count}명)")
            preferences_info += f"- **선호 음식**: {', '.join(food_list)}\n"
        
        # 분위기 선호도 (가중치 포함)
        if prompt_context.atmosphere_weights:
            atm_list = []
            for atm, count in prompt_context.atmosphere_weights.items():
                atm_kr = ATMOSPHERE_KR.get(atm, atm)
                atm_list.append(f"{atm_kr}({count}명)")
            preferences_info += f"- **선호 분위기**: {', '.join(atm_list)}\n"
        
        # 필요 조건 (가중치 포함)
        if prompt_context.condition_weights:
            cond_list = []
            for cond, count in prompt_context.condition_weights.items():
                cond_kr = CONDITION_KR.get(cond, cond)
                cond_list.append(f"{cond_kr}({count}명)")
            preferences_info += f"- **필요 조건**: {', '.join(cond_list)}\n"
        
        preferences_info += "\n※ 괄호 안 숫자는 해당 항목을 선호하는 참가자 수입니다. 더 많은 참가자가 선호하는 항목을 우선적으로 고려해주세요.\n"
        
        # 장소 후보 목록
        candidates_info = """
## 장소 후보 목록
"""
        for i, c in enumerate(prompt_context.candidates[:20], 1):  # 최대 20개
            distance_str = f"{c.distance}m" if c.distance else "거리 정보 없음"
            candidates_info += f"""
### {i}. {c.place_name}
- 카테고리: {c.category}
- 주소: {c.address}
- 전화: {c.phone or "정보 없음"}
- 거리: {distance_str}
"""
            # 블로그 리뷰에서 추출된 정보 추가
            if c.extracted_keywords:
                candidates_info += f"- 특징 키워드: {', '.join(c.extracted_keywords)}\n"
            
            if c.blog_snippets:
                candidates_info += "- 블로그 리뷰 요약:\n"
                for snippet in c.blog_snippets[:2]:  # 최대 2개
                    # 너무 길면 자르기
                    short_snippet = snippet[:150] + "..." if len(snippet) > 150 else snippet
                    candidates_info += f"  > {short_snippet}\n"
        
        # 장소 선택 방식별 추천 기준 조정
        extra_criteria = ""
        if choice_type == "preference_subway":
            extra_criteria = "6. 지하철역과의 거리 (도보 접근성)\n"
        
        prompt = f"""당신은 모임 장소 추천 전문가입니다. 
아래의 모임 정보와 참가자 선호도를 고려하여, 장소 후보 중에서 가장 적합한 장소 {top_n}곳을 추천해주세요.

{meeting_info}
{preferences_info}
{candidates_info}

## 응답 형식
다음 JSON 형식으로만 응답해주세요. 다른 텍스트는 포함하지 마세요.

```json
{{
  "recommendations": [
    {{
      "place_id": "장소 ID",
      "place_name": "장소명",
      "rank": 1,
      "reason": "이 장소를 추천하는 이유 (2-3문장)",
      "match_score": 85,
      "matched_preferences": ["매칭된 선호도 1", "매칭된 선호도 2"],
      "considerations": ["고려사항이나 주의점"]
    }}
  ],
  "summary": "전체 추천 요약 (1-2문장)"
}}
```

## 추천 기준
1. 참가자 선호 음식 종류와 일치하는지
2. 선호하는 분위기와 맞는지
3. 필요한 조건(주차, 룸, 단체 등)을 충족하는지
4. 참가 인원이 이용하기 적합한지
5. 접근성 (거리)
{extra_criteria}
JSON 형식으로만 응답해주세요.
"""
        return prompt
    
    # ============================================================
    # LLM 호출
    # ============================================================
    
    async def _call_llm(self, prompt: str) -> str:
        """Gemini API 호출 (REST API 사용 - Vercel 서버리스 호환)"""
        self._validate_api_key()
        
        url = f"{self._api_base}/{self.model}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 4096,
            }
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            # 응답에서 텍스트 추출
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError) as e:
                raise ValueError(f"Gemini API 응답 파싱 실패: {data}") from e
    
    # ============================================================
    # 응답 파싱
    # ============================================================
    
    def _parse_response(
        self, 
        response: str, 
        context: LLMPromptContext,
        candidates: list[PlaceCandidate]
    ) -> LLMRecommendationResult:
        """LLM 응답을 파싱하여 LLMRecommendationResult 생성"""
        
        # JSON 추출
        try:
            # ```json ... ``` 형태에서 JSON 추출
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            
            data = json.loads(json_str.strip())
        except (json.JSONDecodeError, IndexError) as e:
            # 파싱 실패 시 기본 응답 생성
            return self._create_fallback_result(context, candidates, str(e))
        
        # 원본 장소 정보를 ID/이름으로 빠르게 찾기 위한 맵 생성
        candidates_by_id = {c.id: c for c in candidates}
        candidates_by_name = {c.place_name: c for c in candidates}
        
        # PlaceRecommendation 리스트 생성 (원본 장소 정보 매핑)
        recommendations = []
        for rec in data.get("recommendations", []):
            place_id = rec.get("place_id", "")
            place_name = rec.get("place_name", "")
            
            # 원본 장소 정보 찾기 (ID 또는 이름으로)
            original = candidates_by_id.get(place_id) or candidates_by_name.get(place_name)
            
            recommendation = PlaceRecommendation(
                place_id=original.id if original else place_id,
                place_name=original.place_name if original else place_name,
                rank=rec.get("rank", len(recommendations) + 1),
                reason=rec.get("reason", ""),
                match_score=rec.get("match_score"),
                matched_preferences=rec.get("matched_preferences", []),
                considerations=rec.get("considerations", []),
            )
            
            # 원본 장소에서 지도 표시용 정보 매핑
            if original:
                recommendation.address = original.address
                recommendation.address_jibun = original.address_jibun
                recommendation.latitude = original.latitude
                recommendation.longitude = original.longitude
                recommendation.place_url = original.place_url
                recommendation.phone = original.phone
                recommendation.category = original.category
                recommendation.distance = original.distance
            
            recommendations.append(recommendation)
        
        # 모임 컨텍스트 요약 생성
        purpose_kr = PURPOSE_KR.get(context.meeting_purpose, context.meeting_purpose)
        context_summary = (
            f"{context.center_district or '미정'} 지역, "
            f"{context.participant_count}명, "
            f"{purpose_kr}"
        )
        
        return LLMRecommendationResult(
            recommendations=recommendations,
            summary=data.get("summary", "추천이 완료되었습니다."),
            center_location=context.center_district,
            meeting_context_summary=context_summary,
            total_candidates=len(candidates),
            model_used=self.model,
        )
    
    def _create_fallback_result(
        self,
        context: LLMPromptContext,
        candidates: list[PlaceCandidate],
        error: str
    ) -> LLMRecommendationResult:
        """파싱 실패 시 기본 결과 생성"""
        
        # 상위 3개 후보를 기본 추천으로
        recommendations = []
        for i, c in enumerate(candidates[:3], 1):
            recommendations.append(PlaceRecommendation(
                place_id=c.id,
                place_name=c.place_name,
                rank=i,
                reason=f"{c.category} 카테고리의 장소입니다.",
                # 지도 표시용 정보
                address=c.address,
                address_jibun=c.address_jibun,
                latitude=c.latitude,
                longitude=c.longitude,
                place_url=c.place_url,
                phone=c.phone,
                category=c.category,
                distance=c.distance,
                matched_preferences=[],
                considerations=["LLM 응답 파싱 실패로 기본 추천이 제공되었습니다."],
            ))
        
        purpose_kr = PURPOSE_KR.get(context.meeting_purpose, context.meeting_purpose)
        
        return LLMRecommendationResult(
            recommendations=recommendations,
            summary=f"기본 추천 결과입니다. (파싱 오류: {error})",
            center_location=context.center_district,
            meeting_context_summary=f"{context.center_district}, {context.participant_count}명, {purpose_kr}",
            total_candidates=len(candidates),
            model_used=self.model,
        )


# ============================================================
# 편의 함수
# ============================================================

async def recommend_places(
    context: MeetingContext,
    places: list[KakaoPlaceResult],
    top_n: int = 3,
    api_key: Optional[str] = None,
) -> LLMRecommendationResult:
    """
    장소 추천 편의 함수
    
    Args:
        context: 모임 컨텍스트
        places: 장소 후보 리스트
        top_n: 추천할 장소 수
        api_key: Gemini API 키 (선택)
        
    Returns:
        LLMRecommendationResult
    """
    recommender = LLMRecommender(api_key=api_key)
    return await recommender.recommend(context, places, top_n)


async def full_recommendation_pipeline(
    purpose: str,
    locations: list[dict],
    preferences: list[dict],
    expected_count: int = 4,
    top_n: int = 3,
    kakao_api_key: Optional[str] = None,
    gemini_api_key: Optional[str] = None,
    # 장소 선택 방식
    location_choice_type: str = "center_location",
    preferred_district: Optional[str] = None,
    district_votes: Optional[dict[str, int]] = None,
    preferred_station: Optional[str] = None,
    station_votes: Optional[dict[str, int]] = None,
) -> dict:
    """
    전체 추천 파이프라인 (1단계 + 2단계 + 3단계)
    
    3가지 장소 선택 방식 지원:
    - center_location: 중간위치 찾기 (참가자 위치 기반)
    - preference_area: 선호 지역 선택 (구/동 투표)
    - preference_subway: 선호 지하철역 (역 근처)
    
    Args:
        purpose: 모임 목적
        locations: 참가자 위치 리스트 (center_location 방식일 때 필요)
        preferences: 참가자 선호도 리스트
        expected_count: 예상 참가자 수
        top_n: 추천할 장소 수
        kakao_api_key: 카카오 API 키 (선택, 환경변수에서 가져옴)
        gemini_api_key: Gemini API 키 (선택, 환경변수에서 가져옴)
        location_choice_type: 장소 선택 방식
        preferred_district: 선호 지역 (예: "강남구") - preference_area 방식
        district_votes: 지역별 투표 수 - preference_area 방식
        preferred_station: 선호 지하철역 (예: "강남") - preference_subway 방식
        station_votes: 역별 투표 수 - preference_subway 방식
        
    Returns:
        {
            "context": MeetingContext,
            "keywords": list[SearchKeyword],
            "places": list[KakaoPlaceResult],
            "recommendations": LLMRecommendationResult,
        }
        
    Example (중간위치 방식):
        >>> result = await full_recommendation_pipeline(
        ...     purpose="dining",
        ...     locations=[{"address": "서울 강남구 역삼동"}],
        ...     preferences=[{"food_types": ["korean"]}],
        ...     location_choice_type="center_location",
        ... )
        
    Example (선호 지역 방식):
        >>> result = await full_recommendation_pipeline(
        ...     purpose="dining",
        ...     locations=[],
        ...     preferences=[{"food_types": ["korean"]}],
        ...     location_choice_type="preference_area",
        ...     preferred_district="홍대",
        ... )
        
    Example (선호 지하철역 방식):
        >>> result = await full_recommendation_pipeline(
        ...     purpose="dining",
        ...     locations=[],
        ...     preferences=[{"food_types": ["korean"]}],
        ...     location_choice_type="preference_subway",
        ...     preferred_station="홍대입구",
        ... )
    """
    from .place_searcher import PlaceSearcher
    
    # 1-2단계: 데이터 수집 + 장소 검색
    searcher = PlaceSearcher()
    pipeline_result = await searcher.full_search_pipeline(
        purpose=purpose,
        locations=locations,
        preferences=preferences,
        expected_count=expected_count,
        location_choice_type=location_choice_type,
        preferred_district=preferred_district,
        district_votes=district_votes,
        preferred_station=preferred_station,
        station_votes=station_votes,
    )
    
    # 3단계: LLM 추천
    recommender = LLMRecommender(api_key=gemini_api_key)
    recommendations = await recommender.recommend(
        context=pipeline_result["context"],
        places=pipeline_result["places"],
        top_n=top_n,
    )
    
    return {
        **pipeline_result,
        "recommendations": recommendations,
    }
