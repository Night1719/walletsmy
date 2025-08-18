from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Основная информация о сделке
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    strategy_name = Column(String(100), nullable=False)
    trade_type = Column(String(10), nullable=False)  # buy, sell
    status = Column(String(20), default="pending")  # pending, executed, failed, cancelled
    
    # Токены
    input_mint = Column(String(44), nullable=False)
    output_mint = Column(String(44), nullable=False)
    input_amount = Column(Float, nullable=False)
    output_amount = Column(Float, nullable=False)
    
    # Цены и комиссии
    input_price_usd = Column(Float, nullable=True)
    output_price_usd = Column(Float, nullable=True)
    fee_usd = Column(Float, default=0.0)
    slippage_percent = Column(Float, default=0.0)
    
    # Jupiter API данные
    jupiter_quote_id = Column(String(100), nullable=True)
    jupiter_route = Column(Text, nullable=True)  # JSON с маршрутом
    
    # Solana транзакция
    transaction_signature = Column(String(88), nullable=True)
    block_time = Column(DateTime(timezone=True), nullable=True)
    
    # Risk engine результаты
    risk_checks_passed = Column(Boolean, default=False)
    risk_checks_details = Column(Text, nullable=True)  # JSON с деталями
    
    # P&L
    pnl_usd = Column(Float, default=0.0)
    pnl_percent = Column(Float, default=0.0)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    executed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Связи
    profile = relationship("Profile", back_populates="trades")
    
    def __repr__(self):
        return f"<Trade(id={self.id}, type={self.trade_type}, status='{self.status}')>"