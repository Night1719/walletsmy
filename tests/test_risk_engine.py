import pytest
from unittest.mock import AsyncMock, patch
from bot.risk_engine import RiskEngine, RiskCheckResult


@pytest.fixture
def risk_engine():
    return RiskEngine()


@pytest.fixture
def sample_jupiter_quote():
    return {
        "inAmount": "1000000000",  # 1 SOL
        "outAmount": "50000000000",  # 50 BONK
        "feePct": 0.3,
        "platformFee": 0.1,
        "priceImpactPct": 2.5
    }


class TestRiskEngine:
    
    @pytest.mark.asyncio
    async def test_check_trade_success(self, risk_engine, sample_jupiter_quote):
        """Тест успешной проверки сделки"""
        result = await risk_engine.check_trade(
            input_mint="So11111111111111111111111111111111111111112",
            output_mint="DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
            amount_usd=100.0,
            jupiter_quote=sample_jupiter_quote
        )
        
        assert isinstance(result, RiskCheckResult)
        assert result.passed is True
        assert result.score > 50
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_check_trade_low_liquidity(self, risk_engine):
        """Тест проверки с низкой ликвидностью"""
        low_liquidity_quote = {
            "inAmount": "1000000000",
            "outAmount": "50000000000",
            "feePct": 0.3,
            "platformFee": 0.1,
            "priceImpactPct": 2.5
        }
        
        # Мокаем настройки для низкой ликвидности
        risk_engine.min_tvl_usd = 1000000  # Очень высокий минимум
        
        result = await risk_engine.check_trade(
            input_mint="So11111111111111111111111111111111111111112",
            output_mint="DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
            amount_usd=100.0,
            jupiter_quote=low_liquidity_quote
        )
        
        assert result.passed is False
        assert "TVL too low" in result.errors[0]
    
    @pytest.mark.asyncio
    async def test_check_trade_high_fees(self, risk_engine):
        """Тест проверки с высокими комиссиями"""
        high_fee_quote = {
            "inAmount": "1000000000",
            "outAmount": "50000000000",
            "feePct": 5.0,  # 5% комиссия
            "platformFee": 2.0,  # 2% платформенная комиссия
            "priceImpactPct": 2.5
        }
        
        result = await risk_engine.check_trade(
            input_mint="So11111111111111111111111111111111111111112",
            output_mint="DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
            amount_usd=100.0,
            jupiter_quote=high_fee_quote
        )
        
        assert result.passed is False
        assert "fees too high" in result.errors[0].lower()
    
    @pytest.mark.asyncio
    async def test_check_trade_high_slippage(self, risk_engine):
        """Тест проверки с высоким проскальзыванием"""
        high_slippage_quote = {
            "inAmount": "1000000000",
            "outAmount": "50000000000",
            "feePct": 0.3,
            "platformFee": 0.1,
            "priceImpactPct": 10.0  # 10% проскальзывание
        }
        
        result = await risk_engine.check_trade(
            input_mint="So11111111111111111111111111111111111111112",
            output_mint="DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
            amount_usd=100.0,
            jupiter_quote=high_slippage_quote
        )
        
        assert result.passed is False
        assert "price impact too high" in result.errors[0].lower()
    
    @pytest.mark.asyncio
    async def test_check_liquidity(self, risk_engine, sample_jupiter_quote):
        """Тест проверки ликвидности"""
        result = await risk_engine._check_liquidity(sample_jupiter_quote, 100.0)
        
        assert result["passed"] is True
        assert result["reason"] is None
    
    @pytest.mark.asyncio
    async def test_check_fees(self, risk_engine, sample_jupiter_quote):
        """Тест проверки комиссий"""
        result = await risk_engine._check_fees(sample_jupiter_quote, 100.0)
        
        assert result["passed"] is True
        assert result["reason"] is None
    
    @pytest.mark.asyncio
    async def test_check_slippage(self, risk_engine, sample_jupiter_quote):
        """Тест проверки проскальзывания"""
        result = await risk_engine._check_slippage(sample_jupiter_quote)
        
        assert result["passed"] is True
        assert result["reason"] is None
    
    @pytest.mark.asyncio
    async def test_check_honeypot(self, risk_engine):
        """Тест проверки honeypot"""
        result = await risk_engine._check_honeypot("DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263")
        
        assert result["passed"] is True
        assert result["reason"] is None
    
    @pytest.mark.asyncio
    async def test_check_rugpull(self, risk_engine):
        """Тест проверки rugpull"""
        result = await risk_engine._check_rugpull("DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263")
        
        assert result["passed"] is True
        assert result["reason"] is None
    
    @pytest.mark.asyncio
    async def test_check_volatility(self, risk_engine, sample_jupiter_quote):
        """Тест проверки волатильности"""
        result = await risk_engine._check_volatility(sample_jupiter_quote)
        
        assert "warning" in result
    
    @pytest.mark.asyncio
    async def test_is_token_blacklisted(self, risk_engine):
        """Тест проверки черного списка токенов"""
        result = await risk_engine._is_token_blacklisted("DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_check_trade_exception_handling(self, risk_engine):
        """Тест обработки исключений"""
        # Передаем некорректные данные для вызова исключения
        result = await risk_engine.check_trade(
            input_mint="invalid",
            output_mint="invalid",
            amount_usd=-100.0,
            jupiter_quote={}
        )
        
        assert result.passed is False
        assert result.score == 0
        assert len(result.errors) > 0


class TestRiskCheckResult:
    
    def test_risk_check_result_creation(self):
        """Тест создания объекта RiskCheckResult"""
        result = RiskCheckResult(
            passed=True,
            score=85.5,
            warnings=["High fees"],
            errors=[],
            details={"test": "data"}
        )
        
        assert result.passed is True
        assert result.score == 85.5
        assert result.warnings == ["High fees"]
        assert result.errors == []
        assert result.details == {"test": "data"}
    
    def test_risk_check_result_failed(self):
        """Тест создания объекта RiskCheckResult для неудачной проверки"""
        result = RiskCheckResult(
            passed=False,
            score=25.0,
            warnings=[],
            errors=["Low liquidity", "High fees"],
            details={"test": "data"}
        )
        
        assert result.passed is False
        assert result.score == 25.0
        assert result.warnings == []
        assert len(result.errors) == 2
        assert "Low liquidity" in result.errors
        assert "High fees" in result.errors