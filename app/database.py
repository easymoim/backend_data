from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """애플리케이션 설정"""
    DATABASE_PASSWORD: str = ""
    DATABASE_URL: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# DATABASE_URL이 직접 설정되지 않은 경우 Supabase URL 구성
if not settings.DATABASE_URL:
    if not settings.DATABASE_PASSWORD:
        raise ValueError("DATABASE_PASSWORD 환경 변수가 설정되지 않았습니다. .env 파일에 DATABASE_PASSWORD를 설정해주세요.")
    settings.DATABASE_URL = f"postgresql://postgres:{settings.DATABASE_PASSWORD}@db.wxuunspyyvqndpodtesy.supabase.co:5432/postgres"

# SQLAlchemy 엔진 생성
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=True  # 개발 모드: SQL 쿼리 로깅
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성 (모든 모델이 상속받을 클래스)
Base = declarative_base()

def get_db():
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

