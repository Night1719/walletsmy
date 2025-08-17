from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
import structlog

logger = structlog.get_logger()
router = APIRouter()

@router.get("/positions")
async def get_positions(db: AsyncSession = Depends(get_db)):
    """
    Получение списка активных позиций
    """
    try:
        # TODO: Реализовать получение позиций из БД
        # Пока возвращаем заглушку
        
        positions = [
            {
                "id": 1,
                "token_mint": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
                "token_name": "BONK",
                "token_symbol": "BONK",
                "amount": 1000000,
                "entry_price_usd": 0.000001,
                "current_price_usd": 0.0000012,
                "pnl_usd": 0.20,
                "pnl_percent": 20.0,
                "strategy": "sniper",
                "entry_time": "2024-01-15T10:30:00Z"
            },
            {
                "id": 2,
                "token_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                "token_name": "USD Coin",
                "token_symbol": "USDC",
                "amount": 100000000,
                "entry_price_usd": 1.0,
                "current_price_usd": 1.0,
                "pnl_usd": 0.0,
                "pnl_percent": 0.0,
                "strategy": "manual",
                "entry_time": "2024-01-14T15:45:00Z"
            }
        ]
        
        return {
            "positions": positions,
            "total_count": len(positions),
            "total_value_usd": 100.20
        }
        
    except Exception as e:
        logger.error("Error getting positions", error=str(e))
        return {
            "positions": [],
            "total_count": 0,
            "total_value_usd": 0.0
        }