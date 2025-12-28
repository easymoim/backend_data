from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from pydantic import BaseSettings
from urllib.parse import quote_plus
import ssl

class Settings(BaseSettings):
    """애플리케이션 설정"""
    DATABASE_PASSWORD: str = ""
    DATABASE_URL: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # 환경변수에서 추가 필드 허용

settings = Settings()

# DATABASE_URL 구성
if not settings.DATABASE_URL:
    if not settings.DATABASE_PASSWORD:
        raise ValueError(
            "DATABASE_PASSWORD 환경 변수가 설정되지 않았습니다. .env 파일에 DATABASE_PASSWORD를 설정해주세요.\n"
            "또는 Supabase 대시보드에서 제공하는 전체 DATABASE_URL을 .env 파일에 직접 설정할 수 있습니다."
        )
    encoded_password = quote_plus(settings.DATABASE_PASSWORD)
    # pg8000 드라이버 사용
    db_url = f"postgresql+pg8000://postgres:{encoded_password}@db.wxuunspyyvqndpodtesy.supabase.co:5432/postgres"
else:
    db_url = settings.DATABASE_URL
    # postgresql:// → postgresql+pg8000://
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+pg8000://", 1)
    elif db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+pg8000://", 1)

# SSL 컨텍스트 생성 (Supabase 연결용)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# 환경에 따른 설정
import os
is_production = os.getenv("ENVIRONMENT", "development").lower() == "production" or os.getenv("VERCEL") == "1"
db_echo = os.getenv("DB_ECHO", "false").lower() == "true"  # 환경 변수로 제어 가능

# SQLAlchemy 엔진 생성
# 서버리스 환경 최적화 설정
# pg8000 드라이버는 connect_timeout/timeout 파라미터를 지원하지 않음
engine = create_engine(
    db_url,
    poolclass=NullPool,  # 서버리스 환경 호환 (Vercel)
    echo=db_echo,  # 환경 변수로 제어 (기본값: False, 프로덕션에서는 비활성화)
    connect_args={
        "ssl_context": ssl_context,
        # pg8000은 timeout 파라미터를 지원하지 않으므로 제거
    },
    # 쿼리 실행 최적화
    execution_options={
        "autocommit": False,
    },
    # 서버리스 환경에서 성능 최적화
    future=True,  # SQLAlchemy 2.0 스타일 사용
    # 연결 풀 설정 (NullPool이지만 명시적으로 설정)
    pool_reset_on_return='commit',  # 연결 반환 시 커밋으로 리셋
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
    except Exception as e:
        # 에러 발생 시 롤백
        db.rollback()
        raise
    finally:
        db.close()
