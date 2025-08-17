from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import structlog
import time

from app.config import settings
from app.api import api_router
from app.middleware import PrometheusMiddleware
from app.database import init_db

# Настройка логирования
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Создание FastAPI приложения
app = FastAPI(
    title="Solana Trading Bot",
    description="Платформа для трейдинга на Solana DEX через Jupiter API",
    version="1.0.0",
    docs_url="/docs" if not settings.is_production() else None,
    redoc_url="/redoc" if not settings.is_production() else None,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not settings.is_production() else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if not settings.is_production() else ["yourdomain.com"]
)

if settings.prometheus_enabled:
    app.add_middleware(PrometheusMiddleware)

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключение шаблонов
templates = Jinja2Templates(directory="templates")

# Подключение API роутера
app.include_router(api_router, prefix="/api")

# События жизненного цикла
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Solana Trading Bot...")
    await init_db()
    logger.info("Database initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Solana Trading Bot...")

# Главная страница
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Solana Trading Bot",
            "is_devnet": settings.is_devnet(),
            "enable_real_trades": settings.enable_real_trades
        }
    )

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "environment": "production" if settings.is_production() else "development",
        "solana_network": settings.solana_network
    }

# Обработка ошибок
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse(
        "404.html",
        {"request": request},
        status_code=404
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error("Internal server error", exc_info=exc)
    return templates.TemplateResponse(
        "500.html",
        {"request": request},
        status_code=500
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )