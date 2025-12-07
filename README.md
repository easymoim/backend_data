# EasyMoim Backend API

FastAPI 기반 백엔드 API 서버

## 개발 환경 설정

### uv 설치

uv는 빠른 Python 패키지 관리자입니다. 설치하지 않은 경우:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 또는 Homebrew
brew install uv
```

### 1. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 Supabase 데이터베이스 비밀번호를 설정하세요:

```bash
# .env 파일 생성
DATABASE_PASSWORD=your_supabase_password_here
```

또는 전체 DATABASE_URL을 직접 설정할 수도 있습니다:

```bash
DATABASE_URL=postgresql://postgres:your_password@db.wxuunspyyvqndpodtesy.supabase.co:5432/postgres
```

> **참고**: `.env` 파일은 `.gitignore`에 포함되어 있어 Git에 커밋되지 않습니다.

### 2. uv로 프로젝트 초기화 및 패키지 설치

```bash
# 프로젝트 동기화 (가상 환경 생성 + 패키지 설치)
uv sync
```

> **참고**: `uv.lock` 파일은 git에 포함되어야 합니다. 이 파일은 모든 의존성의 정확한 버전을 고정하여 팀원 간 동일한 개발 환경을 보장합니다.

### 3. 서버 실행

```bash
# 방법 1: uv로 직접 실행 (권장)
uv run python main.py

# 방법 2: uv로 uvicorn 실행
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 방법 3: 가상 환경 활성화 후 실행
source .venv/bin/activate  # macOS/Linux
python main.py
```

### 4. 기타 uv 명령어

```bash
# 패키지 추가
uv add <package-name>

# 개발 의존성 추가
uv add --dev <package-name>

# 패키지 업데이트
uv sync --upgrade

# 가상 환경에 직접 접근 (uv는 .venv 폴더 사용)
source .venv/bin/activate
```

서버가 실행되면 다음 주소에서 접근할 수 있습니다:
- API: http://localhost:8000
- API 문서 (Swagger UI): http://localhost:8000/docs
- API 문서 (ReDoc): http://localhost:8000/redoc

## 프로젝트 구조

```
backend_data/
├── main.py              # FastAPI 메인 애플리케이션
├── pyproject.toml       # 프로젝트 설정 및 의존성 (uv 사용)
├── uv.lock              # 의존성 버전 고정 파일 (git에 포함)
├── requirements.txt     # Python 패키지 의존성 (호환성 유지)
├── .python-version      # Python 버전 지정
├── .gitignore          # Git 제외 파일 목록
├── README.md           # 프로젝트 설명서
├── docs/               # 문서 폴더
│   ├── API_DOCS.md    # API 사용 가이드
│   ├── ERD.md         # 데이터베이스 ERD
│   ├── PRD.md         # 제품 요구사항 문서
│   └── ...            # 기타 문서들
└── app/               # 애플리케이션 코드
    ├── api/           # API 라우터
    ├── crud/          # CRUD 함수
    ├── models/        # 데이터베이스 모델
    └── schemas/       # Pydantic 스키마
