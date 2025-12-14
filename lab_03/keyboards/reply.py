from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from config import MESSAGES


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """главное меню с кнопками для получения рекомендаций и выбора жанра."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Давай, зажги мне рекомендации на основе фильма! 🔥🎬")],
            [KeyboardButton(text="Хочу выбрать жанр, обещаю без зумерского трэша 🚫🎮")],
            [KeyboardButton(text="Совсем не вкуриваю, нужна помощь 🤔💡")],
        ],
        resize_keyboard=True,
    )


def cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
