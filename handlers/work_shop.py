from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
import database as db
from keyboards import main_menu, leaderboard_menu

router = Router()

def work_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💼 Отправить на работу", callback_data="work_start")],
        [InlineKeyboardButton(text="💰 Забрать заработок", callback_data="work_collect")],
        [InlineKeyboardButton(text="🏠 Забрать с работы", callback_data="work_stop")],
    ])

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

@router.message(F.text == "💼 Работа")
async def work_menu(message: Message):
    user = db.get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Сначала запусти /start")
        return
    status = "🟢 На работе" if user['is_working'] else "🔴 Дома"
    await message.answer(
        f"💼 <b>Работа</b>\n"
        f"{'─' * 20}\n"
        f"Статус: {status}\n\n"
        f"⏱ Каждые <b>30 минут</b> капибара приносит от <b>30 до 90 монет</b>",
        reply_markup=work_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "work_start")
async def work_start(callback: CallbackQuery):
    user = db.get_user(callback.from_user.id)
    if user['is_working']:
        await callback.answer("⚠️ Капибара уже на работе!", show_alert=True)
        return
    db.start_work(callback.from_user.id)
    await callback.message.answer("💼 Капибара отправилась на работу!\n⏱ Возвращайся через <b>30 минут</b>.", parse_mode="HTML")
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
    await callback.message.answer(f"💰 Капибара принесла <b>{earned} монет</b>! Продолжает работать 💼", parse_mode="HTML")
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

# ─── ЛИДЕРЫ ─────────────────────────────────────────────────
@router.message(F.text == "🏆 Лидеры")
async def leaderboard(message: Message):
    await message.answer("🏆 <b>Таблица лидеров</b>\n\nВыбери категорию:", reply_markup=leaderboard_menu(), parse_mode="HTML")

@router.callback_query(F.data == "top_coins")
async def top_coins(callback: CallbackQuery):
    top = db.get_top_users_coins(10)
    medals = ["🥇", "🥈", "🥉"]
    text = "💰 <b>Топ по монетам</b>\n" + "─" * 20 + "\n\n"
    for i, u in enumerate(top):
        medal = medals[i] if i < 3 else f"{i+1}."
        text += f"{medal} <b>{u['capybara_name']}</b> — {u['coins']} монет\n"
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "top_referrals")
async def top_referrals(callback: CallbackQuery):
    top = db.get_top_users_referrals(10)
    medals = ["🥇", "🥈", "🥉"]
    text = "🎟 <b>Топ по рефералам</b>\n" + "─" * 20 + "\n\n"
    for i, u in enumerate(top):
        medal = medals[i] if i < 3 else f"{i+1}."
        text += f"{medal} <b>{u['capybara_name']}</b> — {u['referrals_count']} реф.\n"
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "top_battles")
async def top_battles(callback: CallbackQuery):
    top = db.get_top_users_battles(10)
    medals = ["🥇", "🥈", "🥉"]
    text = "⚔️ <b>Топ по победам</b>\n" + "─" * 20 + "\n\n"
    for i, u in enumerate(top):
        medal = medals[i] if i < 3 else f"{i+1}."
        text += f"{medal} <b>{u['capybara_name']}</b> — {u['battles_won']} побед\n"
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

# ─── МАГАЗИН ─────────────────────────────────────────────────
@router.message(F.text == "💎 Купить монеты")
async def shop_menu(message: Message):
    await message.answer(
        "💎 <b>Магазин монет</b>\n"
        "──────────────────────\n\n"
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
    coins = int(message.successful_payment.invoice_payload.split("_")[1])
    db.add_coins(message.from_user.id, coins)
    await message.answer(f"✅ Оплата прошла!\n💰 Зачислено <b>{coins} монет</b>!", parse_mode="HTML")
