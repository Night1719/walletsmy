"""
API endpoints для метрик системы
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import psutil
import time
from datetime import datetime, timedelta
from services.metrics_service import MetricsService

router = APIRouter()
metrics_service = MetricsService()


@router.get("/system")
async def get_system_metrics():
    """Получить системные метрики"""
    try:
        return {
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
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/historical")
async def get_historical_metrics(
    hours: int = 24,
    metric_type: str = "all"
):
    """Получить исторические метрики"""
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        return await metrics_service.get_historical_metrics(
            start_time, end_time, metric_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/processes")
async def get_processes_metrics():
    """Получить метрики процессов"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Сортируем по использованию CPU
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        
        return {
            "processes": processes[:20],  # Топ 20 процессов
            "total_processes": len(processes),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def get_metric_alerts():
    """Получить алерты по метрикам"""
    try:
        return await metrics_service.get_alerts()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))