# f"*Профиль*\n\n"
#                          f"Имя: *{message.from_user.username}*\n"
#                          f"ID:  *{message.from_user.id}*\n"

from unittest.mock import AsyncMock

import pytest

from handlers.menu import send_profile
from keyboards.markup import menu
from db.models import Users

@pytest.mark.asyncio
async def test_profile_bot():
    mock = AsyncMock()
    user = [Users(id=0, username="test")]
    await send_profile(mock, user)
    mock.answer.assert_called_with(f"*Профиль*\n\n"
                         f"Имя: *{mock.from_user.username}*\n"
                         f"ID:  *{mock.from_user.id}*\n"
                         f"Игровой рейтинг: *{user[0].rating}*\n")