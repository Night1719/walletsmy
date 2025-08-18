#!/usr/bin/env python3
"""
Запуск Sniper Bot для Solana Trading Bot
"""

import asyncio
import signal
import sys
from bot.sniper_bot import SniperBot
import structlog

logger = structlog.get_logger()

async def main():
    """Основная функция запуска снайпер-бота"""
    sniper = SniperBot()
    
    # Обработчик сигналов для graceful shutdown
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal, stopping sniper bot...")
        asyncio.create_task(sniper.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        logger.info("Starting Sniper Bot...")
        await sniper.start()
    except KeyboardInterrupt:
        logger.info("Sniper Bot stopped by user")
    except Exception as e:
        logger.error("Sniper Bot error", error=str(e))
        sys.exit(1)
    finally:
        await sniper.stop()
        logger.info("Sniper Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())