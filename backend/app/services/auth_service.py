from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from ..models.user import User
from ..config import get_settings
from ..utils.exceptions import unauthorized

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    def create_access_token(self, user_id: int, role: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
        payload = {
            "sub": str(user_id),
            "role": role,
            "type": "access",
            "exp": expire,
        }
        return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

    def create_refresh_token(self, user_id: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "exp": expire,
        }
        return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

    def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload
        except JWTError:
            raise unauthorized("Invalid or expired token")

    def get_user_from_token(self, token: str) -> User:
        payload = self.decode_token(token)
        if payload.get("type") != "access":
            raise unauthorized("Invalid token type")
        user_id = payload.get("sub")
        if not user_id:
            raise unauthorized()
        user = self.db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.is_active:
            raise unauthorized("User not found or inactive")
        return user

    def authenticate_user(self, email: str, password: str) -> User:
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not self.verify_password(password, user.hashed_password):
            raise unauthorized("Invalid email or password")
        if not user.is_active:
            raise unauthorized("Account is inactive")
        return user
