import asyncio
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from database import init_db
from handlers import start, profile, referrals, clans, work_shop
from profanity import contains_bad_words

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Сначала все основные роутеры
dp.include_router(start.router)
dp.include_router(profile.router)
dp.include_router(referrals.router)
dp.include_router(clans.router)
dp.include_router(work_shop.router)

# Фильтр мата — последним, чтобы не перехватывал команды
profanity_router = Router()

@profanity_router.message()
async def profanity_filter(message: Message):
    if message.text and contains_bad_words(message.text):
        try:
            await message.delete()
        except:
            pass
        await message.answer("🚫 Пожалуйста, не используй нецензурные слова!")

dp.include_router(profanity_router)

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
