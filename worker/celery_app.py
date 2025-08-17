from celery import Celery
from app.config import settings
import structlog

logger = structlog.get_logger()

# Создание Celery приложения
celery_app = Celery(
    "trading_bot",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "worker.tasks.market_scan",
        "worker.tasks.trade_execution",
        "worker.tasks.alerts",
        "worker.tasks.analytics"
    ]
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    task_soft_time_limit=25 * 60,  # 25 минут
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    broker_connection_retry_on_startup=True,
    result_expires=3600,  # 1 час
)

# Автоматическое обнаружение задач
celery_app.autodiscover_tasks()

@celery_app.task(bind=True)
def debug_task(self):
    """Тестовая задача для проверки работы Celery"""
    logger.info(f"Request: {self.request!r}")
    return "Debug task completed"

if __name__ == "__main__":
    celery_app.start()