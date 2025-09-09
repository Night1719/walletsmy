"""
Менеджер WebSocket соединений для real-time уведомлений
"""
from fastapi import WebSocket
from typing import List, Dict, Any
import json
import asyncio

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Подключить новое WebSocket соединение"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Отключить WebSocket соединение"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Отправить персональное сообщение"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Отправить сообщение всем подключенным клиентам"""
        if not self.active_connections:
            return
        
        message_text = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_text)
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Удаляем отключенные соединения
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_notification(self, notification: Dict[str, Any]):
        """Отправить уведомление всем клиентам"""
        await self.broadcast({
            "type": "notification",
            "data": notification
        })
    
    async def send_metric_alert(self, alert: Dict[str, Any]):
        """Отправить алерт по метрикам всем клиентам"""
        await self.broadcast({
            "type": "metric_alert",
            "data": alert
        })
    
    async def send_script_status(self, script_status: Dict[str, Any]):
        """Отправить статус скрипта всем клиентам"""
        await self.broadcast({
            "type": "script_status",
            "data": script_status
        })
    
    def get_connection_count(self) -> int:
        """Получить количество активных соединений"""
        return len(self.active_connections)