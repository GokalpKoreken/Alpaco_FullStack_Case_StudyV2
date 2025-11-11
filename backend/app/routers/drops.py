from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import auth as auth_service
from ..database import get_session
from ..models import Drop, WaitlistEntry
from ..schemas import ClaimResponse, DropRead, JoinLeaveResponse
from ..services import waitlist as waitlist_service

router = APIRouter(prefix="/drops", tags=["drops"])


def _now() -> datetime:
    return datetime.now(timezone.utc)


@router.get("", response_model=list[DropRead])
def list_active_drops(session: Session = Depends(get_session)):
    stmt = select(Drop).where(Drop.claim_close_at >= _now()).order_by(Drop.claim_open_at.asc())
    drops = session.scalars(stmt).all()
    return drops


@router.get("/{drop_id}", response_model=DropRead)
def get_drop(drop_id: UUID, session: Session = Depends(get_session)):
    drop = session.get(Drop, drop_id)
    if not drop:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Drop not found")
    return drop


@router.post("/{drop_id}/join", response_model=JoinLeaveResponse)
def join_waitlist(
    drop_id: UUID,
    session: Session = Depends(get_session),
    current_user=Depends(auth_service.get_current_active_user),
):
    drop = session.get(Drop, drop_id)
    if not drop:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Drop not found")

    entry, already = waitlist_service.join_waitlist(session, current_user, drop)
    status_text = "already_joined" if already else "joined"
    return JoinLeaveResponse(status=status_text, already_joined=already)


@router.post("/{drop_id}/leave", response_model=JoinLeaveResponse)
def leave_waitlist(
    drop_id: UUID,
    session: Session = Depends(get_session),
    current_user=Depends(auth_service.get_current_active_user),
):
    drop = session.get(Drop, drop_id)
    if not drop:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Drop not found")

    removed = waitlist_service.leave_waitlist(session, current_user, drop)
    status_text = "left" if removed else "not_in_waitlist"
    return JoinLeaveResponse(status=status_text, already_joined=removed)


@router.post("/{drop_id}/claim", response_model=ClaimResponse)
def claim(
    drop_id: UUID,
    session: Session = Depends(get_session),
    current_user=Depends(auth_service.get_current_active_user),
):
    drop = session.get(Drop, drop_id)
    if not drop:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Drop not found")

    claim_obj = waitlist_service.claim_drop(session, current_user, drop)
    return ClaimResponse(claim_code=claim_obj.claim_code, claimed_at=claim_obj.claimed_at)


@router.get("/{drop_id}/waitlist/me")
def my_waitlist_status(
    drop_id: UUID,
    session: Session = Depends(get_session),
    current_user=Depends(auth_service.get_current_active_user),
):
    stmt = select(WaitlistEntry).where(WaitlistEntry.user_id == current_user.id, WaitlistEntry.drop_id == drop_id)
    entry = session.scalar(stmt)
    if not entry:
        return {"status": "not_registered"}
    return {
        "status": entry.status,
        "priority_score": float(entry.priority_score),
        "joined_at": entry.joined_at,
    }
