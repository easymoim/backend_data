"""인증 관련 API"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud
from app.schemas.auth import KakaoLoginRequest, KakaoLoginResponse
from app.services.kakao import KakaoService

router = APIRouter()


@router.post("/kakao/login", response_model=KakaoLoginResponse, status_code=status.HTTP_200_OK)
async def kakao_login(
    request: KakaoLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Kakao OAuth 로그인
    
    프론트엔드에서 Kakao SDK로 받은 access_token을 전달받아
    사용자 정보를 조회하고 로그인 처리합니다.
    """
    # Kakao에서 사용자 정보 조회
    kakao_data = await KakaoService.get_user_info(request.access_token)
    
    if not kakao_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 Kakao access_token입니다."
        )
    
    # 사용자 정보 파싱
    user_info = KakaoService.parse_user_info(kakao_data)
    
    # 기존 사용자 확인
    db_user = crud.user.get_user_by_oauth(
        db,
        oauth_provider=user_info["oauth_provider"],
        oauth_id=user_info["oauth_id"]
    )
    
    is_new_user = False
    
    if db_user:
        # 기존 사용자 - 로그인
        # 이름이 변경되었을 수 있으므로 업데이트
        if db_user.name != user_info["name"]:
            from app.schemas.user import UserUpdate
            user_update = UserUpdate(name=user_info["name"])
            db_user = crud.user.update_user(db, user_id=db_user.id, user_update=user_update)
    else:
        # 신규 사용자 - 회원가입
        from app.schemas.user import UserCreate
        user_create = UserCreate(
            name=user_info["name"],
            email=user_info["email"],
            oauth_provider=user_info["oauth_provider"],
            oauth_id=user_info["oauth_id"],
        )
        db_user = crud.user.create_user(db, user=user_create)
        is_new_user = True
    
    return KakaoLoginResponse(
        user=db_user,
        access_token="",  # JWT 토큰은 나중에 추가 가능
        is_new_user=is_new_user
    )

