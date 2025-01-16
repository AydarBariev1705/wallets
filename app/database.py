from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.config import POSTGRES_CONN
engine = create_async_engine(
    POSTGRES_CONN, 
    echo=True,
    )
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)