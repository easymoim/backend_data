"""
지하철역 유틸리티

지하철역 좌표 조회 기능 (카카오 API 사용)
"""

from typing import Optional

from .schemas import CenterLocation


# 주요 역-지역구 매핑 (하드코딩)
STATION_DISTRICT_MAP = {
    "강남": "강남구",
    "홍대입구": "마포구",
    "잠실": "송파구",
    "사당": "동작구",
    "건대입구": "광진구",
    "신림": "관악구",
    "서울대입구": "관악구",
    "선릉": "강남구",
    "역삼": "강남구",
    "삼성": "강남구",
    "교대": "서초구",
    "서초": "서초구",
    "신촌": "서대문구",
    "이대": "서대문구",
    "합정": "마포구",
    "망원": "마포구",
    "여의도": "영등포구",
    "영등포": "영등포구",
    "노원": "노원구",
    "천호": "강동구",
    "고속터미널": "서초구",
    "종로3가": "종로구",
    "을지로입구": "중구",
    "명동": "중구",
    "광화문": "종로구",
    "시청": "중구",
    "동대문": "동대문구",
    "왕십리": "성동구",
    "성수": "성동구",
    "압구정": "강남구",
    "청담": "강남구",
    "신사": "강남구",
    "양재": "서초구",
    "신도림": "구로구",
    "구로디지털단지": "구로구",
    "가산디지털단지": "금천구",
    "종각": "종로구",
    "을지로3가": "중구",
    "충무로": "중구",
    "약수": "중구",
    "한양대": "성동구",
    "뚝섬": "성동구",
    "강변": "광진구",
    "잠실나루": "송파구",
    "석촌": "송파구",
    "송파": "송파구",
    "가락시장": "송파구",
    "수서": "강남구",
    "대치": "강남구",
    "도곡": "강남구",
    "매봉": "강남구",
    "양재시민의숲": "서초구",
}


async def get_station_coordinates(
    station_name: str,
    kakao_client: "KakaoLocalClient"
) -> Optional[CenterLocation]:
    """
    지하철역의 좌표 조회 (카카오 API 사용)
    
    Args:
        station_name: 역명 (예: "강남", "홍대입구")
        kakao_client: 카카오 API 클라이언트
        
    Returns:
        CenterLocation 또는 None
    """
    # "강남역" 형태로 검색
    search_query = f"{station_name}역" if not station_name.endswith("역") else station_name
    
    try:
        result = await kakao_client.search_by_keyword(
            query=search_query,
            size=1,
        )
        
        documents = result.get("documents", [])
        if documents:
            doc = documents[0]
            
            # 지역구 추출
            address = doc.get("road_address_name") or doc.get("address_name", "")
            district = None
            for part in address.split():
                if part.endswith("구") or part.endswith("군"):
                    district = part
                    break
            
            return CenterLocation(
                latitude=float(doc["y"]),
                longitude=float(doc["x"]),
                address=address,
                district=district,
            )
    except Exception as e:
        print(f"지하철역 좌표 조회 실패 '{station_name}': {e}")
    
    return None


def get_district_from_station(station_name: str) -> Optional[str]:
    """
    지하철역 이름에서 지역구 추정 (하드코딩 매핑)
    
    Args:
        station_name: 역명 (예: "강남", "홍대입구역")
        
    Returns:
        지역구 (예: "강남구") 또는 None
    """
    clean_name = station_name.replace("역", "").strip()
    return STATION_DISTRICT_MAP.get(clean_name)
