from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню с кнопками для получения рекомендаций."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Получить рекомендации")],
            [KeyboardButton(text="Выбрать жанр")],
            [KeyboardButton(text="Помощь")],
        ],
        resize_keyboard=True,
    )


def cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
