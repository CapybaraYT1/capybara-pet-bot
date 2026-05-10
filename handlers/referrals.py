from aiogram import Router, F
from aiogram.types import Message
import database as db

router = Router()

@router.message(F.text == "🎟 Рефералы")
async def show_referrals(message: Message):
    user = db.get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Сначала запусти бота командой /start")
        return
    bot_username = (await message.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start=ref{message.from_user.id}"
    await message.answer(
        f"🎟 <b>Реферальная система</b>\n"
        f"{'─' * 20}\n\n"
        f"🔗 Твоя ссылка:\n<code>{ref_link}</code>\n\n"
        f"👥 Приглашено: <b>{user['referrals_count']}</b> чел.\n\n"
        f"{'─' * 20}\n"
        f"💰 Ты получаешь: <b>+120 монет</b>\n"
        f"🎁 Друг получает: <b>+80 монет</b>\n"
        f"{'─' * 20}\n\n"
        f"📢 Приглашай друзей и богатей вместе с капибарой!",
        parse_mode="HTML"
    )
