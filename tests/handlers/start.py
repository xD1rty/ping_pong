from unittest.mock import AsyncMock

import pytest

from handlers.start import start_bot
from keyboards.markup import menu

@pytest.mark.asyncio
async def test_start_bot():
    mock = AsyncMock()
    await start_bot(mock)
    mock.answer.assert_called_with(f"Привет, мой дорогой {mock.from_user.first_name}!\n\n"
                         f"Я - бот для игры в пинг-понг прям внутри телеги\n"
                         f"Правила игры простые - просто туда-сюда тарелку и все)", reply_markup=menu)

