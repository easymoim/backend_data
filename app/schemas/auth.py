from pydantic import BaseModel
from app.schemas.user import UserResponse


class KakaoLoginRequest(BaseModel):
    """Kakao 로그인 요청 스키마"""
    access_token: str


class KakaoLoginResponse(BaseModel):
    """Kakao 로그인 응답 스키마"""
    user: UserResponse
    access_token: str  # JWT 토큰 (선택사항, 나중에 추가 가능)
    is_new_user: bool  # 신규 사용자 여부

