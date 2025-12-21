"""
장소 검색 전체 파이프라인 테스트

사용법:
    # 중간위치 방식 테스트
    uv run python test_place_search.py --location_choice_type center_location
    
    # 선호 지역 방식 테스트
    uv run python test_place_search.py --location_choice_type preference_area
    
    # 선호 지하철역 방식 테스트
    uv run python test_place_search.py --location_choice_type preference_subway
"""

import asyncio
import argparse
import csv
import os
from datetime import datetime
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

from app.core.place_search import (
    full_recommendation_pipeline,
    LocationChoiceType,
)


# ============================================================
# 더미 데이터
# ============================================================

# 중간위치 방식용 더미 데이터
DUMMY_CENTER_LOCATION = {
    "locations": [
        {"address": "서울 강남구 역삼동", "district": "강남구"},
        {"address": "서울 서초구 서초동", "district": "서초구"},
        {"address": "서울 강남구 삼성동", "district": "강남구"},
    ],
    "preferences": [
        {"food_types": ["한식"], "atmospheres": ["조용한"], "conditions": ["주차"]},
        {"food_types": ["고기"], "atmospheres": ["넓은"], "conditions": ["단체석"]},
        {"food_types": ["한식", "고기"], "atmospheres": ["조용한"], "conditions": []},
    ],
}

# 선호 지역 방식용 더미 데이터
DUMMY_PREFERENCE_AREA = {
    "preferred_district": "마포구",
    "district_votes": {"마포구": 4, "강남구": 2, "종로구": 1},
    "preferences": [
        {"food_types": ["한식"], "atmospheres": ["활기찬"], "conditions": []},
        {"food_types": ["양식"], "atmospheres": ["로맨틱한"], "conditions": ["예약가능"]},
        {"food_types": ["한식", "양식"], "atmospheres": ["아늑한"], "conditions": []},
    ],
}

# 선호 지하철역 방식용 더미 데이터 (5명 참가자, 일부 선호도 중복)
DUMMY_PREFERENCE_SUBWAY = {
    "preferred_station": "홍대입구",
    "station_votes": {"홍대입구": 5, "강남": 2, "건대입구": 1},
    "preferences": [
        {"food_types": ["한식", "고기"], "atmospheres": ["활기찬"], "conditions": ["단체석"]},
        {"food_types": ["한식"], "atmospheres": ["활기찬", "아늑한"], "conditions": ["24시간"]},
        {"food_types": ["한식", "일식"], "atmospheres": ["활기찬"], "conditions": []},
        {"food_types": ["일식"], "atmospheres": ["모던한", "조용한"], "conditions": ["24시간"]},
        {"food_types": ["아시안"], "atmospheres": ["활기찬"], "conditions": ["단체석"]},
    ],
}


# ============================================================
# 테스트 함수
# ============================================================

async def test_center_location():
    """중간위치 방식 테스트"""
    print("=" * 70)
    print("📍 장소 선택 방식: center_location (중간위치 찾기)")
    print("=" * 70)
    
    data = DUMMY_CENTER_LOCATION
    
    print("\n📊 입력 데이터:")
    print(f"  참가자 위치:")
    for loc in data["locations"]:
        print(f"    - {loc['address']} ({loc['district']})")
    print(f"\n  참가자 선호도:")
    for i, pref in enumerate(data["preferences"], 1):
        print(f"    {i}. 음식: {pref['food_types']}, 분위기: {pref['atmospheres']}")
    
    print("\n⏳ 파이프라인 실행 중...")
    
    result = await full_recommendation_pipeline(
        purpose="dining",
        locations=data["locations"],
        preferences=data["preferences"],
        expected_count=len(data["preferences"]) + 2,
        top_n=3,
        location_choice_type="center_location",
    )
    
    _print_result(result)
    return result


async def test_preference_area():
    """선호 지역 방식 테스트"""
    print("=" * 70)
    print("📍 장소 선택 방식: preference_area (선호 지역 선택)")
    print("=" * 70)
    
    data = DUMMY_PREFERENCE_AREA
    
    print("\n📊 입력 데이터:")
    print(f"  선호 지역: {data['preferred_district']}")
    print(f"  지역 투표 결과:")
    for district, votes in data["district_votes"].items():
        print(f"    - {district}: {votes}표")
    print(f"\n  참가자 선호도:")
    for i, pref in enumerate(data["preferences"], 1):
        print(f"    {i}. 음식: {pref['food_types']}, 분위기: {pref['atmospheres']}")
    
    print("\n⏳ 파이프라인 실행 중...")
    
    result = await full_recommendation_pipeline(
        purpose="dining",
        locations=[],  # 선호 지역 방식은 위치 필요 없음
        preferences=data["preferences"],
        expected_count=len(data["preferences"]) + 2,
        top_n=3,
        location_choice_type="preference_area",
        preferred_district=data["preferred_district"],
        district_votes=data["district_votes"],
    )
    
    _print_result(result)
    return result


