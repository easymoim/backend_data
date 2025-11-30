# 카카오 로그인 사용 가이드

## 📋 개요

백엔드에서 카카오 OAuth 로그인을 처리하는 API가 구현되어 있습니다.
프론트엔드에서 카카오 SDK로 로그인한 후 받은 `access_token`을 백엔드로 전송하면 됩니다.

## 🔄 로그인 플로우

```
1. 프론트엔드: 카카오 SDK로 로그인
   ↓
2. 프론트엔드: access_token 받음
   ↓
3. 프론트엔드 → 백엔드: access_token 전송
   ↓
4. 백엔드: 카카오 API로 사용자 정보 조회
   ↓
5. 백엔드: DB에 사용자 저장/조회
   ↓
6. 백엔드 → 프론트엔드: 사용자 정보 반환
```

## 🚀 API 엔드포인트

### POST `/api/v1/auth/kakao/login`

카카오 로그인 처리

**Request Body:**
```json
{
  "access_token": "카카오에서_받은_access_token"
}
```

**Response (200 OK):**
```json
{
  "user": {
    "id": 1,
    "name": "홍길동",
    "email": "user@example.com",
    "oauth_provider": "kakao",
    "oauth_id": "123456789",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  },
  "access_token": "",
  "is_new_user": false
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "유효하지 않은 Kakao access_token입니다."
}
```

## 💻 프론트엔드 예제

### React/Next.js 예제

```typescript
// 카카오 SDK 초기화 (한 번만 실행)
useEffect(() => {
  if (typeof window !== 'undefined' && !window.Kakao.isInitialized()) {
    window.Kakao.init('YOUR_KAKAO_JS_KEY');
  }
}, []);

// 카카오 로그인 함수
const handleKakaoLogin = async () => {
  try {
    // 1. 카카오 로그인
    const response = await window.Kakao.Auth.login({
      scope: 'profile_nickname,account_email', // 필요한 정보 동의
    });
    
    // 2. access_token 받기
    const accessToken = response.access_token;
    
    // 3. 백엔드로 전송
    const loginResponse = await fetch('http://localhost:8000/api/v1/auth/kakao/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        access_token: accessToken,
      }),
    });
    
    if (loginResponse.ok) {
      const data = await loginResponse.json();
      console.log('로그인 성공:', data.user);
      console.log('신규 사용자:', data.is_new_user);
      
      // 사용자 정보 저장 (예: localStorage, state 등)
      localStorage.setItem('user', JSON.stringify(data.user));
    } else {
      console.error('로그인 실패');
    }
  } catch (error) {
    console.error('카카오 로그인 오류:', error);
  }
};
```

### JavaScript (Vanilla) 예제

```javascript
// 카카오 SDK 초기화
Kakao.init('YOUR_KAKAO_JS_KEY');

// 카카오 로그인
async function kakaoLogin() {
  try {
    // 1. 카카오 로그인
    const response = await Kakao.Auth.login({
      scope: 'profile_nickname,account_email',
    });
    
    // 2. 백엔드로 access_token 전송
    const res = await fetch('http://localhost:8000/api/v1/auth/kakao/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        access_token: response.access_token,
      }),
    });
    
    const data = await res.json();
    console.log('로그인 성공:', data);
  } catch (error) {
    console.error('오류:', error);
  }
}
```

## 🧪 테스트 방법

### 1. Swagger UI에서 테스트

1. 서버 실행: `uv run python main.py`
2. 브라우저에서 `http://localhost:8000/docs` 접속
3. `/api/v1/auth/kakao/login` 엔드포인트 찾기
4. "Try it out" 클릭
5. Request body에 access_token 입력:
   ```json
   {
     "access_token": "실제_카카오_access_token"
   }
   ```
6. "Execute" 클릭

### 2. curl로 테스트

```bash
curl -X POST "http://localhost:8000/api/v1/auth/kakao/login" \
  -H "Content-Type: application/json" \
  -d '{
    "access_token": "실제_카카오_access_token"
  }'
```

### 3. 카카오 access_token 얻는 방법

#### 방법 1: 카카오 개발자 도구 사용
1. [카카오 개발자 콘솔](https://developers.kakao.com/) 접속
2. 내 애플리케이션 > 앱 설정 > 플랫폼 설정
3. REST API 키 확인
4. 도구 > API 테스트 도구에서 토큰 발급

#### 방법 2: 프론트엔드에서 테스트
- 카카오 SDK로 로그인 후 콘솔에서 `access_token` 확인

## ⚙️ 카카오 개발자 설정

1. [카카오 개발자 콘솔](https://developers.kakao.com/) 접속
2. 내 애플리케이션 생성
3. 플랫폼 설정:
   - Web 플랫폼 추가 (도메인 등록)
   - Redirect URI 설정 (예: `http://localhost:3000/auth/kakao/callback`)
4. 제품 설정 > 카카오 로그인 활성화
5. 동의항목 설정:
   - 필수: 닉네임, 프로필 사진
   - 선택: 이메일 (필요시)
6. REST API 키 확인

## 📝 주의사항

1. **이메일 동의**: 카카오에서 이메일을 제공하지 않는 경우, 임시 이메일(`kakao_{id}@kakao.temp`)이 생성됩니다.
2. **access_token 유효기간**: 카카오 access_token은 일정 시간 후 만료됩니다.
3. **보안**: 프로덕션 환경에서는 HTTPS를 사용해야 합니다.
4. **CORS**: 프론트엔드 도메인을 CORS 설정에 추가해야 할 수 있습니다.

## 🔐 향후 개선 사항

- [ ] JWT 토큰 발급 추가
- [ ] Refresh Token 처리
- [ ] 로그아웃 기능
- [ ] 토큰 갱신 기능

