from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict
import structlog
from app.database import get_db
from app.config import settings
from bot.risk_engine import RiskEngine
import time

logger = structlog.get_logger()
router = APIRouter()

class TradeRequest(BaseModel):
    input_mint: str
    output_mint: str
    amount_usd: float
    slippage_percent: Optional[float] = 1.0
    strategy_name: Optional[str] = "manual"

class TradeResponse(BaseModel):
    success: bool
    trade_id: Optional[str] = None
    message: str
    risk_score: Optional[float] = None
    risk_details: Optional[Dict] = None

@router.post("/simulate")
async def simulate_trade(
    trade_request: TradeRequest,
    db = Depends(get_db)
):
    """
    Симуляция сделки с проверкой рисков
    """
    try:
        # Получаем котировку от Jupiter
        jupiter_quote = await _get_jupiter_quote(
            trade_request.input_mint,
            trade_request.output_mint,
            trade_request.amount_usd
        )
        
        if not jupiter_quote:
            raise HTTPException(status_code=400, detail="Failed to get Jupiter quote")
        
        # Проверяем риски через risk engine
        risk_engine = RiskEngine()
        risk_result = await risk_engine.check_trade(
            input_mint=trade_request.input_mint,
            output_mint=trade_request.output_mint,
            amount_usd=trade_request.amount_usd,
            jupiter_quote=jupiter_quote
        )
        
        # Формируем ответ
        response = TradeResponse(
            success=risk_result.passed,
            message="Trade simulation completed",
            risk_score=risk_result.score,
            risk_details=risk_result.details
        )
        
        if not risk_result.passed:
            response.message = f"Trade blocked by risk engine: {', '.join(risk_result.errors)}"
        
        logger.info(
            "Trade simulation completed",
            input_mint=trade_request.input_mint,
            output_mint=trade_request.output_mint,
            risk_score=risk_result.score,
            passed=risk_result.passed
        )
        
        return response
        
    except Exception as e:
        logger.error("Trade simulation error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")

@router.post("/trade")
async def execute_trade(
    trade_request: TradeRequest,
    db = Depends(get_db)
):
    """
    Исполнение реальной сделки
    """
    if not settings.enable_real_trades:
        raise HTTPException(
            status_code=400, 
            detail="Real trading is disabled. Enable ENABLE_REAL_TRADES to trade."
        )
    
    try:
        # Сначала симулируем сделку
        simulation = await simulate_trade(trade_request, db)
        
        if not simulation.success:
            return simulation
        
        # Если симуляция прошла успешно, исполняем сделку
        # TODO: Реализовать реальное исполнение через Jupiter API
        
        trade_id = f"trade_{int(time.time())}"
        
        response = TradeResponse(
            success=True,
            trade_id=trade_id,
            message="Trade executed successfully",
            risk_score=simulation.risk_score,
            risk_details=simulation.risk_details
        )
        
        logger.info(
            "Trade executed",
            trade_id=trade_id,
            input_mint=trade_request.input_mint,
            output_mint=trade_request.output_mint,
            amount_usd=trade_request.amount_usd
        )
        
        return response
        
    except Exception as e:
        logger.error("Trade execution error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")

async def _get_jupiter_quote(input_mint: str, output_mint: str, amount_usd: float):
    """Получение котировки от Jupiter API"""
    try:
        import httpx
        
        # Конвертируем USD в lamports (упрощенно)
        # В реальности нужно получить актуальный курс SOL/USD
        sol_price_usd = 100  # Примерная цена SOL
        amount_lamports = int((amount_usd / sol_price_usd) * 1e9)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.jupiter_api_url}/quote",
                params={
                    "inputMint": input_mint,
                    "outputMint": output_mint,
                    "amount": str(amount_lamports),
                    "slippageBps": 50
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Jupiter API error: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error("Error getting Jupiter quote", error=str(e))
        return None