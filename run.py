import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.database.models import async_main
from app.handlers import router
from config import TOKEN

bot = Bot(token=TOKEN)  # создаем экземпляр класса БОТ с нашим токеном
dp = Dispatcher()


async def main():  # пишем функцию для старта поллинга (регулярного опроса сервера)
    await async_main()
    bot = Bot(token=TOKEN)  # создаем экземпляр класса БОТ с нашим токеном
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    """можно убрать логгирование,
    т.к. оно замедляет работоспособность бота при большом потоке"""
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
