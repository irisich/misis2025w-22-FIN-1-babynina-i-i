from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from pandas import Series

from config import BOT_DIALOGS
from keyboards.create_recs import after_recs_created_keyboard
from recommendation.item_based_cf import full_pipeline
from states.navigation_states import NavigationStates

router = Router()

@router.message(NavigationStates.create_recs)
async def create_recs_message_handler(message : Message, state : FSMContext):

    """отправляет сообщение при переходе во вкладку создания рекомендации объясняющее как это делать"""

    await message.answer(
        BOT_DIALOGS["create_recs"]
    )

    await state.set_state(NavigationStates.create_recs_process_movie)




@router.message(NavigationStates.create_recs_process_movie)
async def create_recs_process_handler(message : Message, state : FSMContext):
    """
    отвечает за создание самой рекомендации по введенному названию фильма
    """

    movie_name=message.text
    try:
        recs = create_recs(movie_name)
        print(recs)
        await message.answer(
            create_message_from_recs(recs),
            reply_markup=after_recs_created_keyboard()
        )
        await state.set_state(NavigationStates.menu)
    except IndexError as e:
        print(e)
        await message.answer(
            BOT_DIALOGS["invalid_input"],
            reply_markup = after_recs_created_keyboard()
        )



def create_message_from_recs(sr : Series) -> str:
    """форматирование корреляций для вывода пользователю"""
    result = BOT_DIALOGS["recs_generated"]
    i = 0
    for movie_name in sr.index:
        result += f"{i}. {movie_name}\n"
        i+=1
    return result

def create_recs(movie_name : str) -> Series:
    """функция по созданию таблицы корреляции для конкретного фильма"""
    return full_pipeline(movie_name)