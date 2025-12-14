from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config import MAIN_MENU_OPTIONS


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """клавиатура для выбора в меню"""
    builder = ReplyKeyboardBuilder()

    for option in MAIN_MENU_OPTIONS:
        builder.add(KeyboardButton(text=option))

    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)