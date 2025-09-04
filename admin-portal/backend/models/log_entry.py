"""
Модель для логов
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from services.database import Base
from datetime import datetime
from typing import Optional, Dict, Any

class LogEntry(Base):
    __tablename__ = "log_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    level = Column(String, nullable=False, index=True)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    logger = Column(String, nullable=False)  # Название логгера
    message = Column(Text, nullable=False)
    module = Column(String)  # Модуль, где произошло событие
    function = Column(String)  # Функция, где произошло событие
    line_number = Column(Integer)  # Номер строки
    thread_id = Column(String)  # ID потока
    process_id = Column(Integer)  # ID процесса
    hostname = Column(String)  # Имя хоста
    user_id = Column(String)  # ID пользователя (если применимо)
    session_id = Column(String)  # ID сессии (если применимо)
    request_id = Column(String)  # ID запроса (если применимо)
    extra_data = Column(JSON)  # Дополнительные данные
    created_at = Column(DateTime(timezone=True), server_default=func.now())