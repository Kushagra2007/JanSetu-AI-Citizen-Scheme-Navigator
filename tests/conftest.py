import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from database import Base, get_db
import main as main_module

TEST_DB_URL = "sqlite:///./test_citizen_navigator.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


main_module.app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    return TestClient(main_module.app)


@pytest.fixture
def registered_user(client):
    payload = {"name": "Test User", "email": "testuser@example.com", "phone": "9999999999",
               "password": "SecurePass123", "language_pref": "en"}
    res = client.post("/api/auth/register", json=payload)
    return res, client