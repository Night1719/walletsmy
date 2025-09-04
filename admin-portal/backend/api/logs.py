"""
API endpoints для работы с логами
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from services.log_service import LogService

router = APIRouter()
log_service = LogService()


@router.get("/")
async def get_logs(
    log_type: str = Query("all", description="Тип лога: system, application, error, all"),
    level: str = Query("all", description="Уровень лога: DEBUG, INFO, WARNING, ERROR, CRITICAL"),
    limit: int = Query(100, description="Количество записей"),
    offset: int = Query(0, description="Смещение"),
    start_time: Optional[str] = Query(None, description="Начальное время (ISO format)"),
    end_time: Optional[str] = Query(None, description="Конечное время (ISO format)")
):
    """Получить логи с фильтрацией"""
    try:
        start_dt = None
        end_dt = None
        
        if start_time:
            start_dt = datetime.fromisoformat(start_time)
        if end_time:
            end_dt = datetime.fromisoformat(end_time)
            
        return await log_service.get_logs(
            log_type=log_type,
            level=level,
            limit=limit,
            offset=offset,
            start_time=start_dt,
            end_time=end_dt
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types")
async def get_log_types():
    """Получить доступные типы логов"""
    try:
        return await log_service.get_log_types()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/levels")
async def get_log_levels():
    """Получить доступные уровни логов"""
    return {
        "levels": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        "default": "INFO"
    }


@router.get("/search")
async def search_logs(
    query: str = Query(..., description="Поисковый запрос"),
    log_type: str = Query("all", description="Тип лога"),
    limit: int = Query(50, description="Количество результатов")
):
    """Поиск по логам"""
    try:
        return await log_service.search_logs(query, log_type, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_log_stats(
    hours: int = Query(24, description="Период в часах")
):
    """Получить статистику логов"""
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        return await log_service.get_log_stats(start_time, end_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tail/{log_file}")
async def tail_log_file(
    log_file: str,
    lines: int = Query(100, description="Количество последних строк")
):
    """Получить последние строки лог-файла"""
    try:
        return await log_service.tail_log_file(log_file, lines)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export")
async def export_logs(
    log_type: str = Query("all", description="Тип логов для экспорта"),
    start_time: Optional[str] = Query(None, description="Начальное время"),
    end_time: Optional[str] = Query(None, description="Конечное время"),
    format: str = Query("json", description="Формат экспорта: json, csv, txt")
):
    """Экспортировать логи"""
    try:
        start_dt = None
        end_dt = None
        
        if start_time:
            start_dt = datetime.fromisoformat(start_time)
        if end_time:
            end_dt = datetime.fromisoformat(end_time)
            
        return await log_service.export_logs(log_type, start_dt, end_dt, format)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))