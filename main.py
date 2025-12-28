from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 모델 import (테이블 생성용)
from app.database import engine, Base, settings
from app.models import (
    User,
    Meeting,
    Participant,
    MeetingTimeCandidate,
    TimeVote,
    Place,
    PlaceCandidate,
    PlaceVote,
    Review,
)
from app.api import api_router

# 개발 환경에서만 테이블 자동 생성 (프로덕션에서는 마이그레이션 사용)
is_production = os.getenv("ENVIRONMENT", "development").lower() == "production"
if not is_production:
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EasyMoim API",
    description="EasyMoim 백엔드 API",
    version="1.0.0"
)

# CORS 설정
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
if is_production:
    # 프로덕션: 환경 변수에서 허용 도메인 목록 가져오기
    if allowed_origins_env:
        allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
    else:
        allowed_origins = []  # 프로덕션에서는 명시적으로 설정 필요
    allow_credentials = True
else:
    # 개발 환경: localhost 도메인 명시적으로 허용
    # allow_credentials=True일 때는 "*"를 사용할 수 없으므로 명시적으로 지정
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]
    # 개발 환경에서도 credentials 허용
    allow_credentials = True

# CORS 미들웨어는 다른 미들웨어보다 먼저 등록되어야 함
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "Welcome to EasyMoim API"}


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}


if __name__ == "__main__":
    # 환경 변수에서 포트 가져오기 (기본값: 8000)
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=not is_production  # 프로덕션에서는 자동 재시작 비활성화
    )

