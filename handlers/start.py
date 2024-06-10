from aiogram.types import Message
from keyboards.markup import menu

async def start_bot(message: Message):
    await message.answer(f"Привет, мой дорогой {message.from_user.first_name}!\n\n"
                         f"Я - бот для игры в пинг-понг прям внутри телеги\n"
                         f"Правила игры простые - просто туда-сюда тарелку и все)", reply_markup=menu)