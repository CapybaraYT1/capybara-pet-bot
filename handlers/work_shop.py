from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
import database as db
from keyboards import main_menu

router = Router()

# ─── РАБОТА ─────────────────────────────────────────────────
def work_menu_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💼 Отправить на работу", callback_data="work_start")],
        [InlineKeyboardButton(text="💰 Забрать заработок", callback_data="work_collect")],
        [InlineKeyboardButton(text="🏠 Забрать с работы", callback_data="work_stop")],
    ])

@router.message(F.text == "💼 Работа")
async def work_menu(message: Message):
    user = db.get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Сначала запусти бота командой /start")
        return

    status = "🟢 На работе" if user['is_working'] else "🔴 Дома"
    await message.answer(
        f"💼 <b>Работа</b>\n"
        f"{'─' * 20}\n"
        f"Статус: {status}\n\n"
        f"⏱ Каждые <b>30 минут</b> капибара приносит от <b>50 до 150 монет</b>\n"
        f"💡 Не забывай забирать заработок!",
        reply_markup=work_menu_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "work_start")
async def work_start(callback: CallbackQuery):
    user = db.get_user(callback.from_user.id)
    if user['is_working']:
        await callback.answer("⚠️ Капибара уже на работе!", show_alert=True)
        return
    db.start_work(callback.from_user.id)
    await callback.message.answer(
        "💼 Капибара отправилась на работу!\n\n"
        "⏱ Возвращайся через <b>30 минут</b> чтобы забрать монеты.",
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "work_collect")
async def work_collect(callback: CallbackQuery):
    user = db.get_user(callback.from_user.id)
    if not user['is_working']:
        await callback.answer("⚠️ Капибара не на работе!", show_alert=True)
        return

    earned, minutes_left = db.collect_work(callback.from_user.id)
    if earned == 0:
        await callback.answer(f"⏳ Подожди ещё {minutes_left} мин.", show_alert=True)
        return

    await callback.message.answer(
        f"💰 Капибара принесла <b>{earned} монет</b>!\n"
        f"Она продолжает работать 💼",
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "work_stop")
async def work_stop(callback: CallbackQuery):
    user = db.get_user(callback.from_user.id)
    if not user['is_working']:
        await callback.answer("⚠️ Капибара и так дома!", show_alert=True)
        return

    earned, _ = db.collect_work(callback.from_user.id)
    db.stop_work(callback.from_user.id)

    text = "🏠 Капибара вернулась домой!"
    if earned > 0:
        text += f"\n💰 Последний заработок: <b>{earned} монет</b>"

    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

# ─── ТАБЛИЦА ЛИДЕРОВ ────────────────────────────────────────
@router.message(F.text == "🏆 Лидеры")
async def leaderboard(message: Message):
    top = db.get_top_users(15)
    if not top:
        await message.answer("😔 Пока никого нет в таблице лидеров.")
        return

    medals = ["🥇", "🥈", "🥉"]
    text = "🏆 <b>Таблица лидеров</b>\n" + "─" * 20 + "\n\n"
    for i, user in enumerate(top):
        medal = medals[i] if i < 3 else f"{i+1}."
        name = user['capybara_name'] or "Капибара"
        owner = user['username'] or "Игрок"
        text += f"{medal} <b>{name}</b> ({owner})\n💰 {user['coins']} монет\n\n"

    await message.answer(text, parse_mode="HTML")

# ─── МАГАЗИН (TELEGRAM STARS) ───────────────────────────────
def shop_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ 1 звезда → 100 монет", callback_data="buy_1")],
        [InlineKeyboardButton(text="⭐ 10 звёзд → 1 200 монет", callback_data="buy_10")],
        [InlineKeyboardButton(text="⭐ 25 звёзд → 3 000 монет", callback_data="buy_25")],
        [InlineKeyboardButton(text="⭐ 100 звёзд → 13 500 монет", callback_data="buy_100")],
        [InlineKeyboardButton(text="⭐ 1000 звёзд → 175 000 монет", callback_data="buy_1000")],
    ])

SHOP_PACKAGES = {
    "buy_1":    (1,    100),
    "buy_10":   (10,   1200),
    "buy_25":   (25,   3000),
    "buy_100":  (100,  13500),
    "buy_1000": (1000, 175000),
}

@router.message(F.text == "💎 Купить монеты")
async def shop_menu(message: Message):
    await message.answer(
        "💎 <b>Магазин монет</b>\n"
        "{'─' * 20}\n\n"
        "Покупай монеты за Telegram Stars ⭐\n"
        "Выбери пакет:",
        reply_markup=shop_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("buy_"))
async def buy_package(callback: CallbackQuery):
    package = SHOP_PACKAGES.get(callback.data)
    if not package:
        await callback.answer()
        return

    stars, coins = package
    await callback.message.answer_invoice(
        title=f"💰 {coins} монет",
        description=f"Покупка {coins} монет для Capybara Pet",
        payload=f"coins_{coins}",
        currency="XTR",
        prices=[LabeledPrice(label=f"{coins} монет", amount=stars)],
    )
    await callback.answer()

@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)

@router.message(F.successful_payment)
async def successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    coins = int(payload.split("_")[1])
    db.add_coins(message.from_user.id, coins)
    await message.answer(
        f"✅ Оплата прошла успешно!\n"
        f"💰 На счёт зачислено <b>{coins} монет</b>!",
        parse_mode="HTML"
    )
