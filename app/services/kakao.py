"""Kakao OAuth 서비스"""
import httpx
from typing import Optional, Dict
from app.models.user import OAuthProvider


class KakaoService:
    """Kakao API 서비스"""
    
    KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"
    
    @staticmethod
    async def get_user_info(access_token: str) -> Optional[Dict]:
        """
        Kakao access_token으로 사용자 정보 조회
        
        Args:
            access_token: Kakao에서 발급받은 access_token
            
        Returns:
            사용자 정보 딕셔너리 또는 None
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    KakaoService.KAKAO_USER_INFO_URL,
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
                    
        except Exception as e:
            print(f"Kakao API 호출 오류: {e}")
            return None
    
    @staticmethod
    def parse_user_info(kakao_data: Dict) -> Dict:
        """
        Kakao 사용자 정보 파싱
        
        Args:
            kakao_data: Kakao API 응답 데이터
            
        Returns:
            파싱된 사용자 정보
        """
        kakao_account = kakao_data.get("kakao_account", {})
        profile = kakao_account.get("profile", {})
        
        # Kakao ID
        kakao_id = str(kakao_data.get("id", ""))
        
        # 이름 (닉네임 또는 이름)
        name = profile.get("nickname") or kakao_account.get("name") or None
        
        # 이메일 (이메일 동의가 필요한 경우)
        email = kakao_account.get("email", None)
        
        return {
            "oauth_provider": OAuthProvider.KAKAO,
            "oauth_id": kakao_id,
            "name": name,
            "email": email,
        }

