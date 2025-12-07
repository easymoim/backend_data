from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
from urllib.parse import quote_plus
import os

class Settings(BaseSettings):
    """애플리케이션 설정"""
    DATABASE_PASSWORD: str = ""
    DATABASE_URL: str = ""
    DATABASE_ECHO: bool = False  # SQL 쿼리 로깅 (기본값: False, 성능 향상)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# DATABASE_URL이 직접 설정되지 않은 경우 Supabase URL 구성
if not settings.DATABASE_URL:
    if not settings.DATABASE_PASSWORD:
        raise ValueError(
            "DATABASE_PASSWORD 환경 변수가 설정되지 않았습니다. .env 파일에 DATABASE_PASSWORD를 설정해주세요.\n"
            "또는 Supabase 대시보드에서 제공하는 전체 DATABASE_URL을 .env 파일에 직접 설정할 수 있습니다."
        )
    # 비밀번호에 특수문자가 있을 수 있으므로 URL 인코딩
    encoded_password = quote_plus(settings.DATABASE_PASSWORD)
    settings.DATABASE_URL = f"postgresql://postgres:{encoded_password}@db.wxuunspyyvqndpodtesy.supabase.co:5432/postgres"

# 환경 변수에서 echo 설정 확인 (우선순위: 환경 변수 > 설정 파일)
database_echo = os.getenv("DATABASE_ECHO", str(settings.DATABASE_ECHO)).lower() == "true"

# SQLAlchemy 엔진 생성
# Supabase는 SSL 연결을 요구하므로 connect_args에 sslmode 설정
# 연결 풀 설정으로 성능 최적화
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 연결 유효성 검사
    pool_size=10,  # 기본 연결 풀 크기
    max_overflow=20,  # 추가 연결 허용 수
    pool_recycle=3600,  # 1시간마다 연결 재활용 (Supabase 연결 제한 대응)
    echo=database_echo,  # 환경 변수로 제어 가능
    connect_args={
        "sslmode": "require",
        "connect_timeout": 10,  # 연결 타임아웃 10초
    }
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

