
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.router import router
from app.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(router)