"""
LLM 기반 장소 추천 모듈

3단계: LLM 기반 추천 및 선택 (LLM Recommendation & Selection)
- 모임 컨텍스트와 장소 후보를 기반으로 최적의 장소 추천
- Gemini API 사용
"""

import json
import os
from typing import Optional

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
        self._client = None
    
    def _get_client(self):
        """Gemini 클라이언트 초기화 (지연 로딩)"""
        if self._client is None:
            if not self.api_key:
                raise ValueError(
                    "Gemini API 키가 필요합니다. "
                    "생성자에 api_key를 전달하거나 GEMINI_API_KEY 환경변수를 설정하세요."
                )
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._client = genai.GenerativeModel(self.model)
        return self._client
    
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
        prompt = self._build_prompt(prompt_context, top_n)
        
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
    
    def _build_prompt(self, context: LLMPromptContext, top_n: int) -> str:
        """LLM 프롬프트 생성"""
        
        # 모임 정보 요약
        purpose_kr = PURPOSE_KR.get(context.meeting_purpose, context.meeting_purpose)
        food_types_kr = [FOOD_TYPE_KR.get(f, f) for f in context.preferred_food_types]
        atmospheres_kr = [ATMOSPHERE_KR.get(a, a) for a in context.preferred_atmospheres]
        conditions_kr = [CONDITION_KR.get(c, c) for c in context.required_conditions]
        
        meeting_info = f"""
## 모임 정보
- **모임 유형**: {purpose_kr}
- **참가 인원**: {context.participant_count}명
- **지역**: {context.center_district or "미정"}
"""
        if context.meeting_title:
            meeting_info += f"- **모임명**: {context.meeting_title}\n"
        if context.meeting_description:
            meeting_info += f"- **모임 설명**: {context.meeting_description}\n"
        
        preferences_info = """
## 참가자 선호도
"""
        if food_types_kr:
            preferences_info += f"- **선호 음식**: {', '.join(food_types_kr)}\n"
        if atmospheres_kr:
            preferences_info += f"- **선호 분위기**: {', '.join(atmospheres_kr)}\n"
        if conditions_kr:
            preferences_info += f"- **필요 조건**: {', '.join(conditions_kr)}\n"
        
        # 장소 후보 목록
        candidates_info = """
## 장소 후보 목록
"""
        for i, c in enumerate(context.candidates[:20], 1):  # 최대 20개
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

JSON 형식으로만 응답해주세요.
"""
        return prompt
    
    # ============================================================
    # LLM 호출
    # ============================================================
    
    async def _call_llm(self, prompt: str) -> str:
        """Gemini API 호출"""
        client = self._get_client()
        
        response = client.generate_content(prompt)
        return response.text
    
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
        
        # PlaceRecommendation 리스트 생성
        recommendations = []
        for rec in data.get("recommendations", []):
            recommendations.append(PlaceRecommendation(
                place_id=rec.get("place_id", ""),
                place_name=rec.get("place_name", ""),
                rank=rec.get("rank", len(recommendations) + 1),
                reason=rec.get("reason", ""),
                match_score=rec.get("match_score"),
                matched_preferences=rec.get("matched_preferences", []),
                considerations=rec.get("considerations", []),
            ))
        
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
                matched_preferences=[],
                considerations=["LLM 응답 파싱 실패로 기본 추천이 제공되었습니다."],
            ))
        
        purpose_kr = PURPOSE_KR.get(context.meeting_purpose, context.meeting_purpose)
        
        return LLMRecommendationResult(
            recommendations=recommendations,
            summary=f"기본 추천 결과입니다. (파싱 오류: {error})",
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
) -> dict:
    """
    전체 추천 파이프라인 (1단계 + 2단계 + 3단계)
    
    Args:
        purpose: 모임 목적
        locations: 참가자 위치 리스트
        preferences: 참가자 선호도 리스트
        expected_count: 예상 참가자 수
        top_n: 추천할 장소 수
        kakao_api_key: 카카오 API 키 (선택, 환경변수에서 가져옴)
        gemini_api_key: Gemini API 키 (선택, 환경변수에서 가져옴)
        
    Returns:
        {
            "context": MeetingContext,
            "keywords": list[SearchKeyword],
            "places": list[KakaoPlaceResult],
            "recommendations": LLMRecommendationResult,
        }
    """
    from .place_searcher import PlaceSearcher
    
    # 1-2단계: 데이터 수집 + 장소 검색
    searcher = PlaceSearcher()
    pipeline_result = await searcher.full_search_pipeline(
        purpose=purpose,
        locations=locations,
        preferences=preferences,
        expected_count=expected_count,
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

