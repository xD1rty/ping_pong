from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from db.models import Users


class UserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: dict[str, Any],
    ):
        if not event.from_user.username:
            return await event.answer("Вы должны поставить юзернейм для работы с ботом!")
        user, _ = await Users.get_or_create(id=event.from_user.id, username=event.from_user.username)
        data['user'] = user
        return await handler(event, data)

