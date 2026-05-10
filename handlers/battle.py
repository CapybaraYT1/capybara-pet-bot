from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db
from keyboards import main_menu, back_button, battle_inline

router = Router()

class BattleState(StatesGroup):
    waiting_username = State()

@router.message(F.text == "⚔️ Бой")
async def battle_menu(message: Message, state: FSMContext):
    user = db.get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Сначала запусти /start")
        return

    can, minutes_left = db.can_battle(message.from_user.id)
    if not can:
        await message.answer(f"⏳ Следующий бой доступен через <b>{minutes_left} мин.</b>", parse_mode="HTML")
        return

    attack, health = db.get_stats(message.from_user.id)
    await state.set_state(BattleState.waiting_username)
    await message.answer(
        f"⚔️ <b>Бой</b>\n"
        f"{'─' * 20}\n"
        f"💥 Твоя атака: <b>{attack}</b>\n"
        f"❤️ Твоё здоровье: <b>{health}</b>\n\n"
        f"Введи <b>username</b> соперника (без @):",
        reply_markup=back_button(),
        parse_mode="HTML"
    )

@router.message(BattleState.waiting_username)
async def battle_challenge(message: Message, state: FSMContext):
    if message.text == "◀️ Назад":
        await state.clear()
        await message.answer("🏠 Главное меню", reply_markup=main_menu())
        return

    username = message.text.strip().replace("@", "")
    target = db.get_user_by_username(username)

    if not target:
        await message.answer("❌ Игрок не найден. Убедись что он запустил бота!")
        return
    if target['user_id'] == message.from_user.id:
        await message.answer("⚠️ Нельзя сражаться с собой!")
        return

    me = db.get_user(message.from_user.id)
    if me['clan_id'] and me['clan_id'] == target['clan_id']:
        await message.answer("⚠️ Нельзя сражаться с соклановцем!")
        return

    can, minutes_left = db.can_battle(target['user_id'])
    if not can:
        await message.answer(f"⚠️ Соперник недавно сражался. Подожди немного!")
        return

    db.create_battle_request(message.from_user.id, target['user_id'])
    await state.clear()

    try:
        my_attack, my_health = db.get_stats(message.from_user.id)
        await message.bot.send_message(
            target['user_id'],
            f"⚔️ Тебя вызвали на бой!\n\n"
            f"Соперник хочет сразиться с твоей капибарой.\n"
            f"Принять вызов?",
            reply_markup=battle_inline(message.from_user.id)
        )
    except:
        pass

    await message.answer(
        f"✅ Вызов отправлен!\nЖди ответа соперника.",
        reply_markup=main_menu()
    )

@router.callback_query(F.data.startswith("battle_accept_"))
async def battle_accept(callback: CallbackQuery):
    challenger_id = int(callback.data.split("_")[-1])
    target_id = callback.from_user.id

    request = db.get_battle_request(target_id)
    if not request or request['challenger_id'] != challenger_id:
        await callback.answer("❌ Вызов устарел!", show_alert=True)
        return

    db.delete_battle_request(target_id)

    c_attack, c_health = db.get_stats(challenger_id)
    t_attack, t_health = db.get_stats(target_id)

    challenger = db.get_user(challenger_id)
    target = db.get_user(target_id)

    c_kills_t = c_attack >= t_health
    t_kills_c = t_attack >= c_health

    if c_kills_t and t_kills_c:
        result = "🤝 Ничья!"
        result_challenger = "🤝 Ничья!"
        result_target = "🤝 Ничья!"
    elif c_kills_t:
        result_challenger = "🏆 Ты победил!"
        result_target = "💀 Ты проиграл!"
        db.record_battle_win(challenger_id)
    elif t_kills_c:
        result_challenger = "💀 Ты проиграл!"
        result_target = "🏆 Ты победил!"
        db.record_battle_win(target_id)
    else:
        result_challenger = "🤝 Ничья!"
        result_target = "🤝 Ничья!"

    db.set_last_battle(challenger_id)
    db.set_last_battle(target_id)

    battle_text = (
        f"⚔️ <b>Результат боя</b>\n"
        f"{'─' * 20}\n"
        f"💥 Атака: <b>{c_attack}</b> vs ❤️ Здоровье: <b>{t_health}</b>\n"
        f"💥 Атака: <b>{t_attack}</b> vs ❤️ Здоровье: <b>{c_health}</b>\n"
        f"{'─' * 20}\n"
    )

    try:
        await callback.bot.send_message(challenger_id, battle_text + result_challenger, parse_mode="HTML")
    except:
        pass

    await callback.message.answer(battle_text + result_target, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("battle_decline_"))
async def battle_decline(callback: CallbackQuery):
    challenger_id = int(callback.data.split("_")[-1])
    db.delete_battle_request(callback.from_user.id)
    try:
        await callback.bot.send_message(challenger_id, "🏳 Соперник отказался от боя.")
    except:
        pass
    await callback.message.answer("🏳 Ты отказался от боя.")
    await callback.answer()

# ─── ЕЖЕДНЕВКА ──────────────────────────────────────────────
@router.message(F.text == "🎀 Ежедневка")
async def daily_handler(message: Message):
    reward, hours_left = db.claim_daily(message.from_user.id)
    if reward == 0:
        await message.answer(f"⏳ Ежедневка уже получена!\nСледующая через <b>{hours_left} ч.</b>", parse_mode="HTML")
        return
    await message.answer(f"🎀 Ежедневная награда!\n\n💰 +<b>{reward} монет</b>", parse_mode="HTML")
