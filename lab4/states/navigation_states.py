from aiogram.fsm.state import State, StatesGroup


class NavigationStates(StatesGroup):
    """класс для навигации по диалогам бота"""
    start = State()

    cold_start_message = State()

    cold_start_process = State()

    menu = State()

    score_movie = State()

    create_recs = State()

    create_recs_process_movie = State()