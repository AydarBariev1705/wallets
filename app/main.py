from fastapi import FastAPI
from app.router import router
from app.database import init_db

app = FastAPI()

app.include_router(router)

@app.on_event("startup")
async def on_startup():
    await init_db()