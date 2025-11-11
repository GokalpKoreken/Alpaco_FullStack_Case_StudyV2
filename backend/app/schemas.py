from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str | None = None
    exp: int | None = None


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8)
    is_admin: bool = False


class UserRead(UserBase):
    id: UUID
    is_admin: bool
    created_at: datetime


class DropBase(BaseModel):
    title: str
    description: str | None = None
    stock: int = Field(gt=0)
    waitlist_open_at: datetime
    claim_open_at: datetime
    claim_close_at: datetime


class DropCreate(DropBase):
    base_priority: int = 0


class DropUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    stock: int | None = Field(default=None, gt=0)
    waitlist_open_at: datetime | None = None
    claim_open_at: datetime | None = None
    claim_close_at: datetime | None = None
    base_priority: int | None = None


class DropRead(DropBase):
    id: UUID
    base_priority: int
    created_at: datetime
    updated_at: datetime


class WaitlistEntryRead(BaseModel):
    id: UUID
    user_id: UUID
    drop_id: UUID
    joined_at: datetime
    priority_score: float
    status: str


class ClaimRead(BaseModel):
    id: UUID
    user_id: UUID
    drop_id: UUID
    claim_code: str
    claimed_at: datetime


class ClaimRequest(BaseModel):
    drop_id: UUID


class ClaimResponse(BaseModel):
    claim_code: str
    claimed_at: datetime


class JoinLeaveResponse(BaseModel):
    status: str
    already_joined: bool = False


class PriorityPreview(BaseModel):
    priority_score: float
    seed: str
