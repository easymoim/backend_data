# EasyMoim API 문서

프론트엔드 개발자를 위한 EasyMoim 백엔드 API 사용 가이드입니다.

## 기본 정보

- **Base URL**: `http://localhost:8000/api/v1`
- **API 문서 (Swagger)**: `http://localhost:8000/docs`
- **API 문서 (ReDoc)**: `http://localhost:8000/redoc`

모든 API는 JSON 형식으로 요청/응답합니다.

---

## 인증 (Auth)

### 카카오 로그인

**POST** `/auth/kakao/login`

카카오 OAuth 로그인을 처리합니다. 프론트엔드에서 카카오 SDK로 받은 access_token을 전달합니다.

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
    "created_at": "2025-01-01T00:00:00",
    "updated_at": "2025-01-01T00:00:00"
  },
  "access_token": "",  // JWT 토큰 (향후 구현 예정)
  "is_new_user": false  // 신규 사용자 여부
}
```

**에러 응답:**
- `401 Unauthorized`: 유효하지 않은 access_token

---

## 사용자 (Users)

### 사용자 생성

**POST** `/users`

새로운 사용자를 생성합니다. (일반적으로 OAuth 로그인을 통해 자동 생성되므로 직접 호출할 필요는 없습니다)

**Request Body:**
```json
{
  "name": "홍길동",
  "email": "user@example.com",
  "oauth_provider": "kakao",
  "oauth_id": "123456789"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "홍길동",
  "email": "user@example.com",
  "oauth_provider": "kakao",
  "oauth_id": "123456789",
  "is_active": true,
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:00:00"
}
```

### 사용자 조회

**GET** `/users/{user_id}`

특정 사용자 정보를 조회합니다.

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "홍길동",
  "email": "user@example.com",
  "oauth_provider": "kakao",
  "oauth_id": "123456789",
  "is_active": true,
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:00:00"
}
```

### 사용자 정보 업데이트

**PUT** `/users/{user_id}`

사용자 정보를 업데이트합니다.

**Request Body:**
```json
{
  "name": "홍길동 (수정)"
}
```

---

## 모임 (Meetings)

### 모임 생성

**POST** `/meetings?creator_id={user_id}`

새로운 모임을 생성합니다.

**Query Parameters:**
- `creator_id` (required): 주최자 사용자 ID

**Request Body:**
```json
{
  "name": "이지모임",
  "purpose": ["dining", "drink"],
  "is_one_place": true,
  "location_choice_type": "preference_area",
  "location_choice_value": "강남구, 강동구, 마포구",
  "preference_place": {
    "mood": ["대화 나누기 좋은"],
    "food": ["한식", "양식"],
    "condition": ["주차"]
  },
  "deadline": "2025-11-27T23:59:00",
  "expected_participant_count": 5
  // share_code는 선택사항이며, 없으면 null로 저장됩니다
}
```

**참고:** `share_code`는 선택사항입니다. 요청에 포함하지 않으면 `null`로 저장됩니다.

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "이지모임",
  "creator_id": 1,
  "purpose": ["dining", "drink"],
  "is_one_place": true,
  "location_choice_type": "preference_area",
  "location_choice_value": "강남구, 강동구, 마포구",
  "preference_place": {
    "mood": ["대화 나누기 좋은"],
    "food": ["한식", "양식"],
    "condition": ["주차"]
  },
  "deadline": "2025-11-27T23:59:00",
  "expected_participant_count": 5,
  "share_code": "ABC123",
  "confirmed_time": null,
  "confirmed_location": null,
  "confirmed_at": null,
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:00:00"
}
```

### 모임 목록 조회

**GET** `/meetings?skip=0&limit=100`

모든 모임 목록을 조회합니다.

**Query Parameters:**
- `skip` (optional, default: 0): 건너뛸 개수
- `limit` (optional, default: 100): 가져올 개수

**Response (200 OK):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "이지모임",
    "creator_id": 1,
    ...
  }
]
```

### 생성자별 모임 목록 조회

**GET** `/meetings/creator/{creator_id}?skip=0&limit=100`

특정 사용자가 생성한 모임 목록을 조회합니다.

### 공유 코드로 모임 조회

**GET** `/meetings/share-code/{share_code}`

공유 코드를 사용하여 모임을 조회합니다. (비로그인 사용자가 모임에 참가할 때 사용)

