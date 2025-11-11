from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import auth as auth_service
from ..database import get_session
from ..models import Drop
from ..schemas import DropCreate, DropRead, DropUpdate

router = APIRouter(prefix="/admin/drops", tags=["admin"], dependencies=[Depends(auth_service.get_current_admin)])


@router.get("", response_model=list[DropRead])
def list_drops(session: Session = Depends(get_session)):
    stmt = select(Drop).order_by(Drop.claim_open_at.desc())
    return session.scalars(stmt).all()


@router.post("", response_model=DropRead, status_code=status.HTTP_201_CREATED)
def create_drop(payload: DropCreate, session: Session = Depends(get_session)):
    drop = Drop(**payload.model_dump())
    session.add(drop)
    session.commit()
    session.refresh(drop)
    return drop


@router.put("/{drop_id}", response_model=DropRead)
def update_drop(drop_id: UUID, payload: DropUpdate, session: Session = Depends(get_session)):
    drop = session.get(Drop, drop_id)
    if not drop:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Drop not found")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(drop, key, value)
    session.add(drop)
    session.commit()
    session.refresh(drop)
    return drop


@router.delete("/{drop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_drop(drop_id: UUID, session: Session = Depends(get_session)):
    drop = session.get(Drop, drop_id)
    if not drop:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Drop not found")
    session.delete(drop)
    session.commit()
    return None
