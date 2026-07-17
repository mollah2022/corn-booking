import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.services.common_service import CommonService
from app.services.booking_service import BookingService
from app.repositories.booking_repository import BookingRepository
from app.api_client.booking_api_client import BookingApiClient

DATA_DIR = Path(__file__).parent / "data"
TEST_DATABASE_URL = "postgresql+psycopg2://test_user:test_pass@localhost:5434/test_booking_db"


# ---------- Shared test data ----------

@pytest.fixture(scope="function")
def sample_booking_raw():
    """Returns a fresh copy of raw booking dict for every test function,
    so mutations in one test never leak into another."""
    with open(DATA_DIR / "sample_booking.json", "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="function")
def sample_booking_raw_missing_fields(sample_booking_raw):
    """A variant with nested fields set to None, to test null-safety in transform()."""
    data = dict(sample_booking_raw)
    data["accommodations"] = None
    data["booker"] = None
    data["price"] = None
    data["currencies"] = None
    data["accommodation_details"] = None
    return data


# ---------- Services ----------

@pytest.fixture(scope="function")
def common_service():
    return CommonService()


@pytest.fixture(scope="function")
def mock_booking_repository():
    """A MagicMock repository - lets us assert on how BookingService calls it,
    without touching a real database."""
    return MagicMock()


@pytest.fixture(scope="function")
def booking_service(mock_booking_repository):
    return BookingService(booking_repository=mock_booking_repository)


# ---------- Repositories (real test database) ----------

@pytest.fixture(scope="session")
def db_engine():
    """One engine + one set of tables for the whole test session.
    Connection is properly disposed at the very end."""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)

    yield engine

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Fresh connection + transaction per test. Every test's changes are rolled back
    and the connection is explicitly closed, so no connection ever leaks."""
    connection = db_engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def booking_repository():
    return BookingRepository()


#------------- Api client fixtures --------------

@pytest.fixture(scope="function")
def api_client():
    return BookingApiClient(base_url="http://localhost:5001", api_key=None)


@pytest.fixture(scope="function")
def api_client_with_key():
    return BookingApiClient(base_url="http://localhost:5001", api_key="secret-key-123")




# ---------- Cron ----------

@pytest.fixture(scope="function")
def mock_cron_dependencies(mocker):
    """Patches every external dependency BookingCron talks to (API client, repository,
    service, DB session), so tests only exercise the orchestration logic in run()."""
    mock_api_client_cls = mocker.patch("app.cron.booking.BookingApiClient")
    mock_repository_cls = mocker.patch("app.cron.booking.BookingRepository")
    mock_service_cls = mocker.patch("app.cron.booking.BookingService")
    mock_session_scope = mocker.patch("app.cron.booking.session_scope")

    mock_session = MagicMock()
    mock_session_scope.return_value.__enter__.return_value = mock_session
    mock_session_scope.return_value.__exit__.return_value = False

    return {
        "api_client": mock_api_client_cls.return_value,
        "repository_cls": mock_repository_cls,
        "service": mock_service_cls.return_value,
        "session": mock_session,
    }

@pytest.fixture(scope="function")
def booking_cron_class():
    from app.cron.booking import BookingCron
    return BookingCron


# ---------- db.py session_scope ----------

@pytest.fixture(scope="function")
def real_session_scope(db_engine, mocker):
    """Patches app.db.SessionLocal to use our test engine's connection,
    so session_scope() itself can be exercised end-to-end."""
    from sqlalchemy.orm import sessionmaker
    connection = db_engine.connect()
    transaction = connection.begin()
    TestSessionLocal = sessionmaker(bind=connection)

    mocker.patch("app.db.SessionLocal", TestSessionLocal)

    yield

    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def flights_cron_class():
    from app.cron.flights import FlightsCron
    return FlightsCron
