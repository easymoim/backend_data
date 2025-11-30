## user

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

## meeting

| Column | Type | Note | example |
| --- | --- | --- | --- |
| id | PK | UUID |  |
| name | varchar |  | 이지모임 |
| creator_id | FK(User.id) | Host |  |
| purpose | string[] |  | [’dining’, ‘drink’] |
| is_one_place | boolean | 한 곳에서 해결 여부 |  |
| location_choice_type | enum | center_location, preference_area, preference_subway |  |
| location_choice_value | varchar | {”강남구” ,“강동구”, “마포구”} || {”강남역”, “설대입구역”, “구디역”} || {직접입력한값} |  |
| preference_place |  | {”mood” : “대화 나누기 좋은”, “food” : “한식”, “condition”: “주차”} |  |
| deadline | timestamp | 2025-11-27 23:59 |  |
| expected_participant_count | int | 예상 참가 인원 |  |
| share_code |  | 공유 코드 |  |
| confirmed_time |  | 확정된 약속 시간 |  |
| confirmed_location |  | 확정된 장소 |  |
| confirmed_at |  | 주최자가 “확정하기!” 누른 시간 |  |
| created_at | timestamp |  |  |
| updated_at |  |  |  |

## participant

| Column | Type | Note |
| --- | --- | --- |
| id | PK | UUID |
| meeting_id | FK(Meeting.id) |  |
| user_id | FK(User.id), nullable | 비로그인 사용자도 가능 |
| nickname | varchar | 닉네임 |
| oauth_key |  | 카카오 고유 id |
| is_invited |  |  |
| has_responded |  | 응답 여부 |
| preference_place |  | {”mood” : “대화 나누기 좋은”, “food” : “한식”, “condition”: “주차”} |
| location |  |  |
| created_at |  |  |
| updated_at |  |  |

## time_candidate

| Column | Type | Note | example |
| --- | --- | --- | --- |
| id | PK | UUID |  |
| meeting_id | FK(Meeting.id) |  |  |
| candidate_time | json | 후보 시간 | {
 “가능한 시간” : “vote_count”,
“25.11.11.09:00” : 3,

} |
| created_at | timestamp |  |  |
|  |  |  |  |

## time_vote (누가 몇시에 투표했는지)

| Column | Type | Note |
| --- | --- | --- |
| id | PK | UUID |
| participant_id | FK(Participant.id) |  |
| meeting_id |  |  |
| time_candidate_id | FK(MeetingTimeCandidate.id) |  |
| is_available |  |  |
| memo |  |  |
| created_at | timestamp |  |
| updated_at | timestamp |  |
|  |  |  |

## place_vote (누가 어떤 장소에 투표했는지)

| Column | Type | Note |
| --- | --- | --- |
| id | PK | UUID |
| participant_id | FK(Participant.id) |  |
| meeting_id |  |  |
| time_candidate_id | FK(MeetingTimeCandidate.id) |  |
| is_available |  |  |
| memo |  |  |
| created_at | timestamp |  |
| updated_at | timestamp |  |
|  |  |  |

---

## place

(llm이 추천해준 것 중에서 주최자가 선택한 것이 담김)

| Column | Type | Note |
| --- | --- | --- |
| id | PK | varchar(API Place ID 사용) |
| name | varchar |  |
| category | varchar |  |
| address | text |  |
| location |  |  |
|  |  |  |
| rating | float | nullable |
| thumbnail | text | nullable |
| updated_at | timestamp |  |

```bash
User (1) ───< Participant >─── (N) Meeting
                        │
                        │
                        └──< TimeVote >── (N) MeetingTimeCandidate (1)

```

## place_candidate

| Column | Type | Note |
| --- | --- | --- |
| id | PK | varchar(API Place ID 사용) |
| meeting_id |  |  |
| location |  |  |
| preference_subway | json | {”서울역”, “종각”} |
| preference_area | json | {”강남구” ,“강동구”, “마포구”} |
| food |  |  |
| condition |  |  |
| location_type | enum | center_location, preference_area, preference_subway |
|  |  |  |
- location : 지역, 정확한 위치 (위도 경도) → ex 강남구, 용산구
- place : 식당 , 카페 → ex 장터, 벳남미식
- review 관련 테이블 나중에 해주세요 제발제발제발제발