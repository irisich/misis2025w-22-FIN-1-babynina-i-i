import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties

from config import BOT_KEY
from handlers import get_routers
from middleware.logging import LoggingMiddleware
from utils import storage
from utils.data_loader import load_movielens_ratings

logger = logging.getLogger("movie_recommender_bot")


def setup_logging() -> None:
    """ настройка базового логгирования """
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        level=logging.INFO,
    )


def preload_similarity() -> None:
    """
    Предзагрузка рейтингов и построение матрицы сходства.
    """
    logger.info("предзагрузка рейтингов и построение матрицы сходства")
    base_ratings = load_movielens_ratings()
    storage.load_base_ratings(base_ratings)
    item_count = len(storage.rating_storage.item_user)
    logger.info("подготовлено %d оценок для %d фильмов", len(base_ratings), item_count)


def create_dispatcher() -> Dispatcher:
    """ создает и настраивает диспетчер бота, который будет обрабатывать события """
    dp = Dispatcher()
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    for router in get_routers():
        dp.include_router(router)
    return dp


def run_bot() -> None:
    """ запускает бота """
    if not BOT_KEY:
        raise RuntimeError("отсутствует BOT_KEY в переменных окружения")

    setup_logging()
    preload_similarity()

    bot = Bot(
        token=BOT_KEY,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = create_dispatcher()

    logger.info("бот запущен")
    dp.run_polling(bot)


if __name__ == "__main__":
    run_bot()
