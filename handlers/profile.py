from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import database as db
from keyboards import main_menu, profile_inline, back_button

router = Router()

class RenameState(StatesGroup):
    waiting_new_name = State()

@router.message(F.text == "👤 Профиль")
async def show_profile(message: Message):
    user = db.get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Сначала запусти бота командой /start")
        return

    clan_text = "Без клана"
    if user['clan_id']:
        clan = db.get_clan(user['clan_id'])
        if clan:
            role = "👑 Создатель" if user['clan_role'] == 'owner' else "👤 Участник"
            clan_text = f"{clan['name']} ({role})"

    hours = int((datetime.now() - user['created_at']).total_seconds() / 3600)
    attack, health = db.get_stats(user['user_id'])

    weapon_text = user['equipped_weapon'] or "Нет"
    armor_text = user['equipped_armor'] or "Нет"

    await message.answer(
        f"👤 <b>Профиль</b>\n"
        f"{'─' * 20}\n"
        f"🐾 Капибара: <b>{user['capybara_name']}</b>\n"
        f"⏱ Возраст: <b>{hours} ч.</b>\n"
        f"💰 Монеты: <b>{user['coins']}</b>\n"
        f"🎟 Рефералов: <b>{user['referrals_count']}</b>\n"
        f"⚔️ Побед: <b>{user['battles_won']}</b>\n"
        f"👥 Клан: <b>{clan_text}</b>\n"
        f"{'─' * 20}\n"
        f"⚔️ Оружие: <b>{weapon_text}</b>\n"
        f"🛡 Броня: <b>{armor_text}</b>\n"
        f"💥 Атака: <b>{attack}</b> | ❤️ Здоровье: <b>{health}</b>",
        reply_markup=profile_inline(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "rename_capy")
async def rename_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RenameState.waiting_new_name)
    await callback.message.answer("✏️ Введи новое имя капибары:\n<i>(от 3 до 12 символов)</i>", reply_markup=back_button(), parse_mode="HTML")
    await callback.answer()

@router.message(RenameState.waiting_new_name)
async def rename_finish(message: Message, state: FSMContext):
    if message.text == "◀️ Назад":
        await state.clear()
        await message.answer("🏠 Главное меню", reply_markup=main_menu())
        return
    name = message.text.strip()
    if len(name) < 3 or len(name) > 12:
        await message.answer("⚠️ Имя должно быть от 3 до 12 символов!")
        return
    if db.get_user_by_capybara_name(name):
        await message.answer("❌ Это имя уже занято!")
        return
    db.update_capybara_name(message.from_user.id, name)
    await state.clear()
    await message.answer(f"✅ Капибара переименована в <b>{name}</b>!", reply_markup=main_menu(), parse_mode="HTML")

@router.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery):
    await callback.message.answer("🏠 Главное меню", reply_markup=main_menu())
    await callback.answer()
