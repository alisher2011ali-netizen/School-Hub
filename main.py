from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncio
import os
from dotenv import load_dotenv

from database import Database
from handlers import router as user_router

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if TOKEN is None:
    raise ValueError("Токен TELEGRAM_BOT_TOKEN не найден в переменных окружения.")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
db = Database("school_hub.db")


async def main():
    await db.create_tables()
    await db.seed_subjects()

    dp.include_router(user_router)

    print("Бот запущен и база готова!")
    await dp.start_polling(bot, db=db)


if __name__ == "__main__":
    asyncio.run(main())
