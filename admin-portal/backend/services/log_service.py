"""
Сервис для работы с логами
"""
import os
import json
import glob
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
from services.database import get_db
from models.log_entry import LogEntry
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

class LogService:
    
    def __init__(self):
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
    
    async def get_logs(
        self,
        log_type: str = "all",
        level: str = "all",
        limit: int = 100,
        offset: int = 0,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Получить логи с фильтрацией"""
        async for db in get_db():
            query = select(LogEntry)
            
            # Фильтры
            conditions = []
            
            if level != "all":
                conditions.append(LogEntry.level == level.upper())
            
            if start_time:
                conditions.append(LogEntry.timestamp >= start_time)
            
            if end_time:
                conditions.append(LogEntry.timestamp <= end_time)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            # Сортировка и пагинация
            query = query.order_by(LogEntry.timestamp.desc()).offset(offset).limit(limit)
            
            result = await db.execute(query)
            logs = result.scalars().all()
            
            # Подсчет общего количества
            count_query = select(func.count(LogEntry.id))
            if conditions:
                count_query = count_query.where(and_(*conditions))
            
            count_result = await db.execute(count_query)
            total_count = count_result.scalar()
            
            return {
                "logs": [
                    {
                        "id": log.id,
                        "timestamp": log.timestamp.isoformat(),
                        "level": log.level,
                        "logger": log.logger,
                        "message": log.message,
                        "module": log.module,
                        "function": log.function,
                        "line_number": log.line_number,
                        "thread_id": log.thread_id,
                        "process_id": log.process_id,
                        "hostname": log.hostname,
                        "user_id": log.user_id,
                        "session_id": log.session_id,
                        "request_id": log.request_id,
                        "extra_data": log.extra_data
                    }
                    for log in logs
                ],
                "total_count": total_count,
                "limit": limit,
                "offset": offset
            }
    
    async def get_log_types(self) -> List[str]:
        """Получить доступные типы логов"""
        return ["system", "application", "error", "all"]
    
    async def search_logs(
        self, 
        query: str, 
        log_type: str = "all", 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Поиск по логам"""
        async for db in get_db():
            search_query = select(LogEntry).where(
                or_(
                    LogEntry.message.contains(query),
                    LogEntry.logger.contains(query),
                    LogEntry.module.contains(query)
                )
            ).order_by(LogEntry.timestamp.desc()).limit(limit)
            
            result = await db.execute(search_query)
            logs = result.scalars().all()
            
            return [
                {
                    "id": log.id,
                    "timestamp": log.timestamp.isoformat(),
                    "level": log.level,
                    "logger": log.logger,
                    "message": log.message,
                    "module": log.module
                }
                for log in logs
            ]
    
    async def get_log_stats(
        self, 
        start_time: datetime, 
        end_time: datetime
    ) -> Dict[str, Any]:
        """Получить статистику логов"""
        async for db in get_db():
            # Общее количество логов
            total_query = select(func.count(LogEntry.id)).where(
                and_(
                    LogEntry.timestamp >= start_time,
                    LogEntry.timestamp <= end_time
                )
            )
            total_result = await db.execute(total_query)
            total_count = total_result.scalar()
            
            # Количество по уровням
            level_query = select(
                LogEntry.level,
                func.count(LogEntry.id).label('count')
            ).where(
                and_(
                    LogEntry.timestamp >= start_time,
                    LogEntry.timestamp <= end_time
                )
            ).group_by(LogEntry.level)
            
            level_result = await db.execute(level_query)
            level_stats = {row.level: row.count for row in level_result}
            
            # Количество по модулям
            module_query = select(
                LogEntry.module,
                func.count(LogEntry.id).label('count')
            ).where(
                and_(
                    LogEntry.timestamp >= start_time,
                    LogEntry.timestamp <= end_time,
                    LogEntry.module.isnot(None)
                )
            ).group_by(LogEntry.module).order_by(func.count(LogEntry.id).desc()).limit(10)
            
            module_result = await db.execute(module_query)
            module_stats = {row.module: row.count for row in module_result}
            
            return {
                "total_count": total_count,
                "level_stats": level_stats,
                "top_modules": module_stats,
                "period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                }
            }
    
    async def tail_log_file(
        self, 
        log_file: str, 
        lines: int = 100
    ) -> List[str]:
        """Получить последние строки лог-файла"""
        log_path = self.logs_dir / log_file
        
        if not log_path.exists():
            raise ValueError(f"Log file not found: {log_file}")
        
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
        except Exception as e:
            raise ValueError(f"Error reading log file: {e}")
    
    async def export_logs(
        self,
        log_type: str = "all",
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Экспортировать логи"""
        # Получаем логи
        logs_data = await self.get_logs(
            log_type=log_type,
            start_time=start_time,
            end_time=end_time,
            limit=10000  # Большой лимит для экспорта
        )
        
        logs = logs_data["logs"]
        
        if format == "json":
            return {
                "format": "json",
                "data": logs,
                "count": len(logs)
            }
        elif format == "csv":
            # Простая CSV конвертация
            csv_lines = ["timestamp,level,logger,message,module"]
            for log in logs:
                csv_lines.append(
                    f"{log['timestamp']},{log['level']},{log['logger']},"
                    f'"{log["message"].replace('"', '""')}",{log["module"] or ""}'
                )
            return {
                "format": "csv",
                "data": "\n".join(csv_lines),
                "count": len(logs)
            }
        else:
            # TXT формат
            txt_lines = []
            for log in logs:
                txt_lines.append(
                    f"[{log['timestamp']}] {log['level']} {log['logger']}: {log['message']}"
                )
            return {
                "format": "txt",
                "data": "\n".join(txt_lines),
                "count": len(logs)
            }