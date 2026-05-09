from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="🎟 Рефералы")],
        [KeyboardButton(text="👥 Кланы"), KeyboardButton(text="💼 Работа")],
        [KeyboardButton(text="🏆 Лидеры"), KeyboardButton(text="💎 Купить монеты")]
    ], resize_keyboard=True)

def back_button():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="◀️ Назад")]
    ], resize_keyboard=True)

def profile_inline(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Переименовать капибару", callback_data="rename_capy")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")]
    ])

def clans_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🏠 Мой клан")],
        [KeyboardButton(text="➕ Создать клан")],
        [KeyboardButton(text="📨 Приглашения"), KeyboardButton(text="👑 Топ кланов")],
        [KeyboardButton(text="◀️ Назад")]
    ], resize_keyboard=True)

def my_clan_member_inline(clan_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Пополнить казну", callback_data=f"donate_{clan_id}")],
        [InlineKeyboardButton(text="🚪 Покинуть клан", callback_data=f"leave_clan_{clan_id}")]
    ])

def my_clan_owner_inline(clan_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Пополнить казну", callback_data=f"donate_{clan_id}")],
        [InlineKeyboardButton(text="📨 Пригласить игрока", callback_data=f"invite_{clan_id}")],
        [InlineKeyboardButton(text="🗑 Удалить клан", callback_data=f"delete_clan_{clan_id}")]
    ])

def invite_inline(invite_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_invite_{invite_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline_invite_{invite_id}")
        ]
    ])

def confirm_inline(action: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{action}"),
            InlineKeyboardButton(text="❌ Нет", callback_data="cancel_action")
        ]
    ])
