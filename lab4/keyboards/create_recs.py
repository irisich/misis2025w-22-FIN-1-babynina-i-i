from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder




def after_recs_created_keyboard() -> ReplyKeyboardMarkup:
    """клавиатура для возврата в меню"""
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text="Вернуться в меню"))

    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

