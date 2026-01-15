from aiogram import Bot, Dispatcher
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if TOKEN is None:
    raise ValueError("Токен TELEGRAM_BOT_TOKEN не найден в переменных окружения.")

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    print("Бот запущен и база готова!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
