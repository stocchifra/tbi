"""
Test configuration for pytest
"""
import pytest
import pytest_asyncio
import asyncio
import sys
import os
from typing import Generator
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
from app.models.database import Base, get_db_session
from app.utils.config import get_settings

# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
test_engine = create_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Initialize tables once for the entire test session
@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Set up test database tables for the entire test session"""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


def override_get_db_session():
    """Override database dependency for testing"""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test"""
    # Provide session (tables already created by setup_test_database)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Clean up data but keep tables
        session = TestSessionLocal()
        try:
            for table in reversed(Base.metadata.sorted_tables):
                session.execute(table.delete())
            session.commit()
        finally:
            session.close()


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    """Create test client with database override"""
    app.dependency_overrides[get_db_session] = override_get_db_session
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    return {
        "choices": [
            {
                "message": {
                    "content": "This is a test response from the AI assistant.",
                    "role": "assistant"
                }
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    }
