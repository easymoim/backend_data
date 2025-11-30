"""
카카오 로컬 API 클라이언트

카카오 로컬 API를 사용하여 장소 검색, 주소 변환 등의 기능을 제공합니다.

API 문서: https://developers.kakao.com/docs/latest/ko/local/dev-guide
"""

import httpx
from typing import Optional
import os
from functools import lru_cache

from .schemas import KakaoPlaceResult, KeywordSearchParams, CenterLocation


class KakaoLocalClient:
    """카카오 로컬 API 클라이언트"""
    
    BASE_URL = "https://dapi.kakao.com/v2/local"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: 카카오 REST API 키. 없으면 환경변수 KAKAO_REST_API_KEY에서 가져옴
        """
        self.api_key = api_key or os.getenv("KAKAO_REST_API_KEY")
        if not self.api_key:
            raise ValueError(
                "카카오 REST API 키가 필요합니다. "
                "생성자에 api_key를 전달하거나 KAKAO_REST_API_KEY 환경변수를 설정하세요."
            )
    
    @property
    def _headers(self) -> dict:
        """API 요청 헤더"""
        return {"Authorization": f"KakaoAK {self.api_key}"}
    
    async def search_by_keyword(
        self,
        query: str,
        x: Optional[str] = None,
        y: Optional[str] = None,
        radius: int = 5000,
        page: int = 1,
        size: int = 15,
        sort: str = "accuracy",
    ) -> dict:
        """
        키워드로 장소 검색
        
        Args:
            query: 검색 키워드
            x: 중심 좌표 경도 (longitude)
            y: 중심 좌표 위도 (latitude)
            radius: 검색 반경 (미터, 최대 20000)
            page: 페이지 번호 (1~45)
            size: 한 페이지에 보여질 문서 수 (1~15)
            sort: 정렬 기준 (accuracy: 정확도순, distance: 거리순)
            
        Returns:
            카카오 API 응답 (meta, documents 포함)
        """
        url = f"{self.BASE_URL}/search/keyword.json"
        
        params = {
            "query": query,
            "page": page,
            "size": size,
            "sort": sort,
        }
        
        # 중심 좌표가 있으면 추가
        if x and y:
            params["x"] = x
            params["y"] = y
            params["radius"] = radius
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self._headers, params=params)
            response.raise_for_status()
            return response.json()
    
    async def search_by_keyword_with_params(
        self, 
        params: KeywordSearchParams
    ) -> dict:
        """
        KeywordSearchParams 객체를 사용한 키워드 검색
        
        Args:
            params: 검색 파라미터 객체
            
        Returns:
            카카오 API 응답
        """
        return await self.search_by_keyword(
            query=params.query,
            x=params.x,
            y=params.y,
            radius=params.radius,
            page=params.page,
            size=params.size,
            sort=params.sort,
        )
    
    async def search_by_category(
        self,
        category_group_code: str,
        x: str,
        y: str,
        radius: int = 5000,
        page: int = 1,
        size: int = 15,
        sort: str = "accuracy",
    ) -> dict:
        """
        카테고리로 장소 검색
        
        Args:
            category_group_code: 카테고리 그룹 코드
                - MT1: 대형마트
                - CS2: 편의점
                - PS3: 어린이집, 유치원
                - SC4: 학교
                - AC5: 학원
                - PK6: 주차장
                - OL7: 주유소, 충전소
                - SW8: 지하철역
                - BK9: 은행
                - CT1: 문화시설
                - AG2: 중개업소
                - PO3: 공공기관
                - AT4: 관광명소
                - AD5: 숙박
                - FD6: 음식점
                - CE7: 카페
                - HP8: 병원
                - PM9: 약국
            x: 중심 좌표 경도
            y: 중심 좌표 위도
            radius: 검색 반경 (미터, 최대 20000)
            page: 페이지 번호
            size: 한 페이지에 보여질 문서 수
            sort: 정렬 기준
            
        Returns:
            카카오 API 응답
        """
        url = f"{self.BASE_URL}/search/category.json"
        
        params = {
            "category_group_code": category_group_code,
            "x": x,
            "y": y,
            "radius": radius,
            "page": page,
            "size": size,
            "sort": sort,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self._headers, params=params)
            response.raise_for_status()
            return response.json()
    
    async def search_address(self, query: str) -> dict:
        """
        주소로 좌표 변환 (주소 검색)
        
        Args:
            query: 검색할 주소
            
        Returns:
            카카오 API 응답 (좌표 정보 포함)
        """
        url = f"{self.BASE_URL}/search/address.json"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, 
                headers=self._headers, 
                params={"query": query}
            )
            response.raise_for_status()
            return response.json()
    
    async def coord_to_address(self, x: str, y: str) -> dict:
        """
        좌표로 주소 변환
        
        Args:
            x: 경도 (longitude)
            y: 위도 (latitude)
            
        Returns:
            카카오 API 응답 (주소 정보 포함)
        """
        url = f"{self.BASE_URL}/geo/coord2address.json"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=self._headers,
                params={"x": x, "y": y}
            )
            response.raise_for_status()
            return response.json()
    
    async def coord_to_region(self, x: str, y: str) -> dict:
        """
        좌표로 행정구역 정보 변환
        
        Args:
            x: 경도 (longitude)
            y: 위도 (latitude)
            
        Returns:
            카카오 API 응답 (행정구역 정보 포함)
        """
        url = f"{self.BASE_URL}/geo/coord2regioncode.json"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=self._headers,
                params={"x": x, "y": y}
            )
            response.raise_for_status()
            return response.json()
    
    # ============================================================
    # 헬퍼 메서드
    # ============================================================
    
    async def get_address_coordinates(self, address: str) -> Optional[CenterLocation]:
        """
        주소를 좌표로 변환하여 CenterLocation 객체로 반환
        
        Args:
            address: 검색할 주소
            
        Returns:
            CenterLocation 객체 또는 None
        """
        result = await self.search_address(address)
        documents = result.get("documents", [])
        
        if not documents:
            return None
        
        doc = documents[0]
        
        # 지역구 추출 (예: "서울 강남구" -> "강남구")
        address_parts = doc.get("address_name", "").split()
        district = None
        for part in address_parts:
            if part.endswith("구") or part.endswith("군") or part.endswith("시"):
                district = part
                break
        
        return CenterLocation(
            latitude=float(doc["y"]),
            longitude=float(doc["x"]),
            address=doc.get("address_name"),
            district=district,
        )
    
    async def get_region_from_coordinates(
        self, 
        latitude: float, 
        longitude: float
    ) -> Optional[str]:
        """
        좌표로부터 지역구 이름 가져오기
        
        Args:
            latitude: 위도
            longitude: 경도
            
        Returns:
            지역구 이름 (예: "강남구") 또는 None
        """
        result = await self.coord_to_region(
            x=str(longitude), 
            y=str(latitude)
        )
        documents = result.get("documents", [])
        
        for doc in documents:
            if doc.get("region_type") == "H":  # 행정동
                return doc.get("region_2depth_name")  # 구/군
        
        return None
    
    def parse_place_results(
        self, 
        api_response: dict
    ) -> list[KakaoPlaceResult]:
        """
        카카오 API 응답을 KakaoPlaceResult 리스트로 파싱
        
        Args:
            api_response: 카카오 API 응답
            
        Returns:
            KakaoPlaceResult 리스트
        """
        documents = api_response.get("documents", [])
        return [KakaoPlaceResult(**doc) for doc in documents]


@lru_cache()
def get_kakao_client() -> KakaoLocalClient:
    """
    싱글톤 패턴으로 KakaoLocalClient 인스턴스 반환
    
    Returns:
        KakaoLocalClient 인스턴스
    """
    return KakaoLocalClient()

