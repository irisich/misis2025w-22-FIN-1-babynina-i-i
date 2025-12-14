from typing import Dict, List

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery

from config import MESSAGES
from keyboards.inline import navigation_keyboard
from utils import storage
from utils.data_loader import find_movie_by_name, display_title, top_movies_by_genre, list_genres

recommendations_router = Router()

USER_RECS: Dict[int, List[str]] = {}
USER_PTR: Dict[int, int] = {}
BATCH_SIZE = 5


def _format_batch(recs: List[str], offset: int = 0) -> List[str]:
    return [f"{idx + 1 + offset}. {display_title(r)}" for idx, r in enumerate(recs)]


@recommendations_router.message(Command("recommend"))
async def handle_recommend(message: types.Message) -> None:
    """Вернуть похожие фильмы по названию (Item-Based CF / Пирсон)."""
    text = (message.text or "").strip()
    parts = text.split(maxsplit=1)
    query = parts[1].strip() if len(parts) > 1 else ""
    if not query:
        await message.answer(MESSAGES.get("ask_movie", "Напиши название фильма после /recommend."))
        return

    movie_key = find_movie_by_name(query)
    if not movie_key:
        await message.answer(MESSAGES.get("error_no_movie", "Не нашел такой фильм в базе."))
        return

    recs = storage.similar_items(movie_key, top_n=30)
    if not recs:
        await message.answer(MESSAGES.get("error_no_recs", "Пока нет похожих фильмов."))
        return

    USER_RECS[message.from_user.id] = recs
    USER_PTR[message.from_user.id] = 0

    batch = recs[:BATCH_SIZE]
    pretty = _format_batch(batch, offset=0)
    await message.answer(
        MESSAGES.get("recommendation_result", "Вот что могу предложить:") + "\n" + "\n".join(pretty),
        reply_markup=navigation_keyboard(has_more=len(recs) > BATCH_SIZE),
    )


@recommendations_router.message(Command("genre"))
@recommendations_router.message(F.text.lower() == "выбрать жанр")
async def handle_genre(message: types.Message) -> None:
    """Вернуть топ фильмов по жанру, отсортированных по среднему рейтингу."""
    text = (message.text or "").strip()
    parts = text.split(maxsplit=1)
    genre_query = parts[1].strip() if len(parts) > 1 else ""

    available = ", ".join(list_genres())
    if not genre_query:
        await message.answer(
            MESSAGES.get("ask_genre", "Выбери жанр.") + f"\nДоступные жанры: {available}"
        )
        return

    top_in_genre = top_movies_by_genre(genre_query, top_n=30)
    if not top_in_genre:
        await message.answer(MESSAGES.get("error_no_genre", "Не нашел такой жанр."))
        return

    USER_RECS[message.from_user.id] = top_in_genre
    USER_PTR[message.from_user.id] = 0

    batch = top_in_genre[:BATCH_SIZE]
    pretty = _format_batch(batch, offset=0)
    await message.answer(
        MESSAGES.get("genre_result", f"Подборка жанра {genre_query}:") + "\n" + "\n".join(pretty),
        reply_markup=navigation_keyboard(has_more=len(top_in_genre) > BATCH_SIZE),
    )


@recommendations_router.callback_query(F.data.in_(["more", "restart"]))
async def handle_more_restart(query: CallbackQuery) -> None:
    """Обработка кнопок «еще» и «начать заново»."""
    await query.answer()
    user_id = query.from_user.id
    action = query.data

    if action == "restart":
        USER_RECS.pop(user_id, None)
        USER_PTR.pop(user_id, None)
        await query.message.answer(
            MESSAGES.get("restart_prompt", "Начнем сначала. Жми /start или /recommend."),
        )
        return

    recs = USER_RECS.get(user_id, [])
    if not recs:
        await query.message.answer(MESSAGES.get("error_no_recs", "Пока нечего добавить."))
        return

    start = USER_PTR.get(user_id, 0) + BATCH_SIZE
    batch = recs[start : start + BATCH_SIZE]
    if not batch:
        await query.message.answer(MESSAGES.get("error_no_recs", "Все рекомендации уже показал."))
        return

    USER_PTR[user_id] = start
    pretty = _format_batch(batch, offset=start)
    await query.message.answer(
        "\n".join(pretty),
        reply_markup=navigation_keyboard(has_more=len(recs) > start + BATCH_SIZE),
    )
