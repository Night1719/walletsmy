from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
import structlog

logger = structlog.get_logger()
router = APIRouter()

@router.get("/pnl")
async def get_pnl(
    period: Optional[str] = Query("24h", description="Period: 24h, 7d, 30d, all"),
    strategy: Optional[str] = Query(None, description="Filter by strategy"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение P&L по периодам и стратегиям
    """
    try:
        # TODO: Реализовать получение P&L из БД
        # Пока возвращаем заглушку
        
        pnl_data = {
            "24h": {
                "total_pnl_usd": 234.12,
                "total_pnl_percent": 1.9,
                "trades_count": 15,
                "win_rate": 68.5,
                "by_strategy": {
                    "sniper": {"pnl_usd": 156.78, "trades": 8, "win_rate": 75.0},
                    "manual": {"pnl_usd": 77.34, "trades": 7, "win_rate": 57.1}
                }
            },
            "7d": {
                "total_pnl_usd": 1245.67,
                "total_pnl_percent": 11.2,
                "trades_count": 89,
                "win_rate": 71.9,
                "by_strategy": {
                    "sniper": {"pnl_usd": 892.45, "trades": 45, "win_rate": 77.8},
                    "manual": {"pnl_usd": 353.22, "trades": 44, "win_rate": 61.4}
                }
            },
            "30d": {
                "total_pnl_usd": 4567.89,
                "total_pnl_percent": 58.3,
                "trades_count": 342,
                "win_rate": 69.6,
                "by_strategy": {
                    "sniper": {"pnl_usd": 3245.67, "trades": 178, "win_rate": 73.0},
                    "manual": {"pnl_usd": 1322.22, "trades": 164, "win_rate": 64.6}
                }
            }
        }
        
        if period == "all":
            # Возвращаем все периоды
            return pnl_data
        elif period in pnl_data:
            # Возвращаем конкретный период
            period_data = pnl_data[period]
            
            # Фильтруем по стратегии если указана
            if strategy and strategy in period_data["by_strategy"]:
                return {
                    "period": period,
                    "strategy": strategy,
                    **period_data["by_strategy"][strategy]
                }
            
            return {
                "period": period,
                **period_data
            }
        else:
            return {
                "error": f"Invalid period: {period}. Use: 24h, 7d, 30d, all"
            }
        
    except Exception as e:
        logger.error("Error getting P&L", error=str(e))
        return {
            "error": f"Failed to get P&L data: {str(e)}"
        }

@router.get("/pnl/chart")
async def get_pnl_chart(
    period: str = Query("7d", description="Period: 24h, 7d, 30d"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение данных для графика P&L
    """
    try:
        # TODO: Реализовать получение данных для графика из БД
        # Пока возвращаем заглушку
        
        chart_data = {
            "7d": {
                "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                "cumulative_pnl": [0, 156.78, 234.12, 456.78, 789.12, 1023.45, 1245.67],
                "daily_pnl": [0, 156.78, 77.34, 222.66, 332.34, 234.33, 222.22]
            },
            "30d": {
                "labels": [f"Day {i+1}" for i in range(30)],
                "cumulative_pnl": [0] + [i * 150 for i in range(1, 31)],
                "daily_pnl": [0] + [150 for _ in range(29)]
            }
        }
        
        if period in chart_data:
            return chart_data[period]
        else:
            return {
                "error": f"Invalid period: {period}. Use: 24h, 7d, 30d"
            }
        
    except Exception as e:
        logger.error("Error getting P&L chart data", error=str(e))
        return {
            "error": f"Failed to get P&L chart data: {str(e)}"
        }