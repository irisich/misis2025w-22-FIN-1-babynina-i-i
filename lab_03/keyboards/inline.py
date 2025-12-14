from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import MESSAGES


def navigation_keyboard(has_more: bool = False) -> InlineKeyboardMarkup:
    """ навигационная клавиатура с кнопками 'ещё' и 'начать заново' """
    rows = []
    if has_more:
        rows.append(
            [InlineKeyboardButton(text=MESSAGES["more_button"], callback_data="more")]
        )
    rows.append(
        [InlineKeyboardButton(text=MESSAGES["restart_button"], callback_data="restart")]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)
