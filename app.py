import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from db import init
from aiogram.enums import ParseMode

from handlers.menu import menu_router
from handlers.start import start_bot
from handlers.game import game_router
from middlewares.user import UserMiddleware

# Функция для инициализации и старта бота

async def main():
    await init()
    logging.basicConfig(level=logging.INFO) # Логирование

    bot = Bot(token="", parse_mode=ParseMode.MARKDOWN) # Сам бот
    dp = Dispatcher() # Диспетчер для Backend бота (я про Backend самой программы))

    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())
    dp.message.register(start_bot, CommandStart())
    dp.include_router(menu_router)
    dp.include_router(game_router)

    # Проверка ошибок при старте бота
    try:
        await dp.start_polling(bot) # Действие, запускающие все входящие запросы
    except Exception as _e:
        logging.error(f"Your bot can't start working due to an error: {_e}") # Логирование ошибки, которая может произойти при запуске бота
    finally: # Метод, выполняющий все действия при завершении работы остальных методов
        await bot.session.close()
        logging.info("The bot closed its session. Thanks for using my code)")

if __name__ == "__main__":
    asyncio.run(main()) # Запуск ассинхронной функции
