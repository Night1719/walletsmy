"""
Сервис для работы с метриками системы
"""
import psutil
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from services.redis_client import cache_set, cache_get, publish_message
from models.metric import Metric
from services.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

class MetricsService:
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """Сбор текущих метрик системы"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent,
                "used": psutil.virtual_memory().used
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "free": psutil.disk_usage('/').free,
                "percent": psutil.disk_usage('/').percent
            },
            "network": {
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv,
                "packets_sent": psutil.net_io_counters().packets_sent,
                "packets_recv": psutil.net_io_counters().packets_recv
            }
        }
        
        # Кэшируем метрики
        await cache_set("current_metrics", metrics, expire=60)
        
        # Сохраняем в базу данных
        await self._save_metrics(metrics)
        
        # Проверяем алерты
        await self._check_alerts(metrics)
        
        return metrics
    
    async def _save_metrics(self, metrics: Dict[str, Any]):
        """Сохранение метрик в базу данных"""
        async for db in get_db():
            metric = Metric(
                timestamp=datetime.fromisoformat(metrics["timestamp"]),
                cpu_percent=metrics["cpu_percent"],
                memory_total=metrics["memory"]["total"],
                memory_used=metrics["memory"]["used"],
                memory_percent=metrics["memory"]["percent"],
                disk_total=metrics["disk"]["total"],
                disk_used=metrics["disk"]["used"],
                disk_percent=metrics["disk"]["percent"],
                network_bytes_sent=metrics["network"]["bytes_sent"],
                network_bytes_recv=metrics["network"]["bytes_recv"]
            )
            db.add(metric)
            await db.commit()
            break
    
    async def get_historical_metrics(
        self, 
        start_time: datetime, 
        end_time: datetime, 
        metric_type: str = "all"
    ) -> List[Dict[str, Any]]:
        """Получение исторических метрик"""
        async for db in get_db():
            query = select(Metric).where(
                and_(
                    Metric.timestamp >= start_time,
                    Metric.timestamp <= end_time
                )
            ).order_by(Metric.timestamp.desc())
            
            result = await db.execute(query)
            metrics = result.scalars().all()
            
            return [
                {
                    "timestamp": metric.timestamp.isoformat(),
                    "cpu_percent": metric.cpu_percent,
                    "memory_percent": metric.memory_percent,
                    "disk_percent": metric.disk_percent,
                    "network_bytes_sent": metric.network_bytes_sent,
                    "network_bytes_recv": metric.network_bytes_recv
                }
                for metric in metrics
            ]
    
    async def _check_alerts(self, metrics: Dict[str, Any]):
        """Проверка метрик на превышение пороговых значений"""
        alerts = []
        
        # Проверка CPU
        if metrics["cpu_percent"] > 80:
            alerts.append({
                "type": "cpu_high",
                "message": f"High CPU usage: {metrics['cpu_percent']:.1f}%",
                "level": "warning" if metrics["cpu_percent"] < 90 else "critical"
            })
        
        # Проверка памяти
        if metrics["memory"]["percent"] > 85:
            alerts.append({
                "type": "memory_high",
                "message": f"High memory usage: {metrics['memory']['percent']:.1f}%",
                "level": "warning" if metrics["memory"]["percent"] < 95 else "critical"
            })
        
        # Проверка диска
        if metrics["disk"]["percent"] > 90:
            alerts.append({
                "type": "disk_high",
                "message": f"High disk usage: {metrics['disk']['percent']:.1f}%",
                "level": "critical"
            })
        
        # Отправляем алерты если есть
        if alerts:
            await publish_message("alerts", {
                "timestamp": datetime.now().isoformat(),
                "alerts": alerts
            })
    
    async def get_alerts(self) -> List[Dict[str, Any]]:
        """Получение активных алертов"""
        # В реальном приложении здесь была бы логика получения алертов из БД
        return []