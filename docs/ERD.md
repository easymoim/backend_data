## user

**테이블 설명:**
- 사용자(회원) 정보를 저장하는 테이블입니다.
- OAuth(Google, Kakao)를 통한 소셜 로그인을 지원합니다.
- `oauth_provider`와 `oauth_id`의 조합으로 고유하게 식별됩니다.
- `is_active` 플래그로 계정 활성화 상태를 관리합니다.

| Column | Type | Note |
| --- | --- | --- |
| id | PK | 숫자 |
| name | varchar |  |
| email | varchar(unique) |  |
| oauth_provider |  |  |
| oauth_id |  |  |
| is_active |  |  |
| created_at | timestamp |  |
| updated_at | timestamp |  |

**SQL:**
```sql
CREATE TABLE user (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    oauth_provider oauth_provider_enum NOT NULL,
    oauth_id VARCHAR(255) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## meeting

**테이블 설명:**
- 모임의 전체 정보를 저장하는 핵심 테이블입니다.
- 주최자(creator_id)가 모임을 생성하고, 참가자들이 시간과 장소에 투표합니다.
- `purpose`: 모임 목적을 배열로 저장 (예: ['dining', 'drink'])
- `location_choice_type`: 위치 선택 방식 (중심 위치, 선호 지역, 선호 지하철역)
- `preference_place`: 모임의 선호 장소 조건 (분위기, 음식 종류, 조건 등)
- `share_code`: 모임 초대를 위한 고유 공유 코드
- `confirmed_time`, `confirmed_location`, `confirmed_at`: 주최자가 최종 확정한 시간과 장소 정보

| Column | Type | Note | example |
| --- | --- | --- | --- |
| id | PK | UUID |  |
| name | varchar |  | 이지모임 |
| creator_id | FK(User.id) | Host |  |
| purpose | string[] |  | ['dining', 'drink'] |
| is_one_place | boolean | 한 곳에서 해결 여부 |  |
| location_choice_type | enum | center_location, preference_area, preference_subway |  |
| location_choice_value | varchar | {"강남구" ,"강동구", "마포구"} || {"강남역", "설대입구역", "구디역"} || {직접입력한값} |  |
| preference_place | jsonb | {"mood" : ["대화 나누기 좋은"], "food" : ["한식", "양식"], "condition": ["주차"]} |  |
| deadline | timestamp | 2025-11-27 23:59 |  |
| expected_participant_count | int | 예상 참가 인원 |  |
| share_code | varchar | 공유 코드 |  |
| status | varchar | 모임 상태 (time_voting, place_voting, confirmed) | time_voting |
| available_times | timestamp[] | 주최자가 선택한 가능한 시간 목록 | ["2025-11-10 09:00", "2025-11-10 10:00", "2025-11-11 08:00"] |
| confirmed_time | timestamp | 확정된 모임 시간 |  |
| confirmed_location | varchar | 확정된 장소 |  |
| confirmed_at | timestamp | 주최자가 "확정하기!" 누른 시간 |  |
| created_at | timestamp |  |  |
| updated_at | timestamp |  |  |
| deleted_at | timestamp | 소프트 삭제 시간 (null이면 삭제되지 않음) |  |

**SQL:**
```sql
CREATE TABLE meeting (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    creator_id INTEGER NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    purpose TEXT[] NOT NULL,
    is_one_place BOOLEAN,
    location_choice_type location_choice_type_enum,
    location_choice_value VARCHAR(255),
    preference_place JSONB,
    deadline TIMESTAMP,
    expected_participant_count INTEGER,
    share_code VARCHAR(255) UNIQUE,
    status VARCHAR(50),
    available_times TIMESTAMP[],
    confirmed_time TIMESTAMP,
    confirmed_location VARCHAR(255),
    confirmed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);
