from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class EventActivityInformationBase(BaseModel):
    """문화행사/활동 정보 기본 스키마"""
    category: Optional[str] = None  # 카테고리 (클래식, 뮤지컬/오페라 등)
    city_name: Optional[str] = None  # 도시명
    guname: Optional[str] = None  # 구 이름
    title: Optional[str] = None  # 행사 제목
    date: Optional[str] = None  # 행사 날짜
    place: Optional[str] = None  # 장소
    organization_name: Optional[str] = None  # 주최 기관명
    use_target: Optional[str] = None  # 이용 대상
    use_fee: Optional[str] = None  # 이용 요금
    inquiry: Optional[str] = None  # 문의 번호
    program_info: Optional[str] = None  # 프로그램 정보
    organization_link: Optional[str] = None  # 기관 링크
    thumbnail_image: Optional[str] = None  # 썸네일 이미지 URL
    host_type: Optional[str] = None  # 주최자 유형 (시민/기관)
    start_date: Optional[datetime] = None  # 시작 일시
    end_date: Optional[datetime] = None  # 종료 일시
    longitude: Optional[str] = None  # 경도
    latitude: Optional[str] = None  # 위도
    is_free: Optional[str] = None  # 무료 여부
    hompage_link: Optional[str] = None  # 홈페이지 링크
    program_time: Optional[str] = None  # 프로그램 시간


class EventActivityInformationCreate(EventActivityInformationBase):
    """문화행사/활동 정보 생성 스키마"""
    title: str  # 행사 제목 (필수)


class EventActivityInformationUpdate(BaseModel):
    """문화행사/활동 정보 업데이트 스키마"""
    category: Optional[str] = None
    city_name: Optional[str] = None
    guname: Optional[str] = None
    title: Optional[str] = None
    date: Optional[str] = None
    place: Optional[str] = None
    organization_name: Optional[str] = None
    use_target: Optional[str] = None
    use_fee: Optional[str] = None
    inquiry: Optional[str] = None
    program_info: Optional[str] = None
    organization_link: Optional[str] = None
    thumbnail_image: Optional[str] = None
    host_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    is_free: Optional[str] = None
    hompage_link: Optional[str] = None
    program_time: Optional[str] = None


class EventActivityInformationResponse(EventActivityInformationBase):
    """문화행사/활동 정보 응답 스키마"""
    id: UUID

    class Config:
        orm_mode = True
        # None 값을 허용하도록 설정
        allow_none = True
