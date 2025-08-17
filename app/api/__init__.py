from fastapi import APIRouter
from app.api.endpoints import health, metrics, quotes, trading, positions, pnl

api_router = APIRouter()

# Подключаем все эндпоинты
api_router.include_router(health.router, tags=["health"])
api_router.include_router(metrics.router, tags=["metrics"])
api_router.include_router(quotes.router, tags=["quotes"])
api_router.include_router(trading.router, tags=["trading"])
api_router.include_router(positions.router, tags=["positions"])
api_router.include_router(pnl.router, tags=["pnl"])