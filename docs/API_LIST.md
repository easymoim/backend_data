# EasyMoim API 리스트

## 기본 엔드포인트

- `GET /` - 루트 엔드포인트
- `GET /health` - 헬스 체크 엔드포인트

## 인증 (Auth)

- `POST /api/v1/auth/kakao/login` - 카카오 OAuth 로그인 (자동 회원가입/로그인)

## 사용자 (Users)

- `POST /api/v1/users` - 사용자 생성
- `GET /api/v1/users/{user_id}` - 사용자 조회
- `PUT /api/v1/users/{user_id}` - 사용자 정보 업데이트

## 모임 (Meetings)

- `POST /api/v1/meetings?creator_id={user_id}` - 모임 생성
- `GET /api/v1/meetings` - 모든 모임 목록 조회
- `GET /api/v1/meetings/creator/{creator_id}` - 생성자별 모임 목록 조회
- `GET /api/v1/meetings/share-code/{share_code}` - 공유 코드로 모임 조회
- `GET /api/v1/meetings/{meeting_id}` - 모임 상세 조회
- `PUT /api/v1/meetings/{meeting_id}` - 모임 정보 업데이트
- `DELETE /api/v1/meetings/{meeting_id}` - 모임 삭제

## 참가자 (Participants)

- `POST /api/v1/participants` - 참가자 추가 (로그인/비로그인 가능)
- `GET /api/v1/participants/meeting/{meeting_id}` - 모임별 참가자 목록 조회
- `GET /api/v1/participants/user/{user_id}` - 사용자별 참가한 모임 목록 조회
- `GET /api/v1/participants/{participant_id}` - 참가자 조회
- `PUT /api/v1/participants/{participant_id}` - 참가자 정보 업데이트
- `DELETE /api/v1/participants/{participant_id}` - 참가자 삭제

## 시간 후보 (Time Candidates)

- `POST /api/v1/time-candidates` - 시간 후보 생성
- `GET /api/v1/time-candidates/meeting/{meeting_id}` - 모임별 시간 후보 목록 조회
- `GET /api/v1/time-candidates/{candidate_id}` - 시간 후보 조회
- `DELETE /api/v1/time-candidates/{candidate_id}` - 시간 후보 삭제

## 시간 투표 (Time Votes)

- `POST /api/v1/time-votes` - 시간 투표 생성/업데이트 (중복 시 자동 업데이트)
- `GET /api/v1/time-votes/participant/{participant_id}` - 참가자별 시간 투표 목록 조회
- `GET /api/v1/time-votes/candidate/{candidate_id}` - 시간 후보별 투표 목록 조회
- `GET /api/v1/time-votes/{vote_id}` - 시간 투표 조회
- `PUT /api/v1/time-votes/{vote_id}` - 시간 투표 업데이트
- `DELETE /api/v1/time-votes/{vote_id}` - 시간 투표 삭제

## 장소 (Places)

- `POST /api/v1/places` - 장소 생성 (주최자가 선택한 최종 장소)
- `GET /api/v1/places` - 모든 장소 목록 조회
- `GET /api/v1/places/{place_id}` - 장소 조회
- `PUT /api/v1/places/{place_id}` - 장소 정보 업데이트
- `DELETE /api/v1/places/{place_id}` - 장소 삭제

## 장소 후보 (Place Candidates)

- `POST /api/v1/place-candidates` - 장소 후보 생성 (LLM 추천 장소)
- `GET /api/v1/place-candidates/meeting/{meeting_id}` - 모임별 장소 후보 목록 조회
- `GET /api/v1/place-candidates/{candidate_id}` - 장소 후보 조회
- `PUT /api/v1/place-candidates/{candidate_id}` - 장소 후보 정보 업데이트
- `DELETE /api/v1/place-candidates/{candidate_id}` - 장소 후보 삭제

## 장소 투표 (Place Votes)

- `POST /api/v1/place-votes` - 장소 투표 생성/업데이트 (중복 시 자동 업데이트)
- `GET /api/v1/place-votes/participant/{participant_id}` - 참가자별 장소 투표 목록 조회
- `GET /api/v1/place-votes/meeting/{meeting_id}` - 모임별 장소 투표 목록 조회
- `GET /api/v1/place-votes/{vote_id}` - 장소 투표 조회
- `PUT /api/v1/place-votes/{vote_id}` - 장소 투표 업데이트
- `DELETE /api/v1/place-votes/{vote_id}` - 장소 투표 삭제

## 리뷰 (Reviews)

- `POST /api/v1/reviews` - 리뷰 생성
- `GET /api/v1/reviews` - 모든 리뷰 목록 조회
- `GET /api/v1/reviews/{review_id}` - 리뷰 조회
- `GET /api/v1/reviews/meeting/{meeting_id}` - 모임별 리뷰 목록 조회
- `GET /api/v1/reviews/user/{user_id}` - 사용자별 리뷰 목록 조회
- `PUT /api/v1/reviews/{review_id}` - 리뷰 정보 업데이트
- `DELETE /api/v1/reviews/{review_id}` - 리뷰 삭제 (소프트 삭제)
- `POST /api/v1/reviews/{review_id}/like` - 리뷰 좋아요
- `DELETE /api/v1/reviews/{review_id}/like` - 리뷰 좋아요 취소

