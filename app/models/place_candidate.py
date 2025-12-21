from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSON, ENUM
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

class LocationType(str, enum.Enum):
    """장소 선택 타입 (LocationChoiceType과 동일)"""
    center_location = "center_location"
    preference_area = "preference_area"
    preference_subway = "preference_subway"

# DB에 이미 존재하는 enum 타입 참조 (create_type=False)
location_type_enum = ENUM(
    'center_location', 'preference_area', 'preference_subway',
    name='location_choice_type_enum',
    create_type=False
)

class PlaceCandidate(Base):
    """장소 후보 모델"""
    __tablename__ = "place_candidate"

    id = Column(String(255), primary_key=True, index=True)  # API Place ID 사용
    meeting_id = Column(UUID(as_uuid=True), ForeignKey("meeting.id"), nullable=False, index=True)
    
    location = Column(JSON, nullable=True)  # LLM 추천 결과 JSON (recommendations, summary 등)
    preference_subway = Column(JSON, nullable=True)  # {"서울역", "종각"}
    preference_area = Column(JSON, nullable=True)  # {"강남구", "강동구", "마포구"}
    food = Column(String(255), nullable=True)
    condition = Column(String(255), nullable=True)
    location_type = Column(location_type_enum, nullable=True)  # DB의 기존 enum 사용
    
    # 관계
    meeting = relationship("Meeting")

