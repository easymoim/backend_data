from sqlalchemy import Column, String, DateTime, Date, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database import Base


class EventActivityInformation(Base):
    """문화행사/활동 정보 모델"""
    __tablename__ = "event_activity_information"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # 기본 정보
    category = Column(String, nullable=True)  # 카테고리 (클래식, 뮤지컬/오페라 등)
    city_name = Column(String, nullable=True)  # 도시명
    guname = Column(String, nullable=True)  # 구 이름
    title = Column(String, nullable=True)  # 행사 제목
    date = Column(String, nullable=True)  # 행사 날짜 (예: 2026-04-16~2026-04-16)
    place = Column(String, nullable=True)  # 장소
    organization_name = Column(String, nullable=True)  # 주최 기관명
    
    # 이용 정보
    use_target = Column(String, nullable=True)  # 이용 대상
    use_fee = Column(String, nullable=True)  # 이용 요금
    inquiry = Column(String, nullable=True)  # 문의 번호
    program_info = Column(Text, nullable=True)  # 프로그램 정보
    
    # 링크 및 이미지
    organization_link = Column(String, nullable=True)  # 기관 링크
    thumbnail_image = Column(String, nullable=True)  # 썸네일 이미지 URL
    hompage_link = Column(String, nullable=True)  # 홈페이지 링크
    
    # 날짜/시간 정보
    register_date = Column(Date, nullable=True)  # 등록 날짜
    start_date = Column(DateTime, nullable=True)  # 시작 일시
    end_date = Column(DateTime, nullable=True)  # 종료 일시
    program_time = Column(String, nullable=True)  # 프로그램 시간
    
    # 위치 정보
    longitude = Column(String, nullable=True)  # 경도 (LOT)
    latitude = Column(String, nullable=True)  # 위도 (LAT)
    
    # 기타 정보
    host_type = Column(String, nullable=True)  # 주최자 유형 (시민/기관)
    is_free = Column(String, nullable=True)  # 무료 여부

