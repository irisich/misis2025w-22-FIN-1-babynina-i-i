from aiogram import F, Router, types
from aiogram.filters import Command

from config import MESSAGES
from keyboards.reply import main_menu_keyboard

start_router = Router()


@start_router.message(Command("start"))
async def handle_start(message: types.Message) -> None:
    """Greet the user and show the main menu."""
    greeting = MESSAGES.get("greeting", "Привет! Я бот-рекомендатор фильмов.")
    hint = MESSAGES.get("greeting_line2", "Выбери, что хочешь сделать.")
    await message.answer(f"{greeting}\n{hint}", reply_markup=main_menu_keyboard())


@start_router.message(Command("help"))
@start_router.message(F.text.lower() == "помощь")
async def handle_help(message: types.Message) -> None:
    """Short help text."""
    await message.answer(
        "Напиши название фильма после команды /recommend, и я подберу похожие.\n"
        "Например: /recommend Матрица\n"
        "Можно выбрать жанр: /genre Комедия"
    )


@start_router.message(F.text.lower() == "получить рекомендации")
async def shortcut_recommend(message: types.Message) -> None:
    """Menu shortcut to recommendations."""
    await message.answer("Напиши /recommend название фильма, и я подберу похожие.")


@start_router.message(F.text.lower() == "выбрать жанр")
async def shortcut_genre(message: types.Message) -> None:
    """Menu shortcut to genre recommendations."""
    await message.answer("Напиши /genre жанр. Например: /genre Комедия")
