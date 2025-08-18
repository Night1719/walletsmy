from typing import Dict, List
from dataclasses import dataclass
import structlog
from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.system_settings import SystemSettings

logger = structlog.get_logger()


@dataclass
class RiskCheckResult:
    """Результат проверки risk engine"""
    passed: bool
    score: float  # 0-100
    warnings: List[str]
    errors: List[str]
    details: Dict


class RiskEngine:
    """Движок проверки рисков для торговых сделок"""

    def __init__(self, dynamic: bool = True):
        # Значения по умолчанию из env
        self.min_tvl_usd = settings.min_tvl_usd
        self.max_fee_percent = settings.max_fee_percent
        self.enable_honeypot_check = settings.enable_honeypot_check
        self.enable_rugpull_check = settings.enable_rugpull_check
        self.max_tax_percent = settings.max_tax_percent
        self.max_slippage_percent = getattr(settings, "max_slippage_percent", 1.0)
        self._dynamic = dynamic

    async def _maybe_load_db_settings(self) -> None:
        if not self._dynamic:
            return
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(SystemSettings).order_by(SystemSettings.id.asc()).limit(1)
                )
                row = result.scalar_one_or_none()
                if row:
                    self.min_tvl_usd = row.min_tvl_usd
                    self.max_fee_percent = row.max_fee_percent
                    self.enable_honeypot_check = row.enable_honeypot_check
                    self.enable_rugpull_check = row.enable_rugpull_check
                    self.max_tax_percent = row.max_tax_percent
                    self.max_slippage_percent = row.max_slippage_percent
        except Exception:
            # Молча используем env-настройки при ошибке
            pass

    async def check_trade(
        self,
        input_mint: str,
        output_mint: str,
        amount_usd: float,
        jupiter_quote: Dict,
    ) -> RiskCheckResult:
        """
        Полная проверка сделки на риски
        """
        warnings: List[str] = []
        errors: List[str] = []
        score = 100.0

        try:
            # загрузка актуальных настроек из БД (если включено)
            await self._maybe_load_db_settings()

            # 1. Проверка ликвидности
            liquidity_check = await self._check_liquidity(jupiter_quote, amount_usd)
            if not liquidity_check["passed"]:
                errors.append(liquidity_check["reason"])
                score -= 30
            elif liquidity_check["warning"]:
                warnings.append(liquidity_check["warning"])
                score -= 10

            # 2. Проверка комиссий
            fee_check = await self._check_fees(jupiter_quote, amount_usd)
            if not fee_check["passed"]:
                errors.append(fee_check["reason"])
                score -= 25
            elif fee_check["warning"]:
                warnings.append(fee_check["warning"])
                score -= 5

            # 3. Проверка проскальзывания
            slippage_check = await self._check_slippage(jupiter_quote)
            if not slippage_check["passed"]:
                errors.append(slippage_check["reason"])
                score -= 20
            elif slippage_check["warning"]:
                warnings.append(slippage_check["warning"])
                score -= 5

            # 4. Проверка на honeypot (если включено)
            if self.enable_honeypot_check:
                honeypot_check = await self._check_honeypot(output_mint)
                if not honeypot_check["passed"]:
                    errors.append(honeypot_check["reason"])
                    score -= 40
                elif honeypot_check["warning"]:
                    warnings.append(honeypot_check["warning"])
                    score -= 15
            else:
                honeypot_check = {"passed": True, "reason": None, "warning": None}

            # 5. Проверка на rugpull (если включено)
            if self.enable_rugpull_check:
                rugpull_check = await self._check_rugpull(output_mint)
                if not rugpull_check["passed"]:
                    errors.append(rugpull_check["reason"])
                    score -= 35
                elif rugpull_check["warning"]:
                    warnings.append(rugpull_check["warning"])
                    score -= 10
            else:
                rugpull_check = {"passed": True, "reason": None, "warning": None}

            # 6. Проверка волатильности (плейсхолдер)
            volatility_check = await self._check_volatility(jupiter_quote)
            if volatility_check["warning"]:
                warnings.append(volatility_check["warning"])
                score -= 5

            # Финальная оценка
            score = max(0, score)
            passed = score >= 50 and len(errors) == 0

            return RiskCheckResult(
                passed=passed,
                score=score,
                warnings=warnings,
                errors=errors,
                details={
                    "liquidity_check": liquidity_check,
                    "fee_check": fee_check,
                    "slippage_check": slippage_check,
                    "honeypot_check": honeypot_check if self.enable_honeypot_check else None,
                    "rugpull_check": rugpull_check if self.enable_rugpull_check else None,
                    "volatility_check": volatility_check,
                },
            )

        except Exception as e:
            logger.error("Risk check failed", error=str(e))
            return RiskCheckResult(
                passed=False,
                score=0,
                warnings=[],
                errors=[f"Risk check error: {str(e)}"],
                details={},
            )

    async def _check_liquidity(self, jupiter_quote: Dict, amount_usd: float) -> Dict:
        """Проверка ликвидности пула"""
        try:
            in_amount = float(jupiter_quote.get("inAmount", 0))
            # Упрощенная оценка TVL
            estimated_tvl = in_amount * 2

            if estimated_tvl < self.min_tvl_usd:
                return {
                    "passed": False,
                    "reason": f"Pool TVL too low: ${estimated_tvl:.2f} < ${self.min_tvl_usd}",
                    "warning": None,
                }

            # Проверка глубины пула для нашей суммы
            if amount_usd > estimated_tvl * 0.1:  # Не более 10% от TVL
                return {
                    "passed": True,
                    "reason": None,
                    "warning": f"Trade size ({amount_usd:.2f}) is {amount_usd/estimated_tvl*100:.1f}% of pool TVL",
                }

            return {"passed": True, "reason": None, "warning": None}

        except Exception as e:
            logger.error("Liquidity check failed", error=str(e))
            return {"passed": False, "reason": f"Liquidity check error: {str(e)}", "warning": None}

    async def _check_fees(self, jupiter_quote: Dict, amount_usd: float) -> Dict:
        """Проверка комиссий"""
        try:
            fee_pct = float(jupiter_quote.get("feePct", 0))
            platform_fee = float(jupiter_quote.get("platformFee", 0))
            total_fee_pct = fee_pct + platform_fee

            if total_fee_pct > self.max_fee_percent:
                return {
                    "passed": False,
                    "reason": f"Total fees too high: {total_fee_pct:.2f}% > {self.max_fee_percent}%",
                    "warning": None,
                }

            fee_usd = amount_usd * total_fee_pct / 100
            if fee_usd > amount_usd * 0.05:
                return {
                    "passed": True,
                    "reason": None,
                    "warning": f"High fees: ${fee_usd:.2f} ({total_fee_pct:.2f}% of trade amount)",
                }

            return {"passed": True, "reason": None, "warning": None}

        except Exception as e:
            logger.error("Fee check failed", error=str(e))
            return {"passed": False, "reason": f"Fee check error: {str(e)}", "warning": None}

    async def _check_slippage(self, jupiter_quote: Dict) -> Dict:
        """Проверка проскальзывания"""
        try:
            price_impact = float(jupiter_quote.get("priceImpactPct", 0))

            if price_impact > self.max_slippage_percent:
                return {
                    "passed": False,
                    "reason": f"Price impact too high: {price_impact:.2f}% > {self.max_slippage_percent}%",
                    "warning": None,
                }

            if price_impact > self.max_slippage_percent * 0.7:
                return {
                    "passed": True,
                    "reason": None,
                    "warning": f"High price impact: {price_impact:.2f}%",
                }

            return {"passed": True, "reason": None, "warning": None}

        except Exception as e:
            logger.error("Slippage check failed", error=str(e))
            return {"passed": False, "reason": f"Slippage check error: {str(e)}", "warning": None}

    async def _check_honeypot(self, token_mint: str) -> Dict:
        """Проверка на honeypot токен"""
        try:
            # TODO: Реальная проверка через RPC и tiny swap
            return {"passed": True, "reason": None, "warning": None}
        except Exception as e:
            logger.error("Honeypot check failed", error=str(e))
            return {"passed": False, "reason": f"Honeypot check error: {str(e)}", "warning": None}

    async def _check_rugpull(self, token_mint: str) -> Dict:
        """Проверка на rugpull"""
        try:
            # TODO: Проверка mint/freeze authority, налоги и др.
            return {"passed": True, "reason": None, "warning": None}
        except Exception as e:
            logger.error("Rugpull check failed", error=str(e))
            return {"passed": False, "reason": f"Rugpull check error: {str(e)}", "warning": None}

    async def _check_volatility(self, jupiter_quote: Dict) -> Dict:
        """Проверка волатильности (плейсхолдер)"""
        try:
            return {"warning": None}
        except Exception as e:
            logger.error("Volatility check failed", error=str(e))
            return {"warning": f"Volatility check error: {str(e)}"}