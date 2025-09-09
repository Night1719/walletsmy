"""
Модель для уведомлений
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from services.database import Base
from datetime import datetime
from typing import Optional, Dict, Any

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String, nullable=False)  # info, warning, error, success
    level = Column(String, nullable=False)  # low, medium, high, critical
    source = Column(String)  # system, script, metric, user
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True))
    metadata = Column(JSON)  # Дополнительные данные уведомления
    expires_at = Column(DateTime(timezone=True))  # Время истечения уведомления