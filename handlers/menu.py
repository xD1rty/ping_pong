from aiogram import Router, F
from aiogram.types import Message
from db.models import Users
menu_router = Router()


@menu_router.message(F.text == "Профиль")
async def send_profile(message: Message, user: Users):
    await message.answer(f"*Профиль*\n\n"
                         f"Имя: *{message.from_user.username}*\n"
                         f"ID:  *{message.from_user.id}*\n"
                         f"Игровой рейтинг: *{user.rating}*\n")

@menu_router.message(F.text == "Глобальный рейтинг")
async def send_global_rating(message: Message, user: Users):
    top_users = await Users.filter().order_by('-rating').limit(10).all()
    text = f"Глобальный рейтинг\n\n"
    for i in range(len(top_users)):
        text += f"{i+1}. {top_users[i].username.replace('_', "\\_")} - {top_users[i].rating}\n"

    await message.answer(f"{text}")