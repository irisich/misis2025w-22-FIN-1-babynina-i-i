from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def cold_start_keyboard() -> ReplyKeyboardMarkup:

    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text="Стоп"))

    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def end_cold_start_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text="Отлично!"))

    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)