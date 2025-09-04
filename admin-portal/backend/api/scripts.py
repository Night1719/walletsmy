"""
API endpoints для управления скриптами
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Dict, Any, Optional
import os
import subprocess
import asyncio
from datetime import datetime
from services.script_service import ScriptService

router = APIRouter()
script_service = ScriptService()


@router.get("/")
async def get_scripts():
    """Получить список всех скриптов"""
    try:
        return await script_service.get_all_scripts()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{script_id}")
async def get_script(script_id: str):
    """Получить информацию о конкретном скрипте"""
    try:
        return await script_service.get_script(script_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_script(
    file: UploadFile = File(...),
    category: str = Form(...),
    description: str = Form("")
):
    """Загрузить новый скрипт"""
    try:
        return await script_service.upload_script(file, category, description)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{script_id}/execute")
async def execute_script(
    script_id: str,
    parameters: Optional[Dict[str, Any]] = None
):
    """Выполнить скрипт"""
    try:
        return await script_service.execute_script(script_id, parameters or {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{script_id}/logs")
async def get_script_logs(
    script_id: str,
    limit: int = 100,
    offset: int = 0
):
    """Получить логи выполнения скрипта"""
    try:
        return await script_service.get_script_logs(script_id, limit, offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{script_id}/status")
async def get_script_status(script_id: str):
    """Получить статус выполнения скрипта"""
    try:
        return await script_service.get_script_status(script_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{script_id}")
async def delete_script(script_id: str):
    """Удалить скрипт"""
    try:
        return await script_service.delete_script(script_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{script_id}/schedule")
async def schedule_script(
    script_id: str,
    cron_expression: str = Form(...),
    enabled: bool = Form(True)
):
    """Настроить расписание выполнения скрипта"""
    try:
        return await script_service.schedule_script(script_id, cron_expression, enabled)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))