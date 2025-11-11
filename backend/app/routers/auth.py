from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import auth as auth_service
from ..database import get_session
from ..models import User
from ..schemas import Token, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, session: Session = Depends(get_session)):
    stmt = select(User).where(User.email == payload.email)
    existing = session.scalar(stmt)
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(email=payload.email, password_hash=auth_service.get_password_hash(payload.password), is_admin=payload.is_admin)
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered")
    session.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = auth_service.authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = auth_service.create_access_token(str(user.id))
    return Token(access_token=access_token)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(auth_service.get_current_active_user)):
    return current_user
