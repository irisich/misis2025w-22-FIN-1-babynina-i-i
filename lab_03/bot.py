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
    """Configure base logging for the bot."""
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        level=logging.INFO,
    )


def preload_similarity() -> None:
    """
    Load the bundled ratings and build the item-based similarity matrix
    so that recommendations are available right after /start.
    """
    logger.info("Loading base ratings (MovieLens subset) and building similarity...")
    base_ratings = load_movielens_ratings()
    storage.load_base_ratings(base_ratings)
    item_count = len(storage.rating_storage.item_user)
    logger.info("Prepared %d ratings across %d items", len(base_ratings), item_count)


def create_dispatcher() -> Dispatcher:
    """Create dispatcher, attach middleware and include routers."""
    dp = Dispatcher()
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    for router in get_routers():
        dp.include_router(router)
    return dp


def run_bot() -> None:
    """Entry point: configure, preload data, and start polling."""
    if not BOT_KEY:
        raise RuntimeError("BOT_KEY is not set in environment or .env")

    setup_logging()
    preload_similarity()

    bot = Bot(
        token=BOT_KEY,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = create_dispatcher()

    logger.info("Bot is starting polling")
    dp.run_polling(bot)


if __name__ == "__main__":
    run_bot()
