"""
Главный файл FastAPI приложения для админского портала
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import os
import sys

# Добавляем текущую директорию в путь для импортов
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api import metrics, scripts, logs, notifications
from services.database import init_db
from services.redis_client import init_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация при запуске и очистка при завершении"""
    # Инициализация при запуске
    await init_db()
    await init_redis()
    yield
    # Очистка при завершении (если нужна)


app = FastAPI(
    title="Admin Portal API",
    description="API для портала системных администраторов",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(scripts.router, prefix="/api/scripts", tags=["scripts"])
app.include_router(logs.router, prefix="/api/logs", tags=["logs"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])

# Статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "Admin Portal API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья API"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )