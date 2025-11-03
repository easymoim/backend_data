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

### 1. uv로 프로젝트 초기화 및 패키지 설치

```bash
# 프로젝트 동기화 (가상 환경 생성 + 패키지 설치)
uv sync
```

> **참고**: `uv.lock` 파일은 git에 포함되어야 합니다. 이 파일은 모든 의존성의 정확한 버전을 고정하여 팀원 간 동일한 개발 환경을 보장합니다.

### 2. 서버 실행

```bash
# 방법 1: uv로 직접 실행 (권장)
uv run python main.py

# 방법 2: uv로 uvicorn 실행
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 방법 3: 가상 환경 활성화 후 실행
source .venv/bin/activate  # macOS/Linux
python main.py
```

### 3. 기타 uv 명령어

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
└── README.md           # 프로젝트 설명서
```

## API 엔드포인트

- `GET /` - 루트 엔드포인트
- `GET /health` - 헬스 체크 엔드포인트
