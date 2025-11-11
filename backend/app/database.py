from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from .config import get_settings

Base = declarative_base()

_settings = get_settings()
_database_url = _settings.database_url or "sqlite:///./dropspot.db"
_connect_args: dict[str, object] = {}
if _database_url.startswith("sqlite"):
    _connect_args["check_same_thread"] = False

engine = create_engine(_database_url, echo=_settings.debug, future=True, connect_args=_connect_args)


def get_engine():
    return engine


SessionLocal = sessionmaker(bind=engine, class_=Session, autoflush=False, autocommit=False, future=True)


def override_engine(new_engine) -> None:
    global engine, SessionLocal
    engine = new_engine
    SessionLocal = sessionmaker(bind=engine, class_=Session, autoflush=False, autocommit=False, future=True)


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    from . import models  # noqa: F401

    engine = get_engine()
    Base.metadata.create_all(bind=engine)
