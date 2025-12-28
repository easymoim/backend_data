-- ============================================
-- 성능 최적화를 위한 추가 인덱스
-- ============================================

-- meeting 테이블 인덱스
-- deleted_at 단독 인덱스 (모든 조회에서 deleted_at 필터링 사용)
CREATE INDEX IF NOT EXISTS idx_meeting_deleted_at 
ON meeting(deleted_at) 
WHERE deleted_at IS NULL;

-- creator_id + deleted_at 복합 인덱스 (생성자별 모임 조회 최적화)
CREATE INDEX IF NOT EXISTS idx_meeting_creator_deleted 
ON meeting(creator_id, deleted_at) 
WHERE deleted_at IS NULL;

-- creator_id + deleted_at + status 복합 인덱스 (호스트 모임 조회 최적화)
CREATE INDEX IF NOT EXISTS idx_meeting_creator_deleted_status 
ON meeting(creator_id, deleted_at, status) 
WHERE deleted_at IS NULL;

-- deleted_at + status 인덱스 (일반 모임 조회 최적화)
CREATE INDEX IF NOT EXISTS idx_meeting_deleted_status 
ON meeting(deleted_at, status) 
WHERE deleted_at IS NULL;

-- participant 테이블 인덱스
-- user_id + meeting_id 복합 인덱스 (참가자 모임 조회 최적화)
CREATE INDEX IF NOT EXISTS idx_participant_user_meeting 
ON participant(user_id, meeting_id);

-- meeting_id + has_responded 인덱스 (참가자 통계 조회 최적화)
CREATE INDEX IF NOT EXISTS idx_participant_meeting_responded 
ON participant(meeting_id, has_responded);

-- 설명
COMMENT ON INDEX idx_meeting_deleted_at IS 
'모임 조회 최적화: deleted_at 필터링 (소프트 삭제된 모임 제외)';

COMMENT ON INDEX idx_meeting_creator_deleted IS 
'생성자별 모임 조회 최적화: creator_id와 deleted_at 조건';

COMMENT ON INDEX idx_meeting_creator_deleted_status IS 
'호스트 모임 조회 최적화: creator_id로 필터링하고 deleted_at과 status 조건 적용';

COMMENT ON INDEX idx_meeting_deleted_status IS 
'일반 모임 조회 최적화: deleted_at과 status 조건 적용';

COMMENT ON INDEX idx_participant_user_meeting IS 
'참가자 모임 조회 최적화: user_id와 meeting_id로 빠른 조회';

COMMENT ON INDEX idx_participant_meeting_responded IS 
'참가자 통계 조회 최적화: meeting_id와 has_responded로 통계 계산';

