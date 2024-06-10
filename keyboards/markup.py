from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Играть")],
    [KeyboardButton(text="Глобальный рейтинг"), KeyboardButton(text="Профиль")]
])

