import pytest_asyncio
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.main import app
from app.database import Base, get_db

@pytest_asyncio.fixture
async def async_client():
    with TestClient(app) as client:
        yield client

@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///", echo=True,
        )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = sessionmaker(
        engine, 
        expire_on_commit=False, 
        class_=AsyncSession,
        )
    async with async_session() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def override_get_db(db_session):
    async def _override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()