"""
Модель для скриптов
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from services.database import Base
from datetime import datetime
from typing import Optional, Dict, Any

class Script(Base):
    __tablename__ = "scripts"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    category = Column(String, nullable=False)  # monitoring, backup, maintenance
    description = Column(Text)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    cron_schedule = Column(String)  # Cron выражение для расписания
    last_executed = Column(DateTime(timezone=True))
    execution_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    metadata = Column(JSON)  # Дополнительные параметры скрипта