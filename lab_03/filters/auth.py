from typing import Iterable, Set
from aiogram.filters import BaseFilter
from aiogram.types import Message


class AdminFilter(BaseFilter):
    """Allow messages only from configured admin ids."""

    def __init__(self, admin_ids: Iterable[int]):
        self.admin_ids: Set[int] = {int(i) for i in admin_ids}

    async def __call__(self, message: Message) -> bool:
        if message.from_user is None:
            return False
        return message.from_user.id in self.admin_ids
