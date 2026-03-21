from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..dependencies import get_db, get_current_user
from ..models.user import User
from ..schemas.auth import LoginRequest, Token, TokenRefresh
from ..schemas.user import UserCreate, UserRead
from ..services.auth_service import AuthService
from ..utils.exceptions import conflict, unauthorized

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise conflict(f"Email '{payload.email}' is already registered")

    auth_service = AuthService(db)
    user = User(
        email=payload.email,
        hashed_password=auth_service.hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(payload.email, payload.password)
    access_token = auth_service.create_access_token(user.id, user.role.value)
    refresh_token = auth_service.create_refresh_token(user.id)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
def refresh_token(payload: TokenRefresh, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    decoded = auth_service.decode_token(payload.refresh_token)
    if decoded.get("type") != "refresh":
        raise unauthorized("Invalid token type")
    user_id = int(decoded["sub"])
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise unauthorized("User not found")
    access_token = auth_service.create_access_token(user.id, user.role.value)
    new_refresh = auth_service.create_refresh_token(user.id)
    return Token(access_token=access_token, refresh_token=new_refresh)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: User = Depends(get_current_user)):
    # JWT is stateless; client simply discards the token.
    # In production, add token to a denylist (Redis).
    return None
