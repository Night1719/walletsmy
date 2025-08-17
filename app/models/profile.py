from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    wallet_address = Column(String(44), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    is_paper_trading = Column(Boolean, default=True)
    max_position_size_usd = Column(Integer, default=1000)
    max_daily_loss_usd = Column(Integer, default=100)
    risk_tolerance = Column(String(20), default="medium")  # low, medium, high
    
    # Настройки уведомлений
    telegram_enabled = Column(Boolean, default=False)
    discord_enabled = Column(Boolean, default=False)
    email_enabled = Column(Boolean, default=False)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    trades = relationship("Trade", back_populates="profile")
    positions = relationship("Position", back_populates="profile")
    
    def __repr__(self):
        return f"<Profile(id={self.id}, wallet={self.wallet_address}, name='{self.name}')>"