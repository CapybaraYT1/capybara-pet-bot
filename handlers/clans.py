from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db
from keyboards import (
    main_menu, clans_menu, my_clan_member_inline,
    my_clan_owner_inline, invite_inline, confirm_inline, back_button
)

router = Router()

class ClanState(StatesGroup):
    creating_name = State()
    donating = State()
    inviting = State()

@router.message(F.text == "👥 Кланы")
async def clans_menu_handler(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Сначала запусти бота командой /start")
        return
    await message.answer("👥 <b>Меню кланов</b>", reply_markup=clans_menu(), parse_mode="HTML")

# ─── МОЙ КЛАН ───────────────────────────────────────────────
@router.message(F.text == "🏠 Мой клан")
async def my_clan(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user or not user['clan_id']:
        await message.answer(
            "😔 Ты не состоишь ни в одном клане.\n"
            "Создай свой или подожди приглашения!",
        )
        return

    clan = await db.get_clan(user['clan_id'])
    members = await db.get_clan_members(user['clan_id'])
    role = "👑 Создатель" if user['clan_role'] == 'owner' else "👤 Участник"

    members_text = "\n".join([
        f"{'👑' if m['clan_role'] == 'owner' else '👤'} {m['username'] or 'Игрок'}"
        for m in members
    ])

    keyboard = my_clan_owner_inline(clan['id']) if user['clan_role'] == 'owner' else my_clan_member_inline(clan['id'])

    await message.answer(
        f"🏰 <b>{clan['name']}</b>\n"
        f"{'─' * 20}\n"
        f"🎖 Твоя роль: <b>{role}</b>\n"
        f"👥 Участников: <b>{len(members)}</b>\n"
        f"💰 Казна: <b>{clan['treasury']} монет</b>\n"
        f"{'─' * 20}\n"
        f"<b>Состав:</b>\n{members_text}",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

# ─── СОЗДАТЬ КЛАН ───────────────────────────────────────────
@router.message(F.text == "➕ Создать клан")
async def create_clan_start(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    if not user:
        return
    if user['clan_id']:
        await message.answer("⚠️ Ты уже состоишь в клане!")
        return
    if user['coins'] < 200:
        await message.answer(
            f"💸 Недостаточно монет!\n"
            f"Нужно: <b>200 монет</b>\n"
            f"У тебя: <b>{user['coins']} монет</b>",
            parse_mode="HTML"
        )
        return

    await state.set_state(ClanState.creating_name)
    await message.answer(
        "🏰 <b>Создание клана</b>\n\n"
        "Придумай название для своего клана:\n"
        "<i>(от 3 до 20 символов)</i>",
        reply_markup=back_button(),
        parse_mode="HTML"
    )

@router.message(ClanState.creating_name)
async def create_clan_finish(message: Message, state: FSMContext):
    if message.text == "◀️ Назад":
        await state.clear()
        await message.answer("👥 Меню кланов", reply_markup=clans_menu())
        return

    name = message.text.strip()
    if len(name) < 3 or len(name) > 20:
        await message.answer("⚠️ Название должно быть от 3 до 20 символов!")
        return

    existing = await db.get_clan_by_name(name)
    if existing:
        await message.answer("❌ Клан с таким названием уже существует!")
        return

    clan = await db.create_clan(name, message.from_user.id)
    await state.clear()
    await message.answer(
        f"🎉 Клан <b>{name}</b> успешно создан!\n"
        f"💸 Списано: <b>200 монет</b>\n\n"
        f"Приглашай друзей через меню клана!",
        reply_markup=clans_menu(),
        parse_mode="HTML"
    )

# ─── ПРИГЛАШЕНИЯ ────────────────────────────────────────────
@router.message(F.text == "📨 Приглашения")
async def show_invites(message: Message):
    invites = await db.get_invites(message.from_user.id)
    if not invites:
        await message.answer("📭 У тебя нет входящих приглашений в кланы.")
        return

    for invite in invites:
        await message.answer(
            f"📨 <b>Приглашение в клан</b>\n"
            f"{'─' * 20}\n"
            f"🏰 Клан: <b>{invite['clan_name']}</b>\n"
            f"👤 Пригласил: <b>{invite['inviter_name']}</b>",
            reply_markup=invite_inline(invite['id']),
            parse_mode="HTML"
        )

# ─── ТОП КЛАНОВ ─────────────────────────────────────────────
@router.message(F.text == "👑 Топ кланов")
async def top_clans(message: Message):
    clans = await db.get_top_clans()
    if not clans:
        await message.answer("😔 Кланов пока нет. Создай первый!")
        return

    text = "👑 <b>Топ кланов</b>\n" + "─" * 20 + "\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, clan in enumerate(clans):
        medal = medals[i] if i < 3 else f"{i+1}."
        text += f"{medal} <b>{clan['name']}</b> — {clan['member_count']} участн.\n"

    await message.answer(text, parse_mode="HTML")

# ─── CALLBACK КНОПКИ ────────────────────────────────────────
@router.callback_query(F.data.startswith("leave_clan_"))
async def leave_clan_confirm(callback: CallbackQuery):
    clan_id = int(callback.data.split("_")[-1])
    await callback.message.answer(
        "⚠️ Ты уверен что хочешь покинуть клан?",
        reply_markup=confirm_inline(f"leave_{clan_id}")
    )
    await callback.answer()

@router.callback_query(F.data.startswith("delete_clan_"))
async def delete_clan_confirm(callback: CallbackQuery):
    clan_id = int(callback.data.split("_")[-1])
    await callback.message.answer(
        "⚠️ Удалить клан? Все участники будут исключены!",
        reply_markup=confirm_inline(f"delete_{clan_id}")
    )
    await callback.answer()

@router.callback_query(F.data.startswith("donate_"))
async def donate_start(callback: CallbackQuery, state: FSMContext):
    clan_id = int(callback.data.split("_")[1])
    await state.update_data(clan_id=clan_id)
    await state.set_state(ClanState.donating)
    await callback.message.answer(
        "💰 Сколько монет хочешь пожертвовать в казну клана?",
        reply_markup=back_button()
    )
    await callback.answer()

@router.message(ClanState.donating)
async def donate_finish(message: Message, state: FSMContext):
    if message.text == "◀️ Назад":
        await state.clear()
        await message.answer("👥 Меню кланов", reply_markup=clans_menu())
        return

    try:
        amount = int(message.text.strip())
        if amount <= 0:
            raise ValueError
    except:
        await message.answer("⚠️ Введи корректное число монет!")
        return

    user = await db.get_user(message.from_user.id)
    if user['coins'] < amount:
        await message.answer(f"💸 Недостаточно монет! У тебя: <b>{user['coins']}</b>", parse_mode="HTML")
        return

    data = await state.get_data()
    await db.donate_to_clan(message.from_user.id, data['clan_id'], amount)
    await state.clear()
    await message.answer(
        f"✅ Ты пожертвовал <b>{amount} монет</b> в казну клана!",
        reply_markup=clans_menu(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("invite_"))
async def invite_start(callback: CallbackQuery, state: FSMContext):
    clan_id = int(callback.data.split("_")[1])
    await state.update_data(clan_id=clan_id)
    await state.set_state(ClanState.inviting)
    await callback.message.answer(
        "📨 Введи <b>username</b> или <b>ID</b> игрока которого хочешь пригласить:",
        reply_markup=back_button(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(ClanState.inviting)
async def invite_finish(message: Message, state: FSMContext):
    if message.text == "◀️ Назад":
        await state.clear()
        await message.answer("👥 Меню кланов", reply_markup=clans_menu())
        return

    text = message.text.strip().replace("@", "")
    data = await state.get_data()

    target = None
    try:
        target = await db.get_user(int(text))
    except:
        pass

    if not target:
        await message.answer("❌ Игрок не найден. Убедись что он уже запустил бота!")
        return

    if target['clan_id']:
        await message.answer("⚠️ Этот игрок уже состоит в клане!")
        return

    if target['user_id'] == message.from_user.id:
        await message.answer("⚠️ Нельзя пригласить самого себя!")
        return

    success = await db.create_invite(data['clan_id'], target['user_id'], message.from_user.id)
    await state.clear()

    if success:
        clan = await db.get_clan(data['clan_id'])
        try:
            await message.bot.send_message(
                target['user_id'],
                f"📨 Тебя приглашают в клан <b>{clan['name']}</b>!\n"
                f"Проверь раздел 👥 Кланы → 📨 Приглашения",
                parse_mode="HTML"
            )
        except:
            pass
        await message.answer(
            f"✅ Приглашение отправлено игроку <b>{target['username']}</b>!",
            reply_markup=clans_menu(),
            parse_mode="HTML"
        )
    else:
        await message.answer("⚠️ Этот игрок уже получил приглашение!", reply_markup=clans_menu())

@router.callback_query(F.data.startswith("confirm_"))
async def confirm_action(callback: CallbackQuery):
    action = callback.data.replace("confirm_", "")
    user = await db.get_user(callback.from_user.id)

    if action.startswith("leave_"):
        await db.leave_clan(callback.from_user.id)
        await callback.message.answer("✅ Ты покинул клан.", reply_markup=clans_menu())

    elif action.startswith("delete_"):
        clan_id = int(action.split("_")[1])
        clan = await db.get_clan(clan_id)
        if clan and clan['owner_id'] == callback.from_user.id:
            await db.delete_clan(clan_id)
            await callback.message.answer("🗑 Клан удалён.", reply_markup=clans_menu())

    await callback.answer()

@router.callback_query(F.data == "cancel_action")
async def cancel_action(callback: CallbackQuery):
    await callback.message.answer("❌ Отменено.", reply_markup=clans_menu())
    await callback.answer()

@router.callback_query(F.data.startswith("accept_invite_"))
async def accept_invite(callback: CallbackQuery):
    invite_id = int(callback.data.split("_")[-1])
    user = await db.get_user(callback.from_user.id)
    if user['clan_id']:
        await callback.answer("⚠️ Ты уже в клане!", show_alert=True)
        return
    success = await db.accept_invite(invite_id, callback.from_user.id)
    if success:
        await callback.message.answer("✅ Ты вступил в клан!", reply_markup=clans_menu())
    else:
        await callback.message.answer("❌ Приглашение устарело.")
    await callback.answer()

@router.callback_query(F.data.startswith("decline_invite_"))
async def decline_invite(callback: CallbackQuery):
    invite_id = int(callback.data.split("_")[-1])
    await db.decline_invite(invite_id, callback.from_user.id)
    await callback.message.answer("❌ Приглашение отклонено.")
    await callback.answer()
