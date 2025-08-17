from fastapi import APIRouter
from fastapi.responses import Response
import prometheus_client
import structlog

logger = structlog.get_logger()
router = APIRouter()

@router.get("/metrics")
async def get_metrics():
    """
    Возвращает метрики в формате Prometheus
    """
    try:
        # Собираем все метрики
        metrics_data = prometheus_client.generate_latest()
        return Response(content=metrics_data, media_type="text/plain")
    except Exception as e:
        logger.error("Failed to generate metrics", error=str(e))
        return Response(content="", media_type="text/plain")