**예시:**
```
GET /meetings/share-code/ABC123
```

### 모임 조회

**GET** `/meetings/{meeting_id}`

특정 모임의 상세 정보를 조회합니다.

### 모임 정보 업데이트

**PUT** `/meetings/{meeting_id}`

모임 정보를 업데이트합니다. (확정 시간, 확정 장소 등)

**Request Body:**
```json
{
  "confirmed_time": "2025-11-27T18:00:00",
  "confirmed_location": "강남역 맛집",
  "confirmed_at": "2025-11-20T12:00:00"
}
```

### 모임 삭제

**DELETE** `/meetings/{meeting_id}`

모임을 삭제합니다. (관련된 모든 데이터도 함께 삭제됩니다)

---

## 참가자 (Participants)

### 참가자 추가

**POST** `/participants`

모임에 참가자를 추가합니다. (로그인/비로그인 모두 가능)

**Request Body:**
```json
{
  "meeting_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 1,  // 로그인 사용자인 경우 (nullable)
  "nickname": "홍길동",
  "oauth_key": "kakao_123456789",  // 비로그인 사용자인 경우
  "is_invited": true,
  "preference_place": {
    "mood": ["조용한"],
    "food": ["한식"],
    "condition": ["주차 가능"]
  },
  "location": "서울시 강남구"
}
```

**Response (201 Created):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "meeting_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 1,
  "nickname": "홍길동",
  "oauth_key": null,
  "is_invited": true,
  "has_responded": false,
  "preference_place": {
    "mood": ["조용한"],
    "food": ["한식"],
    "condition": ["주차 가능"]
  },
  "location": "서울시 강남구",
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:00:00"
}
```

### 모임별 참가자 목록 조회

**GET** `/participants/meeting/{meeting_id}`

특정 모임의 참가자 목록을 조회합니다.

**Response (200 OK):**
```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440000",
    "meeting_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": 1,
    "nickname": "홍길동",
    ...
  }
]
```

### 사용자별 참가한 모임 목록 조회

**GET** `/participants/user/{user_id}`

특정 사용자가 참가한 모든 모임 목록을 조회합니다.

### 참가자 조회

**GET** `/participants/{participant_id}`

특정 참가자 정보를 조회합니다.

### 참가자 정보 업데이트

**PUT** `/participants/{participant_id}`

참가자 정보를 업데이트합니다. (응답 여부, 선호도 등)

**Request Body:**
```json
{
  "has_responded": true,
  "preference_place": {
    "mood": ["조용한", "대화 나누기 좋은"],
    "food": ["한식", "양식"]
  }
}
```

### 참가자 삭제

**DELETE** `/participants/{participant_id}`

참가자를 모임에서 제거합니다.

---

## 시간 후보 (Time Candidates)

### 시간 후보 생성

**POST** `/time-candidates`

모임의 시간 후보를 생성합니다. `candidate_time`은 여러 시간과 각 시간의 투표 수를 JSON으로 저장합니다.

**Request Body:**
```json
{
  "meeting_id": "550e8400-e29b-41d4-a716-446655440000",
  "candidate_time": {
    "25.11.11.09:00": 0,
    "25.11.11.14:00": 0,
    "25.11.12.18:00": 0
  }
}
```

**Response (201 Created):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "meeting_id": "550e8400-e29b-41d4-a716-446655440000",
  "candidate_time": {
    "25.11.11.09:00": 0,
    "25.11.11.14:00": 0,
    "25.11.12.18:00": 0
  },
  "created_at": "2025-01-01T00:00:00"
}
```

### 모임별 시간 후보 목록 조회

**GET** `/time-candidates/meeting/{meeting_id}`

특정 모임의 시간 후보 목록을 조회합니다.

### 시간 후보 조회

**GET** `/time-candidates/{candidate_id}`

특정 시간 후보를 조회합니다.

### 시간 후보 삭제

**DELETE** `/time-candidates/{candidate_id}`

시간 후보를 삭제합니다.

---

## 시간 투표 (Time Votes)

### 시간 투표 생성/업데이트

**POST** `/time-votes`

참가자가 특정 시간 후보에 대해 투표합니다. 이미 투표한 경우 자동으로 업데이트됩니다.

