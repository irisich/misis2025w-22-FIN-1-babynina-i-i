from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import MESSAGES


def rating_keyboard(item_id: str) -> InlineKeyboardMarkup:
    """Inline keyboard with rating options 1-5 for a given item."""
    buttons = [
        [InlineKeyboardButton(text=str(score), callback_data=f"rate:{item_id}:{score}")]
        for score in range(1, 6)
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def navigation_keyboard(has_more: bool = False) -> InlineKeyboardMarkup:
    """Navigation keyboard for paging or restarting."""
    rows = []
    if has_more:
        rows.append(
            [InlineKeyboardButton(text=MESSAGES.get("more_button", "Еще"), callback_data="more")]
        )
    rows.append(
        [InlineKeyboardButton(text=MESSAGES.get("restart_button", "Начать заново"), callback_data="restart")]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)