```

## API 문서

프론트엔드 개발자를 위한 상세한 API 문서가 준비되어 있습니다.

📖 **[API_DOCS.md](./docs/API_DOCS.md)** - 전체 API 사용 가이드 (요청/응답 예시 포함)

### 빠른 참조

#### 기본 엔드포인트
- `GET /` - 루트 엔드포인트
- `GET /health` - 헬스 체크 엔드포인트

#### 인증
- `POST /api/v1/auth/kakao/login` - 카카오 로그인

#### 사용자
- `POST /api/v1/users` - 사용자 생성
- `GET /api/v1/users/{user_id}` - 사용자 조회
- `PUT /api/v1/users/{user_id}` - 사용자 정보 업데이트

#### 모임 (Meeting)
- `POST /api/v1/meetings?creator_id={user_id}` - 모임 생성
- `GET /api/v1/meetings` - 모임 목록 조회
- `GET /api/v1/meetings/share-code/{share_code}` - 공유 코드로 모임 조회
- `GET /api/v1/meetings/{meeting_id}` - 모임 조회
- `PUT /api/v1/meetings/{meeting_id}` - 모임 정보 업데이트
- `DELETE /api/v1/meetings/{meeting_id}` - 모임 삭제

#### 참가자 (Participant)
- `POST /api/v1/participants` - 참가자 추가
- `GET /api/v1/participants/meeting/{meeting_id}` - 모임별 참가자 목록
- `GET /api/v1/participants/user/{user_id}` - 사용자별 참가한 모임 목록
- `GET /api/v1/participants/{participant_id}` - 참가자 조회
- `PUT /api/v1/participants/{participant_id}` - 참가자 정보 업데이트
- `DELETE /api/v1/participants/{participant_id}` - 참가자 삭제

#### 시간 후보 (Time Candidate)
- `POST /api/v1/time-candidates` - 시간 후보 추가
- `GET /api/v1/time-candidates/meeting/{meeting_id}` - 모임별 시간 후보 목록
- `GET /api/v1/time-candidates/{candidate_id}` - 시간 후보 조회
- `DELETE /api/v1/time-candidates/{candidate_id}` - 시간 후보 삭제

#### 시간 투표 (Time Vote)
- `POST /api/v1/time-votes` - 시간 투표 (생성/업데이트)
- `GET /api/v1/time-votes/participant/{participant_id}` - 참가자별 투표 목록
- `GET /api/v1/time-votes/candidate/{candidate_id}` - 시간 후보별 투표 목록
- `GET /api/v1/time-votes/{vote_id}` - 투표 조회
- `PUT /api/v1/time-votes/{vote_id}` - 투표 업데이트
- `DELETE /api/v1/time-votes/{vote_id}` - 투표 삭제

#### 장소 (Place)
- `POST /api/v1/places` - 장소 생성
- `GET /api/v1/places` - 장소 목록 조회
- `GET /api/v1/places/{place_id}` - 장소 조회
- `PUT /api/v1/places/{place_id}` - 장소 정보 업데이트
- `DELETE /api/v1/places/{place_id}` - 장소 삭제

#### 장소 후보 (Place Candidate)
- `POST /api/v1/place-candidates` - 장소 후보 추가
- `GET /api/v1/place-candidates/meeting/{meeting_id}` - 모임별 장소 후보 목록
- `GET /api/v1/place-candidates/{candidate_id}` - 장소 후보 조회
- `PUT /api/v1/place-candidates/{candidate_id}` - 장소 후보 정보 업데이트
- `DELETE /api/v1/place-candidates/{candidate_id}` - 장소 후보 삭제

#### 장소 투표 (Place Vote)
- `POST /api/v1/place-votes` - 장소 투표 (생성/업데이트)
- `GET /api/v1/place-votes/participant/{participant_id}` - 참가자별 투표 목록
- `GET /api/v1/place-votes/meeting/{meeting_id}` - 모임별 투표 목록
- `GET /api/v1/place-votes/{vote_id}` - 투표 조회
- `PUT /api/v1/place-votes/{vote_id}` - 투표 업데이트
- `DELETE /api/v1/place-votes/{vote_id}` - 투표 삭제

## 카카오 로그인

카카오 OAuth 로그인 기능이 구현되어 있습니다.

- **사용 가이드**: [KAKAO_LOGIN_GUIDE.md](./docs/KAKAO_LOGIN_GUIDE.md)
- **테스트 가이드**: [TEST_KAKAO_LOGIN.md](./docs/TEST_KAKAO_LOGIN.md)

## 문서

프로젝트 관련 문서들은 `docs/` 폴더에 정리되어 있습니다:

- **[API_DOCS.md](./docs/API_DOCS.md)** - API 사용 가이드
- **[ERD.md](./docs/ERD.md)** - 데이터베이스 ERD
- **[PRD.md](./docs/PRD.md)** - 제품 요구사항 문서
- **[KAKAO_LOGIN_GUIDE.md](./docs/KAKAO_LOGIN_GUIDE.md)** - 카카오 로그인 가이드
- **[TEST_KAKAO_LOGIN.md](./docs/TEST_KAKAO_LOGIN.md)** - 카카오 로그인 테스트 가이드
- **[ProjectTODO.md](./docs/ProjectTODO.md)** - 프로젝트 TODO

### 빠른 테스트

1. 서버 실행: `uv run python main.py`
2. Swagger UI 접속: `http://localhost:8000/docs`
3. `/api/v1/auth/kakao/login` 엔드포인트에서 테스트
4. 카카오 access_token은 [카카오 개발자 콘솔](https://developers.kakao.com/) > 도구 > API 테스트 도구에서 발급

또는 테스트 스크립트 사용:
```bash
uv run python test_kakao_login.py YOUR_ACCESS_TOKEN
```

## API 테스트

API를 테스트하는 다양한 방법이 준비되어 있습니다.

📖 **[API_TEST_GUIDE.md](./docs/API_TEST_GUIDE.md)** - API 테스트 가이드

### 빠른 시작

1. **서버 실행**
   ```bash
   .venv/bin/python main.py
   # 또는
   uv run python main.py
   ```

2. **Swagger UI 접속** (가장 쉬운 방법)
   - 브라우저에서 http://localhost:8000/docs 접속
   - 각 API를 클릭하여 직접 테스트 가능

3. **curl로 테스트**
   ```bash
   # 헬스 체크
   curl http://localhost:8000/health
   
   # 모임 목록 조회
   curl http://localhost:8000/api/v1/meetings
   ```
