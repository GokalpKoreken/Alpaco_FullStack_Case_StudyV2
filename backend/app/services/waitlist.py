from __future__ import annotations

import secrets
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models import Claim, Drop, User, WaitlistEntry
from .seed import compute_priority_score


def _generate_claim_code() -> str:
    return secrets.token_hex(8)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_claim_window_open(drop: Drop) -> None:
    now = _utcnow()
    claim_open = _ensure_aware(drop.claim_open_at)
    claim_close = _ensure_aware(drop.claim_close_at)
    if not (claim_open <= now <= claim_close):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Claim window closed")


def _entry_rank(session: Session, entry: WaitlistEntry) -> int:
    ahead_stmt = (
        select(func.count())
        .select_from(WaitlistEntry)
        .where(WaitlistEntry.drop_id == entry.drop_id)
        .where(
            (WaitlistEntry.priority_score > entry.priority_score)
            | (
                (WaitlistEntry.priority_score == entry.priority_score)
                & (WaitlistEntry.joined_at < entry.joined_at)
            )
        )
    )
    ahead_count = session.scalar(ahead_stmt) or 0
    return ahead_count


def join_waitlist(session: Session, user: User, drop: Drop) -> tuple[WaitlistEntry, bool]:
    now = _utcnow()
    waitlist_open_at = _ensure_aware(drop.waitlist_open_at)
    signup_latency_ms = max(int((now - waitlist_open_at).total_seconds() * 1000), 0)
    account_created_at = _ensure_aware(user.created_at)
    account_age_days = max((now - account_created_at).days, 0)
    rapid_actions = 0  # would be tracked via rate limiter / audit table
    priority = compute_priority_score(
        base=drop.base_priority,
        signup_latency_ms=signup_latency_ms,
        account_age_days=account_age_days,
        rapid_actions=rapid_actions,
    )

    stmt = select(WaitlistEntry).where(WaitlistEntry.user_id == user.id, WaitlistEntry.drop_id == drop.id)
    existing = session.scalar(stmt)
    if existing:
        return existing, True

    entry = WaitlistEntry(
        user_id=user.id,
        drop_id=drop.id,
        priority_score=priority,
    )
    session.add(entry)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        existing = session.scalar(stmt)
        if existing:
            return existing, True
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Waitlist join conflict") from exc

    session.refresh(entry)
    return entry, False


def leave_waitlist(session: Session, user: User, drop: Drop) -> bool:
    stmt = select(WaitlistEntry).where(WaitlistEntry.user_id == user.id, WaitlistEntry.drop_id == drop.id)
    entry = session.scalar(stmt)
    if not entry:
        return False

    session.delete(entry)
    session.commit()
    return True


def claim_drop(session: Session, user: User, drop: Drop) -> Claim:
    _ensure_claim_window_open(drop)

    stmt = select(WaitlistEntry).where(WaitlistEntry.user_id == user.id, WaitlistEntry.drop_id == drop.id)
    entry = session.scalar(stmt)
    if not entry:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Waitlist entry not found")

    existing_claim_stmt = select(Claim).where(Claim.user_id == user.id, Claim.drop_id == drop.id)
    existing_claim = session.scalar(existing_claim_stmt)
    if existing_claim:
        return existing_claim

    total_claims_stmt = select(func.count()).select_from(Claim).where(Claim.drop_id == drop.id)
    total_claims = session.scalar(total_claims_stmt) or 0
    if total_claims >= drop.stock:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="No remaining claim slots")

    rank = _entry_rank(session, entry)
    if rank >= drop.stock:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="No remaining claim slots")

    claim_code = _generate_claim_code()
    claim = Claim(user_id=user.id, drop_id=drop.id, claim_code=claim_code)
    session.add(claim)
    entry.status = "claimed"
    session.add(entry)
    session.commit()
    session.refresh(claim)
    session.refresh(entry)
    return claim


def _ensure_aware(dt: datetime) -> datetime:
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)
