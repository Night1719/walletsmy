# BG Survey Platform - Docker контейнер
# Многоэтапная сборка для оптимизации размера

# Этап 1: Сборка
FROM python:3.11-slim as builder

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Создание виртуального окружения
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Этап 2: Финальный образ
FROM python:3.11-slim

# Метаданные
LABEL maintainer="BunterGroup <support@buntergroup.com>"
LABEL description="BG Survey Platform - Корпоративная платформа для опросов"
LABEL version="1.0.0"

# Создание пользователя для безопасности
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копирование виртуального окружения из этапа сборки
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Создание рабочих директорий
WORKDIR /app
RUN mkdir -p /app/logs /app/uploads && \
    chown -R appuser:appuser /app

# Копирование исходного кода
COPY --chown=appuser:appuser . .

# Создание директории для статических файлов
RUN mkdir -p /app/static && chown -R appuser:appuser /app/static

# Переключение на непривилегированного пользователя
USER appuser

# Переменные окружения
ENV FLASK_CONFIG=production
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Проверка здоровья
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Открытие порта
EXPOSE 8000

# Команда запуска
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "sync", "--timeout", "120", "--access-logfile", "/app/logs/gunicorn_access.log", "--error-logfile", "/app/logs/gunicorn_error.log", "--log-level", "info", "app:app"]