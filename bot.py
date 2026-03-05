import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import db

# Импорт хендлеров
from handlers import start, tasks, progress, leaderboard, journal, settings

logging.basicConfig(level=logging.INFO)

async def main():
    # Инициализация базы данных
    await db.init_db()
    
    # Создание бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрация роутеров
    dp.include_router(start.router)
    dp.include_router(tasks.router)
    dp.include_router(progress.router)
    dp.include_router(leaderboard.router)
    dp.include_router(journal.router)
    dp.include_router(settings.router)
    
    # Удаление вебхука и запуск polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())