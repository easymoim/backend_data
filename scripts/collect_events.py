"""
서울 문화행사 정보 수집 스크립트
서울 열린데이터 광장 API에서 문화행사 정보를 가져와 DB에 저장합니다.
"""
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.event_activity_information import EventActivityInformation


# API 설정
API_KEY = os.getenv("SEOUL_OPENAPI_KEY")
BASE_URL = f"http://openapi.seoul.go.kr:8088/{API_KEY}/xml/culturalEventInfo"
BATCH_SIZE = 1000  # 한 번에 가져올 데이터 수


def parse_date(date_str: str) -> datetime | None:
    """날짜 문자열을 datetime으로 변환"""
    if not date_str:
        return None
    try:
        # '2026-04-16 00:00:00.0' 형식
        return datetime.strptime(date_str.split('.')[0], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            # '2026-04-16' 형식
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return None


def parse_date_only(date_str: str):
    """날짜 문자열을 date로 변환"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def get_text(element, tag: str) -> str | None:
    """XML 엘리먼트에서 텍스트 추출"""
    child = element.find(tag)
    if child is not None and child.text:
        return child.text.strip()
    return None


def fetch_events(start_index: int, end_index: int) -> list[dict]:
    """API에서 이벤트 데이터 가져오기"""
    url = f"{BASE_URL}/{start_index}/{end_index}/"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ API 요청 실패: {e}")
        return []
    
    try:
        root = ET.fromstring(response.text)
    except ET.ParseError as e:
        print(f"❌ XML 파싱 실패: {e}")
        return []
    
    # 에러 체크
    result = root.find("RESULT")
    if result is not None:
        code = result.find("CODE")
        if code is not None and code.text != "INFO-000":
            message = result.find("MESSAGE")
            print(f"❌ API 에러: {code.text} - {message.text if message is not None else 'Unknown'}")
            return []
    
    events = []
    for row in root.findall("row"):
        event = {
            "category": get_text(row, "CODENAME"),
            "city_name": "서울시",  # 서울 API이므로 고정
            "guname": get_text(row, "GUNAME"),
            "title": get_text(row, "TITLE"),
            "date": get_text(row, "DATE"),  # 행사 날짜 (예: 2026-04-16~2026-04-16)
            "place": get_text(row, "PLACE"),
            "organization_name": get_text(row, "ORG_NAME"),
            "use_target": get_text(row, "USE_TRGT"),
            "use_fee": get_text(row, "USE_FEE"),
            "inquiry": get_text(row, "INQUIRY"),
            "program_info": get_text(row, "PROGRAM"),
            "organization_link": get_text(row, "ORG_LINK"),
            "thumbnail_image": get_text(row, "MAIN_IMG"),
            "hompage_link": get_text(row, "HMPG_ADDR"),
            "register_date": parse_date_only(get_text(row, "RGSTDATE")),
            "start_date": parse_date(get_text(row, "STRTDATE")),
            "end_date": parse_date(get_text(row, "END_DATE")),
            "program_time": get_text(row, "PRO_TIME"),
            "longitude": get_text(row, "LOT"),  # 경도
            "latitude": get_text(row, "LAT"),  # 위도
            "host_type": get_text(row, "TICKET"),  # 시민/기관
            "is_free": get_text(row, "IS_FREE"),
        }
        events.append(event)
    
    return events


def get_total_count() -> int:
    """전체 데이터 개수 조회"""
    url = f"{BASE_URL}/1/1/"
    
    try:
        response = requests.get(url, timeout=30)
        root = ET.fromstring(response.text)
        total_count = root.find("list_total_count")
        if total_count is not None:
            return int(total_count.text)
    except Exception as e:
        print(f"❌ 전체 개수 조회 실패: {e}")
    
    return 0


def upsert_events(db, events: list[dict]) -> tuple[int, int]:
    """이벤트 데이터를 DB에 upsert (title 기준)"""
    inserted = 0
    updated = 0
    
    for event_data in events:
        title = event_data.get("title")
        if not title:
            continue
        
        # 기존 데이터 조회 (title + start_date로 중복 체크)
        existing = db.query(EventActivityInformation).filter(
            EventActivityInformation.title == title,
            EventActivityInformation.start_date == event_data.get("start_date")
        ).first()
        
        if existing:
            # 업데이트
            for key, value in event_data.items():
                if value is not None:
                    setattr(existing, key, value)
            updated += 1
        else:
            # 새로 삽입
            new_event = EventActivityInformation(**event_data)
            db.add(new_event)
            inserted += 1
    
    db.commit()
    return inserted, updated


def main():
    """메인 실행 함수"""
    print("🚀 서울 문화행사 정보 수집 시작...")
    print(f"📅 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 전체 개수 조회
    total_count = get_total_count()
    if total_count == 0:
        print("❌ 데이터가 없거나 API 조회에 실패했습니다.")
        return
    
    print(f"📊 전체 데이터 개수: {total_count}")
    
    # DB 세션 생성
    db = SessionLocal()
    
    try:
        total_inserted = 0
        total_updated = 0
        
        # 배치로 데이터 가져오기
        for start in range(1, total_count + 1, BATCH_SIZE):
            end = min(start + BATCH_SIZE - 1, total_count)
            print(f"📥 데이터 수집 중: {start} ~ {end}")
            
            events = fetch_events(start, end)
            if events:
                inserted, updated = upsert_events(db, events)
                total_inserted += inserted
                total_updated += updated
                print(f"   ✅ 신규: {inserted}, 업데이트: {updated}")
        
        print(f"\n🎉 수집 완료!")
        print(f"   📥 신규 삽입: {total_inserted}")
        print(f"   🔄 업데이트: {total_updated}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

