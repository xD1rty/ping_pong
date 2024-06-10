from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


game_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="◀️", callback_data="left"), InlineKeyboardButton(text="▶️", callback_data="right")],
    [InlineKeyboardButton(text="Stop", callback_data="stop")]
])

get_opponent_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Игра с ИИ 🤖", callback_data="game_with_ai")],
    [InlineKeyboardButton(text="Игра с человеком 🫂", callback_data="game_with_people")]
])

complexity_ai_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Легко", callback_data="easy")],
    [InlineKeyboardButton(text="Средне", callback_data="middle")],
    [InlineKeyboardButton(text="Сложно", callback_data="hard")],
])