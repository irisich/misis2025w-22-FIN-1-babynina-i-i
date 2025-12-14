import asyncio
import os
import sys
from os import getenv
import logging

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from handlers import routers

load_dotenv()
TOKEN = os.getenv("TG_BOT_TOKEN")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

async def main() -> None:
    try:
        async with AiohttpSession() as session:

            bot = Bot(token=TOKEN, session=session)


            storage = MemoryStorage()
            dp = Dispatcher(storage=storage)

            for router in routers:
                dp.include_router(router)


            await storage.set_state(key=None, state=None)
            await storage.set_data(key=None, data={})


            try:
                me = await bot.get_me(request_timeout=15)
                logger.info(f"✅ Бот подключен")
            except TelegramNetworkError as e:
                logger.error(f" Ошибка подключения: {e}")
                return None

            logger.info("Бот запущен")

            await dp.start_polling(bot, skip_updates=True)

    except TelegramNetworkError as e:
        logger.error(f"Критическая ошибка: {e}")

    finally:
        logger.info("Работа бота завершена")


if __name__ == "__main__":
    asyncio.run(main())