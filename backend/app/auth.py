from datetime import datetime, timedelta, timezone
import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_session
from .models import User
from .schemas import TokenPayload

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode = {"sub": subject, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def authenticate_user(session: Session, email: str, password: str) -> User | None:
    stmt = select(User).where(User.email == email)
    user = session.scalar(stmt)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def get_current_user(
    session: Annotated[Session, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    settings = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        token_data = TokenPayload(**payload)
    except JWTError as exc:  # pragma: no cover - we rethrow consistently
        raise credentials_exception from exc

    if token_data.sub is None:
        raise credentials_exception

    try:
        user_id = uuid.UUID(token_data.sub)
    except (TypeError, ValueError) as exc:
        raise credentials_exception from exc

    stmt = select(User).where(User.id == user_id)
    user = session.scalar(stmt)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user


def get_current_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user
