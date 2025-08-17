from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Position(Base):
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Основная информация
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    strategy_name = Column(String(100), nullable=False)
    
    # Токен
    token_mint = Column(String(44), nullable=False)
    token_name = Column(String(100), nullable=True)
    token_symbol = Column(String(20), nullable=True)
    token_decimals = Column(Integer, default=9)
    
    # Размер позиции
    amount = Column(Float, nullable=False)
    entry_price_usd = Column(Float, nullable=False)
    current_price_usd = Column(Float, nullable=True)
    
    # P&L
    pnl_usd = Column(Float, default=0.0)
    pnl_percent = Column(Float, default=0.0)
    unrealized_pnl_usd = Column(Float, default=0.0)
    realized_pnl_usd = Column(Float, default=0.0)
    
    # Статус позиции
    is_open = Column(Boolean, default=True)
    is_paper_trading = Column(Boolean, default=True)
    
    # Stop-loss и Take-profit
    stop_loss_usd = Column(Float, nullable=True)
    take_profit_usd = Column(Float, nullable=True)
    
    # Временные метки
    entry_time = Column(DateTime(timezone=True), server_default=func.now())
    exit_time = Column(DateTime(timezone=True), nullable=True)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    profile = relationship("Profile", back_populates="positions")
    
    def __repr__(self):
        return f"<Position(id={self.id}, token='{self.token_symbol}', amount={self.amount})>"