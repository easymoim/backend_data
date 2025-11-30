from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.database import Base


class LocationType(str, enum.Enum):
    """장소 선택 타입 (LocationChoiceType과 동일)"""
    CENTER_LOCATION = "center_location"
    PREFERENCE_AREA = "preference_area"
    PREFERENCE_SUBWAY = "preference_subway"


class PlaceCandidate(Base):
    """장소 후보 모델"""
    __tablename__ = "place_candidate"

    id = Column(String(255), primary_key=True, index=True)  # API Place ID 사용
    meeting_id = Column(UUID(as_uuid=True), ForeignKey("meeting.id"), nullable=False, index=True)
    
    location = Column(String(255), nullable=True)  # 지역, 정확한 위치 (위도 경도) → ex 강남구, 용산구
    preference_subway = Column(JSON, nullable=True)  # {"서울역", "종각"}
    preference_area = Column(JSON, nullable=True)  # {"강남구", "강동구", "마포구"}
    food = Column(String(255), nullable=True)
    condition = Column(String(255), nullable=True)
    location_type = Column(String(50), nullable=True)  # center_location, preference_area, preference_subway (Enum을 문자열로 저장)
    
    # 관계
    meeting = relationship("Meeting")

