from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import BOT_DIALOGS
from keyboards.start_dialog import start_dialog_keyboard
from states.navigation_states import NavigationStates

router = Router()

@router.message(CommandStart())
async def start_dialog_handler(message: Message, state: FSMContext):
    """начало диалога с пользователем"""
    await state.clear()
    await state.set_state(NavigationStates.start)

    await message.answer(
        BOT_DIALOGS["start_message"],
        reply_markup = start_dialog_keyboard()
    )
    await state.set_state(NavigationStates.menu)


