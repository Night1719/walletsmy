import asyncio
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
import httpx
import structlog
from app.config import settings
from bot.risk_engine import RiskEngine

logger = structlog.get_logger()

@dataclass
class NewTokenAlert:
    """Алерт о новом токене"""
    token_mint: str
    token_name: str
    token_symbol: str
    pool_address: str
    initial_liquidity_usd: float
    timestamp: float
    risk_score: float
    risk_details: Dict


class SniperBot:
    """Снайпер-бот для мониторинга новых токенов"""
    
    def __init__(self):
        self.risk_engine = RiskEngine()
        self.is_running = False
        self.monitored_tokens = set()
        self.alert_callbacks: List[Callable] = []
        
        # Настройки из конфигурации
        self.min_liquidity_usd = settings.sniper_min_liquidity_usd
        self.max_slippage_percent = settings.sniper_max_slippage_percent
        self.quick_exit_percent = settings.sniper_quick_exit_percent
        
        # Кеш для предотвращения дублирования
        self.recent_alerts = {}
        self.alert_cooldown = 300  # 5 минут
    
    async def start(self):
        """Запуск снайпер-бота"""
        if self.is_running:
            logger.warning("Sniper bot is already running")
            return
        
        self.is_running = True
        logger.info("Starting sniper bot...")
        
        try:
            while self.is_running:
                await self._scan_new_tokens()
                await asyncio.sleep(10)  # Сканируем каждые 10 секунд
        except Exception as e:
            logger.error("Sniper bot error", error=str(e))
            self.is_running = False
            raise
    
    async def stop(self):
        """Остановка снайпер-бота"""
        self.is_running = False
        logger.info("Sniper bot stopped")
    
    def add_alert_callback(self, callback: Callable[[NewTokenAlert], None]):
        """Добавление callback для алертов"""
        self.alert_callbacks.append(callback)
    
    async def _scan_new_tokens(self):
        """Сканирование новых токенов"""
        try:
            # Получаем список новых пулов через Jupiter API
            new_pools = await self._get_new_pools()
            
            for pool in new_pools:
                await self._analyze_pool(pool)
                
        except Exception as e:
            logger.error("Error scanning new tokens", error=str(e))
    
    async def _get_new_pools(self) -> List[Dict]:
        """Получение списка новых пулов"""
        try:
            # TODO: Реализовать получение новых пулов через Jupiter API
            # Пока возвращаем пустой список
            return []
            
        except Exception as e:
            logger.error("Error getting new pools", error=str(e))
            return []
    
    async def _analyze_pool(self, pool_data: Dict):
        """Анализ нового пула"""
        try:
            token_mint = pool_data.get("tokenMint")
            if not token_mint or token_mint in self.monitored_tokens:
                return
            
            # Проверяем, не было ли недавно алерта по этому токену
            if self._is_recent_alert(token_mint):
                return
            
            # Получаем детали токена
            token_info = await self._get_token_info(token_mint)
            if not token_info:
                return
            
            # Проверяем ликвидность
            liquidity_usd = pool_data.get("liquidityUsd", 0)
            if liquidity_usd < self.min_liquidity_usd:
                logger.debug(f"Token {token_mint} liquidity too low: ${liquidity_usd}")
                return
            
            # Получаем Jupiter quote для анализа
            jupiter_quote = await self._get_jupiter_quote(token_mint)
            if not jupiter_quote:
                return
            
            # Проверяем риски через risk engine
            risk_result = await self.risk_engine.check_trade(
                input_mint="So11111111111111111111111111111111111111112",  # SOL
                output_mint=token_mint,
                amount_usd=100,  # Тестовая сумма $100
                jupiter_quote=jupiter_quote
            )
            
            # Создаем алерт
            alert = NewTokenAlert(
                token_mint=token_mint,
                token_name=token_info.get("name", "Unknown"),
                token_symbol=token_info.get("symbol", "UNKNOWN"),
                pool_address=pool_data.get("poolAddress", ""),
                initial_liquidity_usd=liquidity_usd,
                timestamp=time.time(),
                risk_score=risk_result.score,
                risk_details=risk_result.details
            )
            
            # Отправляем алерт
            await self._send_alert(alert)
            
            # Добавляем в отслеживаемые
            self.monitored_tokens.add(token_mint)
            
        except Exception as e:
            logger.error(f"Error analyzing pool {pool_data.get('poolAddress', 'unknown')}", error=str(e))
    
    async def _get_token_info(self, token_mint: str) -> Optional[Dict]:
        """Получение информации о токене"""
        try:
            # TODO: Реализовать получение информации через Solana RPC
            # Пока возвращаем базовую информацию
            return {
                "name": f"Token_{token_mint[:8]}",
                "symbol": f"TKN_{token_mint[:4]}",
                "decimals": 9
            }
            
        except Exception as e:
            logger.error(f"Error getting token info for {token_mint}", error=str(e))
            return None
    
    async def _get_jupiter_quote(self, token_mint: str) -> Optional[Dict]:
        """Получение котировки Jupiter для токена"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.jupiter_api_url}/quote",
                    params={
                        "inputMint": "So11111111111111111111111111111111111111112",  # SOL
                        "outputMint": token_mint,
                        "amount": "1000000000",  # 1 SOL
                        "slippageBps": int(self.max_slippage_percent * 100)
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Jupiter API error for {token_mint}: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting Jupiter quote for {token_mint}", error=str(e))
            return None
    
    def _is_recent_alert(self, token_mint: str) -> bool:
        """Проверка, был ли недавно алерт по этому токену"""
        current_time = time.time()
        if token_mint in self.recent_alerts:
            if current_time - self.recent_alerts[token_mint] < self.alert_cooldown:
                return True
        
        self.recent_alerts[token_mint] = current_time
        return False
    
    async def _send_alert(self, alert: NewTokenAlert):
        """Отправка алерта"""
        try:
            logger.info(
                "New token alert",
                token_mint=alert.token_mint,
                token_name=alert.token_name,
                liquidity_usd=alert.initial_liquidity_usd,
                risk_score=alert.risk_score
            )
            
            # Вызываем все callback'и
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"Error in alert callback", error=str(e))
            
            # TODO: Отправка уведомлений через Telegram/Discord/Email
            
        except Exception as e:
            logger.error("Error sending alert", error=str(e))
    
    async def auto_trade_new_token(self, alert: NewTokenAlert, amount_usd: float):
        """Автоматическая торговля новым токеном"""
        try:
            if alert.risk_score < 70:  # Минимальный риск-скор для автоматической торговли
                logger.warning(f"Token {alert.token_mint} risk score too low: {alert.risk_score}")
                return False
            
            # TODO: Реализовать автоматическую покупку через Jupiter API
            logger.info(f"Auto-trading {amount_usd} USD for token {alert.token_mint}")
            
            # Симуляция сделки
            success = await self._execute_auto_trade(alert, amount_usd)
            
            if success:
                logger.info(f"Auto-trade successful for {alert.token_mint}")
                # TODO: Установить stop-loss и take-profit
                await self._set_exit_orders(alert, amount_usd)
            
            return success
            
        except Exception as e:
            logger.error(f"Auto-trade error for {alert.token_mint}", error=str(e))
            return False
    
    async def _execute_auto_trade(self, alert: NewTokenAlert, amount_usd: float) -> bool:
        """Исполнение автоматической сделки"""
        try:
            # TODO: Реализовать реальную сделку через Jupiter API
            # Пока симулируем успех
            await asyncio.sleep(1)  # Симуляция задержки
            return True
            
        except Exception as e:
            logger.error(f"Error executing auto-trade", error=str(e))
            return False
    
    async def _set_exit_orders(self, alert: NewTokenAlert, amount_usd: float):
        """Установка ордеров на выход"""
        try:
            # TODO: Реализовать установку stop-loss и take-profit
            logger.info(f"Setting exit orders for {alert.token_mint}")
            
        except Exception as e:
            logger.error(f"Error setting exit orders", error=str(e))