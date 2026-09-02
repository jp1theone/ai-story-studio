"""Configuracion de Celery para tareas async (opcional — se puede usar BackgroundTasks de FastAPI)."""
from celery import Celery

from backend.config import settings

celery = Celery("ai_story_studio", broker=settings.redis_url, backend=settings.redis_url)
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)