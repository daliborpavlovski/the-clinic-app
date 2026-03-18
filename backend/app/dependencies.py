from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import SessionLocal
from .services.auth_service import AuthService
from .models.user import User, UserRole
from .utils.exceptions import unauthorized, forbidden

bearer_scheme = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    auth_service = AuthService(db)
    return auth_service.get_user_from_token(token)


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.admin:
        raise forbidden("Admin access required")
    return current_user


def require_doctor_or_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in (UserRole.doctor, UserRole.admin):
        raise forbidden("Doctor or admin access required")
    return current_user
