from typing import List
from aiogram import Router
from .start import start_router
from .recommendations import recommendations_router


def get_routers() -> List[Router]:
    """возвращает список роутеров для регистрации в основном приложении"""
    return [start_router, recommendations_router]
