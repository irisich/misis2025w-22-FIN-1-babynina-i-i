from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def start_dialog_keyboard() -> ReplyKeyboardMarkup:
    """клавиатура для начала общения с ботом"""
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text="Начать"))

    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)