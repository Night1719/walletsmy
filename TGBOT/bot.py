import logging
from aiogram import Bot, Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
import os

from config import TELEGRAM_BOT_TOKEN, LOG_DIR, LOG_FILE, METRICS_PORT
from handlers.start import register_start_handlers
from handlers.main_menu import register_main_menu_handlers
from handlers.my_tasks import register_my_tasks_handlers
from handlers.approval import register_approval_handlers
from handlers.create_task import register_create_task_handlers
from handlers.settings import register_settings_handlers
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


async def on_startup(dp: Dispatcher):
    # start background worker and metrics server
    bot: Bot = dp.bot
    dp.loop.create_task(background_worker(bot))
    start_metrics_server(METRICS_PORT)


def main():
    load_dotenv()
    setup_logging()

    token = TELEGRAM_BOT_TOKEN or os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    bot = Bot(token=token, parse_mode="HTML")
    dp = Dispatcher(bot, storage=MemoryStorage())

    register_start_handlers(dp)
    register_main_menu_handlers(dp)
    register_my_tasks_handlers(dp)
    register_approval_handlers(dp)
    register_create_task_handlers(dp)
    register_settings_handlers(dp)

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


if __name__ == "__main__":
    main()