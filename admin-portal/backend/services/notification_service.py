"""
Сервис для работы с уведомлениями
"""
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from services.database import get_db
from models.notification import Notification
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, update, delete

class NotificationService:
    
    async def get_notifications(
        self,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Получить список уведомлений"""
        async for db in get_db():
            query = select(Notification)
            
            if unread_only:
                query = query.where(Notification.is_read == False)
            
            query = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit)
            
            result = await db.execute(query)
            notifications = result.scalars().all()
            
            return [
                {
                    "id": notification.id,
                    "title": notification.title,
                    "message": notification.message,
                    "type": notification.type,
                    "level": notification.level,
                    "source": notification.source,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.isoformat(),
                    "read_at": notification.read_at.isoformat() if notification.read_at else None,
                    "metadata": notification.metadata,
                    "expires_at": notification.expires_at.isoformat() if notification.expires_at else None
                }
                for notification in notifications
            ]
    
    async def get_notification(self, notification_id: str) -> Dict[str, Any]:
        """Получить конкретное уведомление"""
        async for db in get_db():
            result = await db.execute(select(Notification).where(Notification.id == notification_id))
            notification = result.scalar_one_or_none()
            
            if not notification:
                raise ValueError(f"Notification {notification_id} not found")
            
            return {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "type": notification.type,
                "level": notification.level,
                "source": notification.source,
                "is_read": notification.is_read,
                "created_at": notification.created_at.isoformat(),
                "read_at": notification.read_at.isoformat() if notification.read_at else None,
                "metadata": notification.metadata,
                "expires_at": notification.expires_at.isoformat() if notification.expires_at else None
            }
    
    async def mark_as_read(self, notification_id: str) -> Dict[str, Any]:
        """Отметить уведомление как прочитанное"""
        async for db in get_db():
            result = await db.execute(
                update(Notification)
                .where(Notification.id == notification_id)
                .values(is_read=True, read_at=datetime.now())
            )
            
            if result.rowcount == 0:
                raise ValueError(f"Notification {notification_id} not found")
            
            await db.commit()
            
            return {
                "id": notification_id,
                "message": "Notification marked as read"
            }
    
    async def mark_all_as_read(self) -> Dict[str, Any]:
        """Отметить все уведомления как прочитанные"""
        async for db in get_db():
            result = await db.execute(
                update(Notification)
                .where(Notification.is_read == False)
                .values(is_read=True, read_at=datetime.now())
            )
            
            await db.commit()
            
            return {
                "message": f"Marked {result.rowcount} notifications as read"
            }
    
    async def delete_notification(self, notification_id: str) -> Dict[str, Any]:
        """Удалить уведомление"""
        async for db in get_db():
            result = await db.execute(delete(Notification).where(Notification.id == notification_id))
            
            if result.rowcount == 0:
                raise ValueError(f"Notification {notification_id} not found")
            
            await db.commit()
            
            return {
                "id": notification_id,
                "message": "Notification deleted"
            }
    
    async def get_stats(self) -> Dict[str, Any]:
        """Получить статистику уведомлений"""
        async for db in get_db():
            # Общее количество
            total_query = select(func.count(Notification.id))
            total_result = await db.execute(total_query)
            total_count = total_result.scalar()
            
            # Непрочитанные
            unread_query = select(func.count(Notification.id)).where(Notification.is_read == False)
            unread_result = await db.execute(unread_query)
            unread_count = unread_result.scalar()
            
            # По типам
            type_query = select(
                Notification.type,
                func.count(Notification.id).label('count')
            ).group_by(Notification.type)
            type_result = await db.execute(type_query)
            type_stats = {row.type: row.count for row in type_result}
            
            # По уровням
            level_query = select(
                Notification.level,
                func.count(Notification.id).label('count')
            ).group_by(Notification.level)
            level_result = await db.execute(level_query)
            level_stats = {row.level: row.count for row in level_result}
            
            return {
                "total_count": total_count,
                "unread_count": unread_count,
                "read_count": total_count - unread_count,
                "type_stats": type_stats,
                "level_stats": level_stats
            }
    
    async def create_notification(
        self,
        title: str,
        message: str,
        type: str = "info",
        level: str = "medium",
        source: str = "system",
        metadata: Optional[Dict[str, Any]] = None,
        expires_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Создать новое уведомление"""
        notification_id = str(uuid.uuid4())
        
        async for db in get_db():
            notification = Notification(
                id=notification_id,
                title=title,
                message=message,
                type=type,
                level=level,
                source=source,
                metadata=metadata or {},
                expires_at=expires_at
            )
            
            db.add(notification)
            await db.commit()
            
            return {
                "id": notification_id,
                "message": "Notification created successfully"
            }
    
    async def update_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Обновить настройки уведомлений"""
        # В реальном приложении здесь была бы логика сохранения настроек
        return {
            "message": "Settings updated successfully",
            "settings": settings
        }
    
    async def get_settings(self) -> Dict[str, Any]:
        """Получить настройки уведомлений"""
        # Возвращаем настройки по умолчанию
        return {
            "email_notifications": True,
            "push_notifications": True,
            "critical_alerts": True,
            "warning_alerts": True,
            "info_alerts": False,
            "retention_days": 30
        }