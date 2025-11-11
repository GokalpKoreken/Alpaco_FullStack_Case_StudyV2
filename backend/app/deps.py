from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from .database import get_session
from .models import Drop


def get_drop(drop_id: UUID, session: Annotated[Session, Depends(get_session)]) -> Drop:
    drop = session.get(Drop, drop_id)
    if not drop:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Drop not found")
    return drop
