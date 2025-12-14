import logging
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware


class LoggingMiddleware(BaseMiddleware):
    """Simple middleware to log incoming events."""

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        logging.getLogger("bot").info("incoming event: %s", type(event).__name__)
        return await handler(event, data)
