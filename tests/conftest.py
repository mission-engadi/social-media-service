"""Shared test fixtures for Social Media Service tests."""
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.db.base_class import Base
from app.db.session import get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.models.social_account import SocialAccount
from app.models.scheduled_post import ScheduledPost
from app.models.campaign import Campaign
from app.models.buffer_config import BufferConfig

# Test database URL
TEST_DATABASE_URL = settings.DATABASE_URL.replace("social_media_db", "social_media_test_db")

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)

TestAsyncSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async with TestAsyncSessionLocal() as session:
        yield session
        await session.rollback()

    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database session override."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_token() -> str:
    """Create test user JWT token."""
    return create_access_token(
        data={"sub": "test_user_123", "email": "test@example.com"}
    )


@pytest.fixture
def auth_headers(test_user_token: str) -> dict:
    """Create authorization headers."""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest_asyncio.fixture
async def test_social_account(db_session: AsyncSession) -> SocialAccount:
    """Create test social account."""
    account = SocialAccount(
        user_id="test_user_123",
        platform="twitter",
        account_name="@testuser",
        buffer_profile_id="buf_profile_123",
        access_token="test_token",
        is_active=True
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest_asyncio.fixture
async def test_campaign(db_session: AsyncSession) -> Campaign:
    """Create test campaign."""
    campaign = Campaign(
        user_id="test_user_123",
        name="Test Campaign",
        description="Test campaign description",
        start_date="2025-01-01",
        end_date="2025-12-31",
        status="active"
    )
    db_session.add(campaign)
    await db_session.commit()
    await db_session.refresh(campaign)
    return campaign


@pytest_asyncio.fixture
async def test_scheduled_post(
    db_session: AsyncSession,
    test_social_account: SocialAccount,
    test_campaign: Campaign
) -> ScheduledPost:
    """Create test scheduled post."""
    post = ScheduledPost(
        user_id="test_user_123",
        social_account_id=test_social_account.id,
        campaign_id=test_campaign.id,
        content="Test post content",
        scheduled_time="2025-12-25T10:00:00",
        status="draft",
        platform="twitter"
    )
    db_session.add(post)
    await db_session.commit()
    await db_session.refresh(post)
    return post


@pytest_asyncio.fixture
async def test_buffer_config(db_session: AsyncSession) -> BufferConfig:
    """Create test buffer configuration."""
    config = BufferConfig(
        user_id="test_user_123",
        access_token="test_buffer_token",
        is_active=True
    )
    db_session.add(config)
    await db_session.commit()
    await db_session.refresh(config)
    return config
