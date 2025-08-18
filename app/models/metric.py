from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.sql import func
from app.database import Base


class MetricSnapshot(Base):
    __tablename__ = "metric_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Временная метка
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Основные метрики
    portfolio_value_usd = Column(Float, nullable=False)
    total_pnl_usd = Column(Float, default=0.0)
    daily_pnl_usd = Column(Float, default=0.0)
    
    # Статистика торговли
    total_trades = Column(Integer, default=0)
    successful_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    
    # Активные позиции
    open_positions_count = Column(Integer, default=0)
    total_positions_value_usd = Column(Float, default=0.0)
    
    # Риски
    risk_score = Column(Float, default=100.0)
    blocked_trades_count = Column(Integer, default=0)
    
    # Системные метрики
    rpc_latency_ms = Column(Float, nullable=True)
    jupiter_api_latency_ms = Column(Float, nullable=True)
    
    # Дополнительные данные (JSON)
    extra_data = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<MetricSnapshot(id={self.id}, timestamp='{self.timestamp}', portfolio_value=${self.portfolio_value_usd})>"