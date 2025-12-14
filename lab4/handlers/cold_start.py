from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import BOT_DIALOGS
from handlers.main_menu import main_menu_handler
from keyboards.cold_start import cold_start_keyboard, end_cold_start_keyboard
from states.navigation_states import NavigationStates

router = Router()

@router.message(NavigationStates.cold_start_message)
async def cold_start_message(message: Message, state: FSMContext):

    await message.answer(
        BOT_DIALOGS['cold_start'],
        reply_markup=cold_start_keyboard()
    )

    await state.set_state(NavigationStates.cold_start_process)

@router.message(NavigationStates.cold_start_process, F.text == "Стоп")
async def cold_start_stop(message: Message, state: FSMContext):


    user_data = await state.get_data()
    items = user_data.get('items', [])
    if not items:
        await message.answer("Ты не выбрал ни одного фильма! Пожалуйста выбери хотя бы один")
        return
    else:
        await message.answer(
            "выбор фильмов завершен",
            reply_markup = end_cold_start_keyboard())

        await state.set_state(NavigationStates.menu)


@router.message(NavigationStates.cold_start_process)
async def cold_start_process(message: Message, state: FSMContext):

    user_data = await state.get_data()
    items = user_data.get('items', [])
    items.append(message.text)
    await state.update_data(items=items)
    await message.answer(
        "Фильм учтен",
        reply_markup=cold_start_keyboard()
    )





