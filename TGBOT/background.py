import asyncio
import logging
from typing import Dict
from aiogram import Bot
from config import BACKGROUND_POLL_INTERVAL_SEC
from storage import get_all_sessions

logger = logging.getLogger(__name__)


async def background_worker(bot: Bot):
    while True:
        try:
            sessions: Dict[str, Dict] = get_all_sessions()
            # Здесь может быть логика сравнения кэша и рассылки уведомлений
            # Оставим как заглушку, чтобы не перегружать пример
            await asyncio.sleep(BACKGROUND_POLL_INTERVAL_SEC)
        except Exception as e:
            logger.exception(f"Background error: {e}")
            await asyncio.sleep(10)