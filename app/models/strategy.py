from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class StrategyConfig(Base):
    __tablename__ = "strategy_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Основная информация
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    strategy_type = Column(String(50), nullable=False)  # sniper, arbitrage, momentum, mean_reversion
    
    # Настройки стратегии
    is_active = Column(Boolean, default=True)
    is_paper_trading = Column(Boolean, default=True)
    
    # Параметры стратегии (JSON)
    parameters = Column(JSON, nullable=True)
    
    # Лимиты риска
    max_position_size_usd = Column(Float, default=1000.0)
    max_daily_loss_usd = Column(Float, default=100.0)
    stop_loss_percent = Column(Float, default=10.0)
    take_profit_percent = Column(Float, default=20.0)
    
    # Фильтры токенов
    min_liquidity_usd = Column(Float, default=10000.0)
    max_slippage_percent = Column(Float, default=5.0)
    allowed_tokens = Column(JSON, nullable=True)  # Список разрешенных токенов
    blocked_tokens = Column(JSON, nullable=True)  # Список заблокированных токенов
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_executed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Статистика
    total_trades = Column(Integer, default=0)
    successful_trades = Column(Integer, default=0)
    total_pnl_usd = Column(Float, default=0.0)
    
    def __repr__(self):
        return f"<StrategyConfig(id={self.id}, name='{self.name}', type='{self.strategy_type}')>"