```

## participant

**테이블 설명:**
- 모임에 참가하는 참가자 정보를 저장하는 테이블입니다.
- 로그인한 사용자(`user_id`)와 비로그인 사용자 모두 참가할 수 있습니다.
- 비로그인 사용자의 경우 `oauth_key`(카카오 고유 ID)로 식별합니다.
- `is_invited`: 초대받은 참가자인지 여부
- `has_responded`: 시간/장소 투표에 응답했는지 여부
- `preference_place`: 개별 참가자의 장소 선호도 (모임의 preference_place와 별도)
- `location`: 참가자의 위치 정보

| Column | Type | Note |
| --- | --- | --- |
| id | PK | UUID |
| meeting_id | FK(Meeting.id) |  |
| user_id | FK(User.id), nullable | 비로그인 사용자도 가능 |
| nickname | varchar | 닉네임 |
| oauth_key | varchar | 카카오 고유 id |
| is_invited | boolean |  |
| has_responded | boolean | 응답 여부 |
| preference_place | jsonb | {"mood" : ["대화 나누기 좋은"], "food" : ["한식", "양식"], "condition": ["주차"]} |
| location | varchar |  |
| created_at | timestamp |  |
| updated_at | timestamp |  |

**SQL:**
```sql
CREATE TABLE participant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID NOT NULL REFERENCES meeting(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES user(id) ON DELETE SET NULL,
    nickname VARCHAR(255),
    oauth_key VARCHAR(255),
    is_invited BOOLEAN DEFAULT FALSE,
    has_responded BOOLEAN DEFAULT FALSE,
    preference_place JSONB,
    location VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## meeting_time_candidate

**테이블 설명:**
- 모임의 시간 후보와 각 시간에 대한 투표 수를 저장하는 테이블입니다.
- `candidate_time`: 각 시간별 투표 수를 JSONB 형식으로 저장합니다.
- 예: `{"2025-11-01 02:00": 3, "2025-11-01 03:00": 2, "2025-11-01 09:00": 5}`
- 참가자들이 `time_vote` 테이블을 통해 투표하면, 이 테이블의 `candidate_time` JSON이 업데이트됩니다.
- 한 모임당 하나의 레코드만 존재하며, 모든 시간 후보와 투표 수를 관리합니다.

| Column | Type | Note | example |
| --- | --- | --- | --- |
| id | PK | UUID |  |
| meeting_id | FK(Meeting.id) |  |  |
| candidate_time | jsonb | 각 시간별 투표 수 | {"2025-11-01 02:00": 3, "2025-11-01 03:00": 2, "2025-11-01 09:00": 5} |
| created_at | timestamp |  |  |

**SQL:**
```sql
CREATE TABLE meeting_time_candidate (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID NOT NULL REFERENCES meeting(id) ON DELETE CASCADE,
    candidate_time JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## time_vote (누가 몇시에 투표했는지)

**테이블 설명:**
- 참가자가 여러 시간에 대해 한 번에 투표한 정보를 저장하는 테이블입니다.
- `time_list`: 투표한 시간 목록 배열 (예: ["2025-11-01 02:00", "2025-11-01 03:00", "2025-11-01 09:00"])
- `is_available`: 이 시간들에 대해 가능한지 여부 (true: 가능, false: 불가능)
- `memo`: 시간에 대한 추가 메모나 특이사항
- `participant_id`와 `time_candidate_id`의 조합은 유일해야 합니다 (한 참가자가 같은 시간 후보에 대해 하나의 투표만 가능).
- 이 테이블의 투표 정보가 `meeting_time_candidate` 테이블의 `candidate_time` JSON에 집계됩니다.

| Column | Type | Note |
| --- | --- | --- |
| id | PK | UUID |
| participant_id | FK(Participant.id) |  |
| meeting_id | FK(Meeting.id) |  |
| time_candidate_id | FK(MeetingTimeCandidate.id) |  |
| time_list | text[] | 투표한 시간 목록 (예: ["2025-11-01 02:00", "2025-11-01 03:00"]) |
| is_available | boolean | 가능 여부 |
| memo | text | 메모 |
| created_at | timestamp |  |
| updated_at | timestamp |  |

**SQL:**
```sql
CREATE TABLE time_vote (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    participant_id UUID NOT NULL REFERENCES participant(id) ON DELETE CASCADE,
    meeting_id UUID NOT NULL REFERENCES meeting(id) ON DELETE CASCADE,
    time_candidate_id UUID NOT NULL REFERENCES meeting_time_candidate(id) ON DELETE CASCADE,
    time_list TEXT[] NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    memo TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_participant_time_candidate UNIQUE (participant_id, time_candidate_id)
);
```

## place_vote (누가 어떤 장소에 투표했는지)

**테이블 설명:**
- 참가자가 특정 장소 후보(`place_candidate`)에 대해 투표한 정보를 저장하는 테이블입니다.
- 각 참가자는 여러 장소 후보에 대해 투표할 수 있습니다 (가능/불가능).
- `is_available`: 해당 장소에 가능한지 여부 (true: 가능, false: 불가능)
- `memo`: 장소에 대한 추가 메모나 특이사항
- `time_candidate_id`: 특정 시간대와 연관된 장소 투표인 경우 해당 시간 후보를 참조합니다.
- 참가자들의 장소 선호도를 집계하여 최종 장소를 결정하는 데 사용됩니다.

| Column | Type | Note |
| --- | --- | --- |
| id | PK | UUID |
| participant_id | FK(Participant.id) |  |
| meeting_id | FK(Meeting.id) |  |
| time_candidate_id | FK(MeetingTimeCandidate.id) |  |
| is_available | boolean | 가능 여부 |
| memo | text | 메모 |
| created_at | timestamp |  |
| updated_at | timestamp |  |

**SQL:**
```sql
CREATE TABLE place_vote (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    participant_id UUID NOT NULL REFERENCES participant(id) ON DELETE CASCADE,
    meeting_id UUID NOT NULL REFERENCES meeting(id) ON DELETE CASCADE,
    time_candidate_id UUID NOT NULL REFERENCES meeting_time_candidate(id) ON DELETE CASCADE,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    memo TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## place

**테이블 설명:**
- LLM이 추천한 장소 중에서 주최자가 최종적으로 선택한 장소 정보를 저장하는 테이블입니다.
- `place_candidate` 테이블의 후보들 중에서 선택된 장소가 이 테이블에 저장됩니다.
- `id`는 외부 API(예: 카카오맵, 네이버 플레이스)의 Place ID를 사용합니다.
- `category`: 장소 카테고리 (예: "식당", "카페", "술집")
- `location`: 위도, 경도 등 위치 정보
- `rating`: 장소 평점 (nullable)
- `thumbnail`: 장소 썸네일 이미지 URL (nullable)
- 한 번 저장된 장소는 여러 모임에서 재사용될 수 있습니다 (같은 Place ID로).

| Column | Type | Note |
| --- | --- | --- |
| id | PK | varchar(API Place ID 사용) |
| name | varchar |  |
| category | varchar |  |
| address | text |  |
| location | varchar | 위도, 경도 등 |
| rating | float | nullable |
| thumbnail | text | nullable |
| updated_at | timestamp |  |

**SQL:**
```sql
CREATE TABLE place (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(255),
    address TEXT,
    location VARCHAR(255),
    rating FLOAT,
    thumbnail TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

```
User (1) ───< Participant >─── (N) Meeting
                        │
                        │
                        └──< TimeVote >── (N) MeetingTimeCandidate (1) ─── (N) Meeting
                        └──< PlaceVote >── (N) PlaceCandidate (1) ─── (N) Meeting
```

## place_candidate

**테이블 설명:**
- 모임의 조건에 맞춰 LLM이 추천한 장소 후보들을 저장하는 테이블입니다.
- 모임의 `preference_place`, `location_choice_type`, `location_choice_value` 등을 기반으로 추천됩니다.
- `id`는 외부 API의 Place ID를 사용하며, 실제 장소 정보는 `place` 테이블에 저장됩니다.
- `location_type`: 위치 선택 방식에 따라 다른 필드가 사용됩니다.
  - `center_location`: 중심 위치 기반 추천
  - `preference_area`: 선호 지역 기반 추천 (`preference_area` 필드 사용)
  - `preference_subway`: 선호 지하철역 기반 추천 (`preference_subway` 필드 사용)
- `food`, `condition`: 장소의 음식 종류나 조건 정보
- 참가자들이 `place_vote` 테이블을 통해 이 후보들에 투표하고, 주최자가 최종 선택한 장소가 `place` 테이블에 저장됩니다.

| Column | Type | Note |
| --- | --- | --- |
| id | PK | varchar(API Place ID 사용) |
| meeting_id | FK(Meeting.id) |  |
| location | varchar | 지역, 정확한 위치 (위도 경도) → ex 강남구, 용산구 |
| preference_subway | jsonb | {"서울역", "종각"} |
| preference_area | jsonb | {"강남구" ,"강동구", "마포구"} |
| food | varchar |  |
| condition | varchar |  |
| location_type | enum | center_location, preference_area, preference_subway |

**SQL:**
```sql
CREATE TABLE place_candidate (
    id VARCHAR(255) PRIMARY KEY,
    meeting_id UUID NOT NULL REFERENCES meeting(id) ON DELETE CASCADE,
    location VARCHAR(255),
    preference_subway JSONB,
    preference_area JSONB,
    food VARCHAR(255),
    condition VARCHAR(255),
    location_type location_choice_type_enum
);
```

**참고:**
- location : 지역, 정확한 위치 (위도 경도) → ex 강남구, 용산구
- place : 식당 , 카페 → ex 장터, 벳남미식

## review

**테이블 설명:**
- 모임 완료 후 모임에 대한 리뷰를 저장하는 테이블입니다.
- 참가자들이 모임 후 경험을 공유하고 평가할 수 있습니다.
- `rating`: 평가 점수 (1-5)
- `image_list`: 리뷰에 첨부된 이미지 URL 리스트 (fileserver 필요, Supabase에 있음)
- `text`: 리뷰 텍스트 내용
- `like_count`: 리뷰 좋아요 수
- `deleted_at`: 소프트 삭제 시간 (null이면 삭제되지 않음)

| Column | Type | Note |
| --- | --- | --- |
| id | PK | UUID |
| meeting_id | FK(Meeting.id) |  |
| user_id | FK(User.id) | 리뷰 작성자 |
| rating | int | 평가 점수 (1-5) |
| image_list | text[] | 이미지 URL 리스트 [image1, image2, ...] |
| text | text | 리뷰 텍스트 |
| like_count | int | 좋아요 수 |
| created_at | timestamp |  |
| updated_at | timestamp |  |
| deleted_at | timestamp | 소프트 삭제 시간 (null이면 삭제되지 않음) |

**SQL:**
```sql
CREATE TABLE review (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID NOT NULL REFERENCES meeting(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    rating INTEGER,
    image_list TEXT[],
    text TEXT,
    like_count INTEGER DEFAULT 0 NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);
```