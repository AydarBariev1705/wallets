from celery import Celery

from app.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery_app = Celery(
    "worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.tasks"],
)

celery_app.conf.update(
    result_expires=3600,
)