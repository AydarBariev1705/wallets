from celery import Celery
from app.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
celery_app = Celery(
    "worker",
    broker=CELERY_BROKER_URL,  # URL для Redis
    backend=CELERY_RESULT_BACKEND,  # URL для Redis (для хранения результатов)
    include=["app.tasks"],  # Указываем модуль с задачами
)

celery_app.conf.update(
    result_expires=3600,  # Время жизни результатов (в секундах)
)