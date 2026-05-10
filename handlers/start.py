from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db
from keyboards import main_menu

router = Router()

class RegisterState(StatesGroup):
    waiting_name = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = db.get_user(message.from_user.id)
    if user:
        await message.answer(
            f"🐾 С возвращением! Твоя капибара <b>{user['capybara_name']}</b> скучала по тебе!",
            reply_markup=main_menu(), parse_mode="HTML"
        )
        return

    args = message.text.split()
    referred_by = None
    if len(args) > 1:
        try:
            ref_id = int(args[1].replace("ref", ""))
            if ref_id != message.from_user.id:
                referred_by = ref_id
        except:
            pass

    await state.update_data(referred_by=referred_by)
    await state.set_state(RegisterState.waiting_name)
    await message.answer(
        "🐾 Добро пожаловать в <b>Capybara Pet</b>!\n\n"
        "Здесь ты будешь ухаживать за своей капибарой, вступать в кланы и сражаться!\n\n"
        "Придумай имя для своей капибары ✏️\n"
        "<i>(от 3 до 12 символов)</i>",
        parse_mode="HTML"
    )

@router.message(RegisterState.waiting_name)
async def process_name(message: Message, state: FSMContext):
    if message.text == "◀️ Назад":
        await state.clear()
        return

    name = message.text.strip()
    if len(name) < 3 or len(name) > 12:
        await message.answer("⚠️ Имя должно быть от 3 до 12 символов!")
        return
    if db.get_user_by_capybara_name(name):
        await message.answer("❌ Это имя уже занято! Придумай другое.")
        return

    data = await state.get_data()
    referred_by = data.get("referred_by")
    db.create_user(
        user_id=message.from_user.id,
        username=message.from_user.username or message.from_user.first_name,
        capybara_name=name,
        referred_by=referred_by
    )
    await state.clear()

    bonus_text = "\n🎁 <b>+80 монет</b> за приглашение друга!" if referred_by else ""
    await message.answer(
        f"🎉 Твоя капибара <b>{name}</b> готова к приключениям!\n"
        f"💰 Стартовый баланс: <b>150 монет</b>{bonus_text}\n\n"
        f"Используй меню ниже! 👇",
        reply_markup=main_menu(), parse_mode="HTML"
    )

@router.message(F.text == "◀️ Назад")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🏠 Главное меню", reply_markup=main_menu())
