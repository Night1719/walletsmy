"""
Сервис для работы со скриптами
"""
import os
import uuid
import subprocess
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from services.database import get_db
from models.script import Script
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

class ScriptService:
    
    def __init__(self):
        self.scripts_dir = Path("scripts")
        self.scripts_dir.mkdir(exist_ok=True)
    
    async def get_all_scripts(self) -> List[Dict[str, Any]]:
        """Получить все скрипты"""
        async for db in get_db():
            result = await db.execute(select(Script))
            scripts = result.scalars().all()
            
            return [
                {
                    "id": script.id,
                    "name": script.name,
                    "filename": script.filename,
                    "category": script.category,
                    "description": script.description,
                    "is_active": script.is_active,
                    "last_executed": script.last_executed.isoformat() if script.last_executed else None,
                    "execution_count": script.execution_count,
                    "success_count": script.success_count,
                    "failure_count": script.failure_count,
                    "created_at": script.created_at.isoformat(),
                    "cron_schedule": script.cron_schedule
                }
                for script in scripts
            ]
    
    async def get_script(self, script_id: str) -> Dict[str, Any]:
        """Получить конкретный скрипт"""
        async for db in get_db():
            result = await db.execute(select(Script).where(Script.id == script_id))
            script = result.scalar_one_or_none()
            
            if not script:
                raise ValueError(f"Script {script_id} not found")
            
            return {
                "id": script.id,
                "name": script.name,
                "filename": script.filename,
                "category": script.category,
                "description": script.description,
                "file_path": script.file_path,
                "file_size": script.file_size,
                "is_active": script.is_active,
                "last_executed": script.last_executed.isoformat() if script.last_executed else None,
                "execution_count": script.execution_count,
                "success_count": script.success_count,
                "failure_count": script.failure_count,
                "created_at": script.created_at.isoformat(),
                "cron_schedule": script.cron_schedule,
                "metadata": script.metadata
            }
    
    async def upload_script(
        self, 
        file, 
        category: str, 
        description: str = ""
    ) -> Dict[str, Any]:
        """Загрузить новый скрипт"""
        script_id = str(uuid.uuid4())
        category_dir = self.scripts_dir / category
        category_dir.mkdir(exist_ok=True)
        
        file_path = category_dir / file.filename
        file_size = 0
        
        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            file_size = len(content)
        
        # Делаем файл исполняемым
        os.chmod(file_path, 0o755)
        
        # Сохраняем в базу данных
        async for db in get_db():
            script = Script(
                id=script_id,
                name=file.filename,
                filename=file.filename,
                category=category,
                description=description,
                file_path=str(file_path),
                file_size=file_size
            )
            db.add(script)
            await db.commit()
            break
        
        return {
            "id": script_id,
            "name": file.filename,
            "category": category,
            "message": "Script uploaded successfully"
        }
    
    async def execute_script(
        self, 
        script_id: str, 
        parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Выполнить скрипт"""
        async for db in get_db():
            result = await db.execute(select(Script).where(Script.id == script_id))
            script = result.scalar_one_or_none()
            
            if not script:
                raise ValueError(f"Script {script_id} not found")
            
            if not os.path.exists(script.file_path):
                raise ValueError(f"Script file not found: {script.file_path}")
            
            # Подготавливаем команду
            cmd = [script.file_path]
            if parameters:
                for key, value in parameters.items():
                    cmd.extend([f"--{key}", str(value)])
            
            try:
                # Выполняем скрипт
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                # Обновляем статистику
                script.execution_count += 1
                script.last_executed = datetime.now()
                
                if process.returncode == 0:
                    script.success_count += 1
                    status = "success"
                else:
                    script.failure_count += 1
                    status = "failed"
                
                await db.commit()
                
                return {
                    "script_id": script_id,
                    "status": status,
                    "return_code": process.returncode,
                    "stdout": stdout.decode() if stdout else "",
                    "stderr": stderr.decode() if stderr else "",
                    "execution_time": datetime.now().isoformat()
                }
                
            except Exception as e:
                script.failure_count += 1
                await db.commit()
                
                return {
                    "script_id": script_id,
                    "status": "error",
                    "error": str(e),
                    "execution_time": datetime.now().isoformat()
                }
    
    async def get_script_logs(
        self, 
        script_id: str, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Получить логи выполнения скрипта"""
        # В реальном приложении здесь была бы логика получения логов из БД
        return []
    
    async def get_script_status(self, script_id: str) -> Dict[str, Any]:
        """Получить статус выполнения скрипта"""
        async for db in get_db():
            result = await db.execute(select(Script).where(Script.id == script_id))
            script = result.scalar_one_or_none()
            
            if not script:
                raise ValueError(f"Script {script_id} not found")
            
            return {
                "script_id": script_id,
                "is_active": script.is_active,
                "last_executed": script.last_executed.isoformat() if script.last_executed else None,
                "execution_count": script.execution_count,
                "success_count": script.success_count,
                "failure_count": script.failure_count,
                "success_rate": (
                    script.success_count / script.execution_count * 100 
                    if script.execution_count > 0 else 0
                )
            }
    
    async def delete_script(self, script_id: str) -> Dict[str, Any]:
        """Удалить скрипт"""
        async for db in get_db():
            result = await db.execute(select(Script).where(Script.id == script_id))
            script = result.scalar_one_or_none()
            
            if not script:
                raise ValueError(f"Script {script_id} not found")
            
            # Удаляем файл
            if os.path.exists(script.file_path):
                os.remove(script.file_path)
            
            # Удаляем из базы данных
            await db.execute(delete(Script).where(Script.id == script_id))
            await db.commit()
            
            return {
                "script_id": script_id,
                "message": "Script deleted successfully"
            }
    
    async def schedule_script(
        self, 
        script_id: str, 
        cron_expression: str, 
        enabled: bool = True
    ) -> Dict[str, Any]:
        """Настроить расписание выполнения скрипта"""
        async for db in get_db():
            result = await db.execute(select(Script).where(Script.id == script_id))
            script = result.scalar_one_or_none()
            
            if not script:
                raise ValueError(f"Script {script_id} not found")
            
            script.cron_schedule = cron_expression
            script.is_active = enabled
            
            await db.commit()
            
            return {
                "script_id": script_id,
                "cron_schedule": cron_expression,
                "enabled": enabled,
                "message": "Schedule updated successfully"
            }