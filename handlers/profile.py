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

    days = (datetime.now() - user['created_at']).days
    age_text = f"{days} дн." if days > 0 else "Сегодня"

    await message.answer(
        f"👤 <b>Профиль</b>\n"
        f"{'─' * 20}\n"
        f"🐾 Капибара: <b>{user['capybara_name']}</b>\n"
        f"📅 Возраст питомца: <b>{age_text}</b>\n"
        f"💰 Монеты: <b>{user['coins']}</b>\n"
        f"🎟 Рефералов: <b>{user['referrals_count']}</b>\n"
        f"👥 Клан: <b>{clan_text}</b>\n"
        f"{'─' * 20}\n"
        f"🆔 ID: <code>{message.from_user.id}</code>",
        reply_markup=profile_inline(message.from_user.id),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "rename_capy")
async def rename_capy_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RenameState.waiting_new_name)
    await callback.message.answer(
        "✏️ Введи новое имя для своей капибары:",
        reply_markup=back_button()
    )
    await callback.answer()

@router.message(RenameState.waiting_new_name)
async def rename_capy_finish(message: Message, state: FSMContext):
    if message.text == "◀️ Назад":
        await state.clear()
        await message.answer("🏠 Главное меню", reply_markup=main_menu())
        return

    name = message.text.strip()
    if len(name) < 2 or len(name) > 20:
        await message.answer("⚠️ Имя должно быть от 2 до 20 символов!")
        return

    db.update_capybara_name(message.from_user.id, name)
    await state.clear()
    await message.answer(
        f"✅ Капибара переименована в <b>{name}</b>!",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery):
    await callback.message.answer("🏠 Главное меню", reply_markup=main_menu())
    await callback.answer()
