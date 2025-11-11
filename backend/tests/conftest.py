import os
import tempfile
from collections.abc import Generator

os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("DROPSPOT_SEED", "testseed1234")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

os.environ.setdefault("DATABASE_URL", "sqlite:///./test-suite.db")

from app.database import Base, override_engine
from app.main import create_application


@pytest.fixture(scope="session")
def db_engine() -> Generator:
    tmpdir = tempfile.mkdtemp(prefix="dropspot-test-")
    db_path = os.path.join(tmpdir, "test.db")
    engine = create_engine(
        f"sqlite:///{db_path}",
        future=True,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    override_engine(engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    connection = db_engine.connect()
    transaction = connection.begin()
    SessionTesting = sessionmaker(bind=connection, autoflush=False, autocommit=False, future=True)
    session = SessionTesting()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db_engine, db_session):
    app = create_application()

    def _get_session_override():
        try:
            yield db_session
        finally:
            pass

    from app.database import get_session

    app.dependency_overrides[get_session] = _get_session_override

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
