
from fastapi import FastAPI
from app.database import init_db
from contextlib import asynccontextmanager
from app.router import router

# Создаем асинхронный контекстный менеджер для управления жизненным циклом приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация базы данных на старте
    await init_db()
    print("Database initialized")
    yield

app = FastAPI(lifespan=lifespan)

# Добавляем маршруты

app.include_router(router)