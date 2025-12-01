from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

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
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
if is_production:
    # 프로덕션: 환경 변수에서 허용 도메인 목록 가져오기
    allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
    if not allowed_origins or "*" in allowed_origins:
        # 프로덕션에서 *는 보안상 위험하므로 기본값 사용
        allowed_origins = ["*"]  # 실제 배포 시 특정 도메인으로 변경 필요
else:
    # 개발 환경: 모든 도메인 허용
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

