import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    waitlist_entries: Mapped[list["WaitlistEntry"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    claims: Mapped[list["Claim"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Drop(Base):
    __tablename__ = "drops"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    waitlist_open_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    claim_open_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    claim_close_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    base_priority: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    waitlist_entries: Mapped[list["WaitlistEntry"]] = relationship(back_populates="drop", cascade="all, delete-orphan")
    claims: Mapped[list["Claim"]] = relationship(back_populates="drop", cascade="all, delete-orphan")


class WaitlistEntry(Base):
    __tablename__ = "waitlist_entries"
    __table_args__ = (
        UniqueConstraint("user_id", "drop_id", name="uq_waitlist_user_drop"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    drop_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("drops.id", ondelete="CASCADE"), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    priority_score: Mapped[float] = mapped_column(Numeric(10, 4), default=0)
    status: Mapped[str] = mapped_column(String(50), default="waiting")

    user: Mapped[User] = relationship(back_populates="waitlist_entries")
    drop: Mapped[Drop] = relationship(back_populates="waitlist_entries")


class Claim(Base):
    __tablename__ = "claims"
    __table_args__ = (
        UniqueConstraint("drop_id", "user_id", name="uq_claim_drop_user"),
        UniqueConstraint("claim_code", name="uq_claim_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    drop_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("drops.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    claim_code: Mapped[str] = mapped_column(String(32), nullable=False)
    claimed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    drop: Mapped[Drop] = relationship(back_populates="claims")
    user: Mapped[User] = relationship(back_populates="claims")
