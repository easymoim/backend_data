"""
Render 서버 keep-alive 스크립트
서버가 일정 시간 요청이 없어 꺼지는 것을 방지하기 위해 주기적으로 헬스 체크 요청을 보냅니다.
"""
import asyncio
import httpx
import os
import sys
import time
from datetime import datetime
from typing import Optional


class KeepAliveClient:
    def __init__(
        self,
        server_url: str,
        interval: int = 60,  # 기본 1분 (60초)
        endpoint: str = "/health",
        timeout: int = 10
    ):
        """
        Args:
            server_url: 서버 URL (예: https://your-app.onrender.com)
            interval: 요청 간격 (초 단위, 기본값: 60초 = 1분)
            endpoint: 헬스 체크 엔드포인트 (기본값: /health)
            timeout: 요청 타임아웃 (초 단위, 기본값: 10초)
        """
        self.server_url = server_url.rstrip('/')
        self.endpoint = endpoint
        self.interval = interval
        self.timeout = timeout
        self.url = f"{self.server_url}{self.endpoint}"
        self.client = httpx.AsyncClient(timeout=timeout)
        self.running = False

    async def ping(self) -> bool:
        """서버에 헬스 체크 요청을 보냅니다."""
        try:
            response = await self.client.get(self.url)
            response.raise_for_status()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] ✅ 서버 응답 성공: {response.status_code}")
            return True
        except httpx.TimeoutException:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] ⚠️  요청 타임아웃: {self.url}")
            return False
        except httpx.HTTPStatusError as e:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] ⚠️  서버 응답 오류: {e.response.status_code}")
            return False
        except Exception as e:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] ❌ 요청 실패: {str(e)}")
            return False

    async def run(self, once: bool = False):
        """서버에 요청을 보냅니다.
        
        Args:
            once: True이면 한 번만 요청하고 종료, False이면 주기적으로 계속 요청
        """
        self.running = True
        print(f"🚀 Keep-alive 시작: {self.url}")
        if once:
            print("📌 한 번만 실행 모드")
        else:
            print(f"⏰ 요청 간격: {self.interval}초 ({self.interval // 60}분)")
        print("=" * 60)

        try:
            while self.running:
                await self.ping()
                if once:
                    break
                await asyncio.sleep(self.interval)
        except KeyboardInterrupt:
            print("\n\n⏹️  Keep-alive 중지 중...")
            self.running = False
        finally:
            await self.client.aclose()
            print("✅ Keep-alive 종료")

    def stop(self):
        """Keep-alive를 중지합니다."""
        self.running = False


async def main():
    """메인 함수"""
    # 한 번만 실행 모드 확인
    once = "--once" in sys.argv or os.getenv("ONCE", "").lower() == "true"
    if "--once" in sys.argv:
        sys.argv.remove("--once")
    
    # 환경 변수에서 서버 URL 가져오기
    server_url = os.getenv("SERVER_URL")
    
    # 명령줄 인자에서 서버 URL 가져오기
    if not server_url and len(sys.argv) > 1:
        server_url = sys.argv[1]
    
    # 서버 URL이 없으면 에러
    if not server_url:
        print("❌ 서버 URL이 필요합니다.")
        print("\n사용법:")
        print("  python keep_alive.py <서버_URL>")
        print("  또는")
        print("  SERVER_URL=https://your-app.onrender.com python keep_alive.py")
        print("\n옵션:")
        print("  --once 또는 ONCE=true: 한 번만 실행하고 종료 (GitHub Actions용)")
        print("  환경 변수 INTERVAL: 요청 간격 (초, 기본값: 60)")
        print("  환경 변수 ENDPOINT: 엔드포인트 (기본값: /health)")
        sys.exit(1)

    # 환경 변수에서 설정 가져오기
    interval = int(os.getenv("INTERVAL", "60"))
    endpoint = os.getenv("ENDPOINT", "/health")
    timeout = int(os.getenv("TIMEOUT", "10"))

    # Keep-alive 클라이언트 생성 및 실행
    client = KeepAliveClient(
        server_url=server_url,
        interval=interval,
        endpoint=endpoint,
        timeout=timeout
    )
    
    await client.run(once=once)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 프로그램 종료")
        sys.exit(0)

