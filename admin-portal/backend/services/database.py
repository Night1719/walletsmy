"""
Настройка и инициализация базы данных
"""
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Настройки базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./admin_portal.db")
ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL", "sqlite+aiosqlite:///./admin_portal.db")

# Создание движка базы данных
engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


async def init_db():
    """Инициализация базы данных"""
    # Импортируем все модели
    from models import script, notification, log_entry, metric
    
    # Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Получение сессии базы данных"""
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()