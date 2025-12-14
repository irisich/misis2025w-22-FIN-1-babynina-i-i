from typing import List
from aiogram import Router
from .start import start_router
from .recommendations import recommendations_router


def get_routers() -> List[Router]:
    """Return all routers that should be included in the dispatcher."""
    return [start_router, recommendations_router]
