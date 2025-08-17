from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
import time
import structlog

from app.database import get_db
from app.config import settings

logger = structlog.get_logger()
router = APIRouter()

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Проверка здоровья всех компонентов системы
    """
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "components": {}
    }
    
    # Проверка базы данных
    try:
        await db.execute("SELECT 1")
        health_status["components"]["database"] = "healthy"
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        health_status["components"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
    
    # Проверка Solana RPC
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                get_solana_rpc_url(),
                json={"jsonrpc": "2.0", "id": 1, "method": "getHealth"},
                timeout=5.0
            )
            if response.status_code == 200:
                health_status["components"]["solana_rpc"] = "healthy"
            else:
                health_status["components"]["solana_rpc"] = "unhealthy"
                health_status["status"] = "degraded"
    except Exception as e:
        logger.error("Solana RPC health check failed", error=str(e))
        health_status["components"]["solana_rpc"] = "unhealthy"
        health_status["status"] = "degraded"
    
    # Проверка Jupiter API
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.jupiter_api_url}/v6/quote",
                params={"inputMint": "So11111111111111111111111111111111111111112", "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "amount": "1000000"},
                timeout=5.0
            )
            if response.status_code == 200:
                health_status["components"]["jupiter_api"] = "healthy"
            else:
                health_status["components"]["jupiter_api"] = "unhealthy"
                health_status["status"] = "degraded"
    except Exception as e:
        logger.error("Jupiter API health check failed", error=str(e))
        health_status["components"]["jupiter_api"] = "unhealthy"
        health_status["status"] = "degraded"
    
    # Проверка Redis
    try:
        import redis
        r = redis.from_url(settings.redis_url)
        r.ping()
        health_status["components"]["redis"] = "healthy"
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
        health_status["components"]["redis"] = "unhealthy"
        health_status["status"] = "degraded"
    
    return health_status

def get_solana_rpc_url():
    """Получение URL для Solana RPC в зависимости от сети"""
    return settings.solana_devnet_rpc_url if settings.solana_network.lower() == "devnet" else settings.solana_rpc_url