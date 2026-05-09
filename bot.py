import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from database import init_db
from handlers import start, profile, referrals, clans, work_shop
from profanity import contains_bad_words

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(start.router)
dp.include_router(profile.router)
dp.include_router(referrals.router)
dp.include_router(clans.router)
dp.include_router(work_shop.router)

@dp.message()
async def profanity_filter(message: Message):
    if message.text and contains_bad_words(message.text):
        await message.delete()
        await message.answer("🚫 Пожалуйста, не используй нецензурные слова!")

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
