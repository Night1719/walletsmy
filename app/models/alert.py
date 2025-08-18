from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class AlertChannel(Base):
    __tablename__ = "alert_channels"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Основная информация
    name = Column(String(100), nullable=False)
    channel_type = Column(String(50), nullable=False)  # telegram, discord, email, webhook
    
    # Настройки канала
    is_active = Column(Boolean, default=True)
    config = Column(JSON, nullable=True)  # Конфигурация канала (токены, URL и т.д.)
    
    # Фильтры алертов
    alert_types = Column(JSON, nullable=True)  # Типы алертов для отправки
    min_severity = Column(String(20), default="info")  # info, warning, error, critical
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Статистика
    total_alerts_sent = Column(Integer, default=0)
    failed_deliveries = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<AlertChannel(id={self.id}, name='{self.name}', type='{self.channel_type}')>"