**Request Body:**
```json
{
  "participant_id": "660e8400-e29b-41d4-a716-446655440000",
  "meeting_id": "550e8400-e29b-41d4-a716-446655440000",
  "time_candidate_id": "770e8400-e29b-41d4-a716-446655440000",
  "is_available": true,
  "memo": "늦을 수도 있어요"
}
```

**Response (201 Created):**
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440000",
  "participant_id": "660e8400-e29b-41d4-a716-446655440000",
  "meeting_id": "550e8400-e29b-41d4-a716-446655440000",
  "time_candidate_id": "770e8400-e29b-41d4-a716-446655440000",
  "is_available": true,
  "memo": "늦을 수도 있어요",
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:00:00"
}
```

**참고:** 투표가 생성/업데이트되면 `meeting_time_candidate` 테이블의 `candidate_time` JSON이 자동으로 업데이트되어야 합니다. (현재는 수동 업데이트 필요)

### 참가자별 시간 투표 목록 조회

**GET** `/time-votes/participant/{participant_id}`

특정 참가자가 투표한 모든 시간 투표 목록을 조회합니다.

### 시간 후보별 투표 목록 조회

**GET** `/time-votes/candidate/{candidate_id}`

특정 시간 후보에 투표한 모든 투표 목록을 조회합니다.

### 시간 투표 조회

**GET** `/time-votes/{vote_id}`

특정 시간 투표를 조회합니다.

### 시간 투표 업데이트

**PUT** `/time-votes/{vote_id}`

시간 투표 정보를 업데이트합니다.

**Request Body:**
```json
{
  "is_available": false,
  "memo": "불가능합니다"
}
```

### 시간 투표 삭제

**DELETE** `/time-votes/{vote_id}`

시간 투표를 삭제합니다.

---

## 장소 (Places)

### 장소 생성

**POST** `/places`

새로운 장소를 생성합니다. (LLM이 추천한 장소 중 주최자가 선택한 장소)

**Request Body:**
```json
{
  "id": "kakao_place_123456",  // 외부 API의 Place ID
  "name": "맛있는 식당",
  "category": "한식",
  "address": "서울시 강남구 테헤란로 123",
  "location": "37.5665, 126.9780",
  "rating": 4.5,
  "thumbnail": "https://example.com/image.jpg"
}
```

**Response (201 Created):**
```json
{
  "id": "kakao_place_123456",
  "name": "맛있는 식당",
  "category": "한식",
  "address": "서울시 강남구 테헤란로 123",
  "location": "37.5665, 126.9780",
  "rating": 4.5,
  "thumbnail": "https://example.com/image.jpg",
  "updated_at": "2025-01-01T00:00:00"
}
```

### 장소 목록 조회

**GET** `/places?skip=0&limit=100`

모든 장소 목록을 조회합니다.

### 장소 조회

**GET** `/places/{place_id}`

특정 장소 정보를 조회합니다.

### 장소 정보 업데이트

**PUT** `/places/{place_id}`

장소 정보를 업데이트합니다.

### 장소 삭제

**DELETE** `/places/{place_id}`

장소를 삭제합니다.

---

## 장소 후보 (Place Candidates)

### 장소 후보 생성

**POST** `/place-candidates`

LLM이 추천한 장소 후보를 생성합니다.

**Request Body:**
```json
{
  "id": "kakao_place_123456",  // 외부 API의 Place ID
  "meeting_id": "550e8400-e29b-41d4-a716-446655440000",
  "location": "강남구",
  "preference_subway": ["강남역", "역삼역"],
  "preference_area": ["강남구", "서초구"],
  "food": "한식",
  "condition": "주차 가능",
  "location_type": "preference_area"
}
```

**Response (201 Created):**
```json
{
  "id": "kakao_place_123456",
  "meeting_id": "550e8400-e29b-41d4-a716-446655440000",
  "location": "강남구",
  "preference_subway": ["강남역", "역삼역"],
  "preference_area": ["강남구", "서초구"],
  "food": "한식",
  "condition": "주차 가능",
  "location_type": "preference_area"
}
```

### 모임별 장소 후보 목록 조회

**GET** `/place-candidates/meeting/{meeting_id}`

특정 모임의 장소 후보 목록을 조회합니다.

### 장소 후보 조회

**GET** `/place-candidates/{candidate_id}`

특정 장소 후보를 조회합니다.

### 장소 후보 정보 업데이트

**PUT** `/place-candidates/{candidate_id}`

장소 후보 정보를 업데이트합니다.

### 장소 후보 삭제

**DELETE** `/place-candidates/{candidate_id}`

장소 후보를 삭제합니다.

---

## 장소 투표 (Place Votes)

### 장소 투표 생성/업데이트

**POST** `/place-votes`

참가자가 특정 장소 후보에 대해 투표합니다. 이미 투표한 경우 자동으로 업데이트됩니다.

**Request Body:**
```json
{
  "participant_id": "660e8400-e29b-41d4-a716-446655440000",
  "meeting_id": "550e8400-e29b-41d4-a716-446655440000",
  "time_candidate_id": "770e8400-e29b-41d4-a716-446655440000",
  "is_available": true,
  "memo": "이 장소 좋아요!"
}
```

**Response (201 Created):**
```json
{
  "id": "990e8400-e29b-41d4-a716-446655440000",
  "participant_id": "660e8400-e29b-41d4-a716-446655440000",
  "meeting_id": "550e8400-e29b-41d4-a716-446655440000",
  "time_candidate_id": "770e8400-e29b-41d4-a716-446655440000",
  "is_available": true,
  "memo": "이 장소 좋아요!",
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:00:00"
}
```

**참고:** `time_candidate_id`는 특정 시간대와 연관된 장소 투표인 경우 사용합니다.

### 참가자별 장소 투표 목록 조회

**GET** `/place-votes/participant/{participant_id}`

특정 참가자가 투표한 모든 장소 투표 목록을 조회합니다.

### 모임별 장소 투표 목록 조회

**GET** `/place-votes/meeting/{meeting_id}`

특정 모임의 모든 장소 투표 목록을 조회합니다.

### 장소 투표 조회

**GET** `/place-votes/{vote_id}`

특정 장소 투표를 조회합니다.

### 장소 투표 업데이트

**PUT** `/place-votes/{vote_id}`

장소 투표 정보를 업데이트합니다.

### 장소 투표 삭제

**DELETE** `/place-votes/{vote_id}`

장소 투표를 삭제합니다.

---

## 에러 응답

모든 API는 다음과 같은 에러 응답 형식을 사용합니다:

**404 Not Found:**
```json
{
  "detail": "모임을 찾을 수 없습니다."
}
```

**400 Bad Request:**
```json
{
  "detail": "이미 존재하는 이메일입니다."
}
```

**401 Unauthorized:**
```json
{
  "detail": "유효하지 않은 Kakao access_token입니다."
}
```

---

## 일반적인 사용 흐름

### 1. 모임 생성 및 참가

1. 사용자 로그인: `POST /auth/kakao/login`
2. 모임 생성: `POST /meetings?creator_id={user_id}`
3. 참가자 추가: `POST /participants` (공유 코드로 모임 조회 후)

### 2. 시간 투표

1. 시간 후보 생성: `POST /time-candidates`
2. 참가자들이 시간 투표: `POST /time-votes`
3. 시간 후보별 투표 조회: `GET /time-votes/candidate/{candidate_id}`

### 3. 장소 투표

1. 장소 후보 생성: `POST /place-candidates` (LLM 추천 후)
2. 참가자들이 장소 투표: `POST /place-votes`
3. 모임별 장소 투표 조회: `GET /place-votes/meeting/{meeting_id}`

### 4. 모임 확정

1. 모임 정보 업데이트: `PUT /meetings/{meeting_id}`
   - `confirmed_time`, `confirmed_location`, `confirmed_at` 설정

---

## 주의사항

1. **UUID 형식**: `meeting_id`, `participant_id`, `candidate_id` 등은 UUID 형식입니다.
2. **공유 코드**: 비로그인 사용자도 공유 코드로 모임에 참가할 수 있습니다.
3. **투표 중복 방지**: `time_vote`와 `place_vote`는 `participant_id`와 `candidate_id` 조합이 유일해야 합니다.
4. **자동 업데이트**: 투표 생성/업데이트 시 `meeting_time_candidate`의 `candidate_time` JSON이 자동으로 업데이트되어야 합니다. (현재는 수동 업데이트 필요)

---

## 추가 리소스

- **Swagger UI**: `http://localhost:8000/docs` - 인터랙티브 API 문서
- **ReDoc**: `http://localhost:8000/redoc` - 읽기 쉬운 API 문서
- **ERD**: `ERD.md` - 데이터베이스 스키마 문서

