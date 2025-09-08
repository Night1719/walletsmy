import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os

from config import TELEGRAM_BOT_TOKEN, LOG_DIR, LOG_FILE, METRICS_PORT
from handlers import start as start_handlers
from handlers import main_menu as main_menu_handlers
from handlers import my_tasks as my_tasks_handlers
from handlers import approval as approval_handlers
from handlers import create_task as create_task_handlers
from handlers import settings as settings_handlers
from handlers import instructions as instructions_handlers
from background import background_worker
from metrics import start_metrics_server


def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
        ],
    )


async def on_startup(bot: Bot, dp: Dispatcher):
    dp.loop = asyncio.get_event_loop()
    dp.loop.create_task(background_worker(bot))
    start_metrics_server(METRICS_PORT)


async def main_async():
    load_dotenv()
    setup_logging()

    token = TELEGRAM_BOT_TOKEN or os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=MemoryStorage())

    # Include routers
    dp.include_router(start_handlers.router)
    dp.include_router(main_menu_handlers.router)
    dp.include_router(my_tasks_handlers.router)
    dp.include_router(approval_handlers.router)
    dp.include_router(create_task_handlers.router)
    dp.include_router(settings_handlers.router)
    dp.include_router(instructions_handlers.router)

    await on_startup(bot, dp)
    await dp.start_polling(bot)


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()