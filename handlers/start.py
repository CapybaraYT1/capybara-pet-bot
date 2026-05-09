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
            reply_markup=main_menu(),
            parse_mode="HTML"
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
        "Здесь ты будешь ухаживать за своей капибарой, "
        "вступать в кланы и соревноваться с другими!\n\n"
        "Как назовёшь свою капибару? ✏️",
        parse_mode="HTML"
    )

@router.message(RegisterState.waiting_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2 or len(name) > 20:
        await message.answer("⚠️ Имя должно быть от 2 до 20 символов. Попробуй ещё раз!")
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

    bonus_text = ""
    if referred_by:
        bonus_text = "\n🎁 <b>+50 монет</b> за приглашение друга!"

    await message.answer(
        f"🎉 Отлично! Твоя капибара <b>{name}</b> готова к приключениям!\n"
        f"💰 Стартовый баланс: <b>150 монет</b>{bonus_text}\n\n"
        f"Используй меню ниже для управления! 👇",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

@router.message(F.text == "◀️ Назад")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🏠 Главное меню", reply_markup=main_menu())