async def test_preference_subway():
    """선호 지하철역 방식 테스트"""
    print("=" * 70)
    print("📍 장소 선택 방식: preference_subway (선호 지하철역)")
    print("=" * 70)
    
    data = DUMMY_PREFERENCE_SUBWAY
    
    print("\n📊 입력 데이터:")
    print(f"  선호 지하철역: {data['preferred_station']}역")
    print(f"  역 투표 결과:")
    for station, votes in data["station_votes"].items():
        print(f"    - {station}역: {votes}표")
    print(f"\n  참가자 선호도:")
    for i, pref in enumerate(data["preferences"], 1):
        print(f"    {i}. 음식: {pref['food_types']}, 분위기: {pref['atmospheres']}")
    
    print("\n⏳ 파이프라인 실행 중...")
    
    result = await full_recommendation_pipeline(
        purpose="dining",
        locations=[],  # 선호 역 방식은 위치 필요 없음
        preferences=data["preferences"],
        expected_count=len(data["preferences"]) + 2,
        top_n=3,
        location_choice_type="preference_subway",
        preferred_station=data["preferred_station"],
        station_votes=data["station_votes"],
    )
    
    _print_result(result)
    return result


def _save_to_csv(result: dict, location_choice_type: str):
    """결과를 CSV 파일로 저장"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. 추천 결과 CSV 저장
    recommendations_file = f"result_recommendations_{location_choice_type}_{timestamp}.csv"
    recommendations = result["recommendations"].recommendations
    
    with open(recommendations_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        # 헤더
        writer.writerow([
            '순위', '장소명', '추천이유', '매칭점수', '매칭된선호도',
            '도로명주소', '지번주소', '위도', '경도', '전화번호',
            '카테고리', '거리(m)', '장소URL', 'place_id'
        ])
        # 데이터
        for rec in recommendations:
            writer.writerow([
                rec.rank,
                rec.place_name,
                rec.reason,
                rec.match_score,
                ', '.join(rec.matched_preferences) if rec.matched_preferences else '',
                rec.address or '',
                rec.address_jibun or '',
                rec.latitude or '',
                rec.longitude or '',
                rec.phone or '',
                rec.category or '',
                rec.distance or '',
                rec.place_url or '',
                rec.place_id or '',
            ])
    
    print(f"\n📁 추천 결과 저장: {recommendations_file}")
    
    # 2. 전체 검색 결과 CSV 저장
    places_file = f"result_places_{location_choice_type}_{timestamp}.csv"
    places = result["places"]
    
    with open(places_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        # 헤더
        writer.writerow([
            '순번', '장소명', '카테고리', '도로명주소', '지번주소',
            '위도', '경도', '전화번호', '거리(m)', '장소URL', 'place_id'
        ])
        # 데이터
        for i, place in enumerate(places, 1):
            writer.writerow([
                i,
                place.place_name,
                place.category_name,
                place.road_address_name or '',
                place.address_name or '',
                place.y,  # 위도
                place.x,  # 경도
                place.phone or '',
                place.distance or '',
                place.place_url or '',
                place.id,
            ])
    
    print(f"📁 검색 결과 저장: {places_file}")
    
    # 3. 요약 정보 CSV 저장
    summary_file = f"result_summary_{location_choice_type}_{timestamp}.csv"
    context = result["context"]
    keywords = result["keywords"]
    rec_result = result["recommendations"]
    
    with open(summary_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['항목', '값'])
        writer.writerow(['장소선택방식', context.location_choice_type.value])
        writer.writerow(['모임목적', context.purpose])
        writer.writerow(['예상인원', context.expected_participant_count])
        writer.writerow(['검색중심지역', context.center_location.district if context.center_location else ''])
        writer.writerow(['검색중심위도', context.center_location.latitude if context.center_location else ''])
        writer.writerow(['검색중심경도', context.center_location.longitude if context.center_location else ''])
        writer.writerow(['선호지역', context.preferred_district or ''])
        writer.writerow(['선호역', context.preferred_station or ''])
        writer.writerow(['검색키워드', ' | '.join([kw.keyword for kw in keywords])])
        writer.writerow(['검색결과수', len(result["places"])])
        writer.writerow(['추천요약', rec_result.summary])
        writer.writerow(['사용모델', rec_result.model_used])
    
    print(f"📁 요약 정보 저장: {summary_file}")
    
    return recommendations_file, places_file, summary_file


def _print_result(result: dict):
    """파이프라인 결과 출력"""
    context = result["context"]
    keywords = result["keywords"]
    places = result["places"]
    recommendations = result["recommendations"]
    
    print("\n" + "=" * 70)
    print("✅ 파이프라인 완료!")
    print("=" * 70)
    
    # 컨텍스트 정보
    print("\n📋 모임 컨텍스트:")
    print(f"  장소 선택 방식: {context.location_choice_type.value}")
    print(f"  모임 목적: {context.purpose}")
    print(f"  예상 인원: {context.expected_participant_count}명")
    
    if context.center_location:
        print(f"  검색 중심 지역: {context.center_location.district}")
        if context.center_location.latitude and context.center_location.longitude:
            print(f"  검색 중심 좌표: ({context.center_location.latitude:.4f}, {context.center_location.longitude:.4f})")
    
    if context.preferred_district:
        print(f"  선호 지역: {context.preferred_district}")
    if context.preferred_station:
        print(f"  선호 역: {context.preferred_station}역")
    
    # 키워드
    print(f"\n🏷️ 생성된 검색 키워드:")
    for kw in keywords[:5]:
        print(f"  [{kw.priority}] {kw.keyword}")
    
    # 검색 결과
    print(f"\n🔍 카카오 API 검색 결과: 총 {len(places)}개")
    print("  상위 5개:")
    for i, place in enumerate(places[:5], 1):
        distance_str = f"{place.distance}m" if place.distance else "-"
        print(f"    {i}. {place.place_name}")
        print(f"       {place.category_name} | {place.road_address_name or place.address_name} | {distance_str}")
    
    # LLM 추천 결과
    print(f"\n🤖 LLM 추천 결과:")
    print(f"  모델: {recommendations.model_used}")
    print(f"  요약: {recommendations.summary}")
    
    print(f"\n🏆 추천 장소 TOP {len(recommendations.recommendations)}:")
    for rec in recommendations.recommendations:
        print(f"\n  [{rec.rank}위] {rec.place_name}")
        print(f"       추천 이유: {rec.reason[:100]}...")
        print(f"       매칭 점수: {rec.match_score}점")
        if rec.matched_preferences:
            print(f"       매칭된 선호도: {', '.join(rec.matched_preferences)}")
        print(f"       ---")
        print(f"       📍 주소: {rec.address or rec.address_jibun or '정보 없음'}")
        print(f"       📞 전화: {rec.phone or '정보 없음'}")
        print(f"       🔗 URL: {rec.place_url or '정보 없음'}")
        if rec.latitude and rec.longitude:
            print(f"       🗺️ 좌표: ({rec.latitude}, {rec.longitude})")
        if rec.distance:
            print(f"       📏 거리: {rec.distance}m")


async def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="장소 검색 파이프라인 테스트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 중간위치 방식 테스트
  uv run python test_place_search.py --location_choice_type center_location
  
  # 선호 지역 방식 테스트  
  uv run python test_place_search.py --location_choice_type preference_area
  
  # 선호 지하철역 방식 테스트
  uv run python test_place_search.py --location_choice_type preference_subway
        """
    )
    
    parser.add_argument(
        "--location_choice_type",
        "-t",
        type=str,
        choices=["center_location", "preference_area", "preference_subway"],
        required=True,
        help="장소 선택 방식 (center_location: 중간위치, preference_area: 선호지역, preference_subway: 선호역)"
    )
    
    args = parser.parse_args()
    
    # API 키 확인
    kakao_key = os.getenv("KAKAO_REST_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not kakao_key:
        print("❌ 오류: KAKAO_REST_API_KEY 환경변수가 설정되지 않았습니다.")
        return
    
    if not gemini_key:
        print("❌ 오류: GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
        return
    
    print(f"\n🚀 장소 검색 파이프라인 테스트")
    print(f"   카카오 API 키: {kakao_key[:8]}...")
    print(f"   Gemini API 키: {gemini_key[:8]}...")
    print()
    
    try:
        result = None
        if args.location_choice_type == "center_location":
            result = await test_center_location()
        elif args.location_choice_type == "preference_area":
            result = await test_preference_area()
        elif args.location_choice_type == "preference_subway":
            result = await test_preference_subway()
        
        # CSV 저장
        if result:
            _save_to_csv(result, args.location_choice_type)
        
        print("\n" + "=" * 70)
        print("✅ 테스트 완료!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
