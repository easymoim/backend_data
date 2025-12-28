from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn
import os
from dotenv import load_dotenv
import time
from app.middleware.performance import PerformanceMiddleware, get_performance_stats

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
# Vercel에서는 VERCEL 환경 변수가 있음
is_vercel = os.getenv("VERCEL") == "1"
is_production = os.getenv("ENVIRONMENT", "development").lower() == "production" or is_vercel

if not is_production:
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EasyMoim API",
    description="EasyMoim 백엔드 API",
    version="1.0.0"
)

# CORS 설정
# Vercel 배포 환경에서는 항상 localhost를 허용하도록 설정
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")

# 기본 localhost origins (항상 포함)
localhost_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

# 프로덕션 도메인 (기본값으로 포함)
production_origins = [
    "https://easymoim.com",
    "https://www.easymoim.com",
]

# 허용할 origins 초기화
allowed_origins = localhost_origins.copy()

# 프로덕션 환경에서는 프로덕션 도메인도 추가
if is_production:
    for origin in production_origins:
        if origin not in allowed_origins:
            allowed_origins.append(origin)

# 환경 변수에서 추가 origins 가져오기
if allowed_origins_env:
    env_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
    for origin in env_origins:
        if origin not in allowed_origins:
            allowed_origins.append(origin)

allow_credentials = True

# CORS 미들웨어는 다른 미들웨어보다 먼저 등록되어야 함
# Vercel 환경에서도 확실하게 작동하도록 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],  # 빈 리스트 방지
    allow_credentials=allow_credentials if allowed_origins else False,  # "*"일 때는 credentials 비활성화
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],  # 명시적으로 지정
    allow_headers=["*"],  # 모든 헤더 허용
    expose_headers=["*"],  # 모든 헤더 노출
    max_age=3600,  # preflight 요청 캐시 시간 (1시간)
)

# 성능 측정 미들웨어 추가
app.add_middleware(PerformanceMiddleware)

# 전역 예외 핸들러 추가
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP 예외 핸들러"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """요청 검증 에러 핸들러"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """일반 예외 핸들러 (서버 에러)"""
    import traceback
    error_detail = traceback.format_exc()
    
    # 프로덕션에서는 상세 에러 숨김
    if is_production:
        detail = "서버 내부 오류가 발생했습니다."
    else:
        detail = f"서버 오류: {str(exc)}"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail}
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


@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """OPTIONS 요청 핸들러 (CORS preflight)"""
    return {"message": "OK"}


@app.get("/api/v1/performance/stats")
async def get_performance_statistics():
    """
    성능 통계 조회 엔드포인트
    
    - total_requests: 총 요청 수
    - average_time: 평균 처리 시간 (초)
    - min_time / max_time: 최소/최대 처리 시간
    - endpoints: 엔드포인트별 상세 통계
      - count: 요청 수
      - avg_time: 평균 시간
      - min_time / max_time: 최소/최대 시간
      - errors: 에러 수
      - error_rate: 에러율 (%)
      - recent_times: 최근 10개 요청 시간
    - slow_requests: 느린 요청 목록 (1초 이상)
    - recent_requests: 최근 20개 요청 상세 정보
    """
    return get_performance_stats()


if __name__ == "__main__":
    # 환경 변수에서 포트 가져오기 (기본값: 8000)
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=not is_production  # 프로덕션에서는 자동 재시작 비활성화
    )

