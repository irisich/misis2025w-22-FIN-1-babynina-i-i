from aiogram import F, Router, types
from aiogram.filters import Command

from config import MESSAGES
from keyboards.reply import main_menu_keyboard

start_router = Router()


@start_router.message(Command("start"))
async def handle_start(message: types.Message) -> None:
    """приветствовать пользователя и показать главное меню."""
    greeting = MESSAGES["greeting"]
    hint = MESSAGES["greeting_line2"]
    await message.answer(f"{greeting}\n{hint}", reply_markup=main_menu_keyboard())


@start_router.message(Command("help"))
@start_router.message(F.text.lower() == "помощь")
async def handle_help(message: types.Message) -> None:
    """показать справочную информацию пользователю"""
    await message.answer(MESSAGES["help_text"])


@start_router.message(F.text.lower() == "получить рекомендации")
async def shortcut_recommend(message: types.Message) -> None:
    """менюшка для получения рекомендаций."""
    await message.answer(MESSAGES["shortcut_recommend"])


@start_router.message(F.text.lower() == "выбрать жанр")
async def shortcut_genre(message: types.Message) -> None:
    """менюшка для выбора жанра."""
    await message.answer(MESSAGES["shortcut_genre"])
