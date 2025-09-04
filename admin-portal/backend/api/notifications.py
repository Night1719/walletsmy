"""
API endpoints для уведомлений
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Optional
from datetime import datetime
from services.notification_service import NotificationService
from services.websocket_manager import WebSocketManager

router = APIRouter()
notification_service = NotificationService()
websocket_manager = WebSocketManager()


@router.get("/")
async def get_notifications(
    limit: int = 50,
    offset: int = 0,
    unread_only: bool = False
):
    """Получить список уведомлений"""
    try:
        return await notification_service.get_notifications(
            limit=limit,
            offset=offset,
            unread_only=unread_only
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{notification_id}")
async def get_notification(notification_id: str):
    """Получить конкретное уведомление"""
    try:
        return await notification_service.get_notification(notification_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{notification_id}/read")
async def mark_as_read(notification_id: str):
    """Отметить уведомление как прочитанное"""
    try:
        return await notification_service.mark_as_read(notification_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/read-all")
async def mark_all_as_read():
    """Отметить все уведомления как прочитанные"""
    try:
        return await notification_service.mark_all_as_read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{notification_id}")
async def delete_notification(notification_id: str):
    """Удалить уведомление"""
    try:
        return await notification_service.delete_notification(notification_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_notification_stats():
    """Получить статистику уведомлений"""
    try:
        return await notification_service.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/settings")
async def update_notification_settings(
    settings: Dict[str, Any]
):
    """Обновить настройки уведомлений"""
    try:
        return await notification_service.update_settings(settings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings")
async def get_notification_settings():
    """Получить настройки уведомлений"""
    try:
        return await notification_service.get_settings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint для real-time уведомлений"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Ожидаем сообщения от клиента
            data = await websocket.receive_text()
            # Обрабатываем сообщение (если нужно)
            await websocket_manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)