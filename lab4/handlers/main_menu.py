from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


from config import BOT_DIALOGS, MAIN_MENU_OPTIONS
from keyboards.main_menu import main_menu_keyboard
from states.navigation_states import NavigationStates


router = Router()

@router.message(NavigationStates.menu)
async def main_menu_handler(message: Message, state: FSMContext):
    """обработчик перехода в меню"""
    await message.answer(
        BOT_DIALOGS["main_menu"],
        reply_markup = main_menu_keyboard()
    )

    await state.set_state(NavigationStates.create_recs)

