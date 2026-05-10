import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
import database as db
from keyboards import main_menu, cases_menu, confirm_case, inventory_equip

router = Router()

WEAPONS = [
    ("???",       "❓", 30, 0.5),
    ("Огнемёт",   "🔥", 20, 4.5),
    ("Арбалет",   "🏹", 15, 10),
    ("Пистолет",  "🔫", 10, 35),
    ("Меч",       "⚔️",  5, 50),
]

ARMORS = [
    ("???",          "❓", 30, 0.5),
    ("Щит",          "🛡", 20, 4.5),
    ("Шлем",         "⛑", 15, 10),
    ("Бронежилет",   "🦺", 10, 35),
    ("Браслет",      "📿",  5, 50),
]

def roll_item(items):
    names = [i[0] for i in items]
    emojis = [i[1] for i in items]
    bonuses = [i[2] for i in items]
    weights = [i[3] for i in items]
    idx = random.choices(range(len(items)), weights=weights, k=1)[0]
    return names[idx], emojis[idx], bonuses[idx]

@router.message(F.text == "🎁 Кейсы")
async def cases_handler(message: Message):
    user = db.get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Сначала запусти /start")
        return
    await message.answer(
        f"🎁 <b>Кейсы</b>\n"
        f"{'─' * 20}\n"
        f"💰 Твой баланс: <b>{user['coins']} монет</b>\n\n"
        f"Выбери кейс для открытия:",
        reply_markup=cases_menu(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "case_weapon")
async def case_weapon_confirm(callback: CallbackQuery):
    user = db.get_user(callback.from_user.id)
    if user['coins'] < 1000:
        await callback.answer(f"❌ Нужно 1000 монет! У тебя {user['coins']}", show_alert=True)
        return
    await callback.message.answer(
        "⚔️ <b>Кейс оружия — 1000 монет</b>\n\n"
        "Возможные предметы (от редкого к частому):\n"
        "❓ ??? — 0.5% (+30% атаки)\n"
        "🔥 Огнемёт — 4.5% (+20% атаки)\n"
        "🏹 Арбалет — 10% (+15% атаки)\n"
        "🔫 Пистолет — 35% (+10% атаки)\n"
        "⚔️ Меч — 50% (+5% атаки)\n\n"
        "Открыть кейс?",
        reply_markup=confirm_case("weapon"),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "case_armor")
async def case_armor_confirm(callback: CallbackQuery):
    user = db.get_user(callback.from_user.id)
    if user['coins'] < 1000:
        await callback.answer(f"❌ Нужно 1000 монет! У тебя {user['coins']}", show_alert=True)
        return
    await callback.message.answer(
        "🛡 <b>Кейс брони — 1000 монет</b>\n\n"
        "Возможные предметы (от редкого к частому):\n"
        "❓ ??? — 0.5% (+30% здоровья)\n"
        "🛡 Щит — 4.5% (+20% здоровья)\n"
        "⛑ Шлем — 10% (+15% здоровья)\n"
        "🦺 Бронежилет — 35% (+10% здоровья)\n"
        "📿 Браслет — 50% (+5% здоровья)\n\n"
        "Открыть кейс?",
        reply_markup=confirm_case("armor"),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "open_weapon")
async def open_weapon(callback: CallbackQuery):
    user = db.get_user(callback.from_user.id)
    if user['coins'] < 1000:
        await callback.answer("❌ Недостаточно монет!", show_alert=True)
        return
    db.add_coins(callback.from_user.id, -1000)
    name, emoji, bonus = roll_item(WEAPONS)
    db.add_item(callback.from_user.id, "weapon", name, emoji, bonus)
    await callback.message.answer(
        f"🎁 Кейс оружия открыт!\n\n"
        f"Выпало: {emoji} <b>{name}</b>\n"
        f"💥 +{bonus}% к атаке\n\n"
        f"Предмет добавлен в 🎒 Инвентарь",
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "open_armor")
async def open_armor(callback: CallbackQuery):
    user = db.get_user(callback.from_user.id)
    if user['coins'] < 1000:
        await callback.answer("❌ Недостаточно монет!", show_alert=True)
        return
    db.add_coins(callback.from_user.id, -1000)
    name, emoji, bonus = roll_item(ARMORS)
    db.add_item(callback.from_user.id, "armor", name, emoji, bonus)
    await callback.message.answer(
        f"🎁 Кейс брони открыт!\n\n"
        f"Выпало: {emoji} <b>{name}</b>\n"
        f"🛡 +{bonus}% к здоровью\n\n"
        f"Предмет добавлен в 🎒 Инвентарь",
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "cancel_case")
async def cancel_case(callback: CallbackQuery):
    await callback.message.answer("❌ Отменено.")
    await callback.answer()

# ─── ИНВЕНТАРЬ ──────────────────────────────────────────────
@router.message(F.text == "🎒 Инвентарь")
async def inventory_handler(message: Message):
    items = db.get_inventory(message.from_user.id)
    if not items:
        await message.answer("🎒 Инвентарь пуст.\n\nОткрывай кейсы чтобы получить предметы!")
        return

    user = db.get_user(message.from_user.id)
    await message.answer(
        f"🎒 <b>Инвентарь</b>\n"
        f"{'─' * 20}\n"
        f"⚔️ Оружие: <b>{user['equipped_weapon'] or 'Нет'}</b>\n"
        f"🛡 Броня: <b>{user['equipped_armor'] or 'Нет'}</b>\n"
        f"{'─' * 20}\n"
        f"Нажми на предмет чтобы надеть:",
        parse_mode="HTML"
    )

    for item in items:
        type_emoji = "⚔️" if item['item_type'] == 'weapon' else "🛡"
        stat = "атаки" if item['item_type'] == 'weapon' else "здоровья"
        await message.answer(
            f"{item['item_emoji']} <b>{item['item_name']}</b>\n"
            f"{type_emoji} +{item['bonus']}% к {stat}",
            reply_markup=inventory_equip(item['id'], item['item_type']),
            parse_mode="HTML"
        )

@router.callback_query(F.data.startswith("equip_"))
async def equip_handler(callback: CallbackQuery):
    parts = callback.data.split("_")
    item_id = int(parts[1])
    item = db.equip_item(callback.from_user.id, item_id)
    if item:
        stat = "атаки" if item['item_type'] == 'weapon' else "здоровья"
        await callback.message.answer(
            f"✅ {item['item_emoji']} <b>{item['item_name']}</b> надет!\n"
            f"+{item['bonus']}% к {stat}",
            parse_mode="HTML"
        )
    await callback.answer()
