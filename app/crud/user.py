from sqlalchemy.orm import Session
from typing import Optional
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
    return db.query(User).filter(
        User.oauth_provider == oauth_provider,
        User.oauth_id == oauth_id
    ).first()


def create_user(db: Session, user: UserCreate) -> User:
    """새 사용자 생성"""
    # oauth_provider Enum을 문자열로 변환
    oauth_provider_str = user.oauth_provider.value if isinstance(user.oauth_provider, OAuthProvider) else str(user.oauth_provider)
    
    db_user = User(
        name=user.name,
        email=user.email,
        oauth_provider=oauth_provider_str,
        oauth_id=user.oauth_id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
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

