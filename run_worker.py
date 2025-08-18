#!/usr/bin/env python3
"""
Запуск Celery Worker для Solana Trading Bot
"""

from worker.celery_app import celery_app

if __name__ == "__main__":
    celery_app.start()