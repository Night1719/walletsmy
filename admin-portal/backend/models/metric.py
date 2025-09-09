"""
Модель для метрик системы
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, BigInteger
from sqlalchemy.sql import func
from services.database import Base
from datetime import datetime

class Metric(Base):
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    cpu_percent = Column(Float)
    memory_total = Column(BigInteger)
    memory_used = Column(BigInteger)
    memory_percent = Column(Float)
    disk_total = Column(BigInteger)
    disk_used = Column(BigInteger)
    disk_percent = Column(Float)
    network_bytes_sent = Column(BigInteger)
    network_bytes_recv = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())