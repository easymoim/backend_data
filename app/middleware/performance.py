"""
성능 측정 미들웨어
각 API 요청의 실행 시간을 측정하고 상세 분석을 제공합니다.
"""
import time
from typing import Callable, Dict, List
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

# 성능 통계 저장
performance_stats: Dict[str, List[Dict]] = {
    "requests": [],
    "endpoints": {},
}

# 최근 요청 저장 (최대 100개)
MAX_REQUESTS = 100


class PerformanceMiddleware(BaseHTTPMiddleware):
    """API 요청 성능 측정 미들웨어"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 요청 시작 시간
        start_time = time.time()
        
        # 요청 정보
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else ""
        
        # 단계별 시간 측정
        timings = {
            "total": 0,
            "request_parse": 0,
            "db_query": 0,
            "processing": 0,
            "response": 0,
        }
        
        try:
            # 요청 파싱 시간
            parse_start = time.time()
            # 요청 처리
            response = await call_next(request)
            parse_end = time.time()
            timings["request_parse"] = parse_end - parse_start
            
            # 처리 시간 계산
            total_time = time.time() - start_time
            timings["total"] = total_time
            timings["processing"] = total_time - timings["request_parse"]
            
            # 응답 상태 코드
            status_code = response.status_code
            
            # 성능 통계 기록
            request_info = {
                "method": method,
                "path": path,
                "query_params": query_params,
                "status_code": status_code,
                "total_time": round(total_time, 3),
                "timings": {k: round(v, 3) for k, v in timings.items()},
                "timestamp": time.time()
            }
            
            # 전체 요청 목록에 추가
            performance_stats["requests"].append(request_info)
            if len(performance_stats["requests"]) > MAX_REQUESTS:
                performance_stats["requests"] = performance_stats["requests"][-MAX_REQUESTS:]
            
            # 엔드포인트별 통계
            endpoint_key = f"{method} {path}"
            if endpoint_key not in performance_stats["endpoints"]:
                performance_stats["endpoints"][endpoint_key] = {
                    "count": 0,
                    "total_time": 0,
                    "min_time": float('inf'),
                    "max_time": 0,
                    "avg_time": 0,
                    "errors": 0,
                    "recent_times": []
                }
            
            endpoint_stats = performance_stats["endpoints"][endpoint_key]
            endpoint_stats["count"] += 1
            endpoint_stats["total_time"] += total_time
            endpoint_stats["min_time"] = min(endpoint_stats["min_time"], total_time)
            endpoint_stats["max_time"] = max(endpoint_stats["max_time"], total_time)
            endpoint_stats["avg_time"] = endpoint_stats["total_time"] / endpoint_stats["count"]
            
            if status_code >= 400:
                endpoint_stats["errors"] += 1
            
            # 최근 10개 시간만 유지
            endpoint_stats["recent_times"].append(round(total_time, 3))
            if len(endpoint_stats["recent_times"]) > 10:
                endpoint_stats["recent_times"] = endpoint_stats["recent_times"][-10:]
            
            # 느린 요청 로깅
            if total_time >= 1.0:
                logger.warning(
                    f"🐌 느린 요청: {method} {path} - {total_time:.3f}초 (상태코드: {status_code})"
                )
            elif total_time >= 0.5:
                logger.info(
                    f"⏱️  요청: {method} {path} - {total_time:.3f}초"
                )
            
            # 응답 헤더에 처리 시간 추가
            response.headers["X-Process-Time"] = str(round(total_time, 3))
            
            return response
            
        except Exception as e:
            # 에러 발생 시에도 시간 측정
            total_time = time.time() - start_time
            logger.error(
                f"❌ 요청 처리 중 에러: {method} {path} - {total_time:.3f}초 - {str(e)}"
            )
            raise


def get_performance_stats() -> Dict:
    """성능 통계 반환"""
    # 엔드포인트별 통계 정리
    endpoint_stats = {}
    for endpoint, stats in performance_stats["endpoints"].items():
        endpoint_stats[endpoint] = {
            "count": stats["count"],
            "avg_time": round(stats["avg_time"], 3),
            "min_time": round(stats["min_time"], 3),
            "max_time": round(stats["max_time"], 3),
            "errors": stats["errors"],
            "error_rate": round(stats["errors"] / stats["count"] * 100, 2) if stats["count"] > 0 else 0,
            "recent_times": stats["recent_times"]
        }
    
    # 느린 요청 찾기 (1초 이상)
    slow_requests = [
        req for req in performance_stats["requests"][-20:]
        if req["total_time"] >= 1.0
    ]
    
    # 전체 통계
    all_times = [req["total_time"] for req in performance_stats["requests"]]
    total_requests = len(performance_stats["requests"])
    
    return {
        "total_requests": total_requests,
        "average_time": round(sum(all_times) / len(all_times), 3) if all_times else 0,
        "min_time": round(min(all_times), 3) if all_times else 0,
        "max_time": round(max(all_times), 3) if all_times else 0,
        "endpoints": endpoint_stats,
        "slow_requests": slow_requests[-10:],  # 최근 10개 느린 요청
        "recent_requests": performance_stats["requests"][-20:]  # 최근 20개 요청
    }


def clear_stats():
    """통계 초기화"""
    global performance_stats
    performance_stats = {
        "requests": [],
        "endpoints": {},
    }
