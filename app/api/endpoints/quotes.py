from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import httpx
import structlog
from app.config import settings

logger = structlog.get_logger()
router = APIRouter()

@router.get("/quotes")
async def get_quotes(
    input_mint: str = Query(..., description="Input token mint address"),
    output_mint: str = Query(..., description="Output token mint address"),
    amount: str = Query(..., description="Amount in lamports"),
    slippage_bps: Optional[int] = Query(50, description="Slippage in basis points")
):
    """
    Получение котировки для обмена токенов через Jupiter API
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.jupiter_api_url}/quote",
                params={
                    "inputMint": input_mint,
                    "outputMint": output_mint,
                    "amount": amount,
                    "slippageBps": slippage_bps
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                quote_data = response.json()
                logger.info(
                    "Jupiter quote retrieved",
                    input_mint=input_mint,
                    output_mint=output_mint,
                    amount=amount
                )
                return quote_data
            else:
                logger.error(
                    "Jupiter API error",
                    status_code=response.status_code,
                    response_text=response.text
                )
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Jupiter API error: {response.text}"
                )
                
    except httpx.TimeoutException:
        logger.error("Jupiter API timeout")
        raise HTTPException(status_code=408, detail="Jupiter API timeout")
    except Exception as e:
        logger.error("Error getting Jupiter quote", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/tokens")
async def get_tokens():
    """
    Получение списка поддерживаемых токенов
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.jupiter_api_url}/tokens",
                timeout=10.0
            )
            
            if response.status_code == 200:
                tokens_data = response.json()
                logger.info("Jupiter tokens retrieved")
                return tokens_data
            else:
                logger.error(
                    "Jupiter tokens API error",
                    status_code=response.status_code
                )
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to retrieve tokens"
                )
                
    except Exception as e:
        logger.error("Error getting Jupiter tokens", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")