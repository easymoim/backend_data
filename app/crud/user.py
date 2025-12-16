from sqlalchemy.orm import Session
from sqlalchemy import text, cast, String
from typing import Optional
from datetime import datetime
from app.models.user import User, OAuthProvider
from app.schemas.user import UserCreate, UserUpdate


def get_user(db: Session, user_id: int) -> Optional[User]:
    """사용자 ID로 조회"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """이메일로 사용자 조회"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_oauth(db: Session, oauth_provider: str, oauth_id: str) -> Optional[User]:
    """OAuth 정보로 사용자 조회"""
    # DB의 oauth_provider는 oauth_provider_enum 타입이므로 타입 캐스팅 필요
    # PostgreSQL enum을 문자열로 캐스팅하여 비교
    result = db.execute(
        text('''
            SELECT * FROM "user" 
            WHERE oauth_provider::text = :oauth_provider 
            AND oauth_id = :oauth_id 
            LIMIT 1
        '''),
        {"oauth_provider": oauth_provider, "oauth_id": oauth_id}
    )
    row = result.first()
    if row:
        # Row 객체를 User 모델로 변환
        return db.query(User).filter(User.id == row.id).first()
    return None


def create_user(db: Session, user: UserCreate) -> User:
    """새 사용자 생성"""
    # oauth_provider Enum을 문자열로 변환
    oauth_provider_str = user.oauth_provider.value if isinstance(user.oauth_provider, OAuthProvider) else str(user.oauth_provider)
    
    # DB의 oauth_provider는 oauth_provider_enum 타입이므로 타입 캐스팅 필요
    # Raw SQL을 사용하여 enum 타입으로 캐스팅
    result = db.execute(
        text('''
            INSERT INTO "user" (name, email, oauth_provider, oauth_id, is_active, created_at, updated_at)
            VALUES (:name, :email, CAST(:oauth_provider AS oauth_provider_enum), :oauth_id, :is_active, :created_at, :updated_at)
            RETURNING id
        '''),
        {
            "name": user.name,
            "email": user.email,
            "oauth_provider": oauth_provider_str,
            "oauth_id": user.oauth_id,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    )
    user_id = result.scalar()
    db.commit()
    
    # 생성된 사용자 조회
    db_user = get_user(db, user_id)
    return db_user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """사용자 정보 업데이트"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    if user_update.name is not None:
        db_user.name = user_update.name
    
    db.commit()
    db.refresh(db_user)
    return db_user

