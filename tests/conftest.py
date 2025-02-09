"""Test configuration and fixtures."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from contextlib import contextmanager
from src.database import Base, get_db
from src.models import DBGardenBed, DBPlant, DBPlantImage  # Import all models
from main import app
import os

# Use PostgreSQL test database
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

@pytest.fixture(scope="function")
def engine():
    """Create a fresh database engine for each test."""
    test_engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Base.metadata.drop_all(bind=test_engine)  # Clean before creating
    Base.metadata.create_all(bind=test_engine)  # Create all tables
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def session_factory(engine):
    """Create a session factory bound to the test engine."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return TestingSessionLocal

@pytest.fixture(scope="function")
def test_db(session_factory):
    """Provide a test database session."""
    def override_get_db():
        session = session_factory()
        try:
            Base.metadata.create_all(bind=session.get_bind())  # Ensure tables exist
            yield session
            session.commit()  # Commit changes within the test
        except:
            session.rollback()
            raise
        finally:
            session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    session = session_factory()
    Base.metadata.create_all(bind=session.get_bind())  # Ensure tables exist at fixture setup
    
    yield session
    
    session.close()
    # Clear the override after the test
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def client(test_db):
    """Provide a test client with a fresh database."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
def mock_storage():
    """Mock storage for file uploads."""
    class MockStorage:
        def __init__(self):
            self.files = {}
            
        def save(self, file_name, content):
            self.files[file_name] = content
            return f"http://example.com/images/{file_name}"
            
        def get(self, file_name):
            return self.files.get(file_name)
    
    return MockStorage()