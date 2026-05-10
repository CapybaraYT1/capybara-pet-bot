from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="🎟 Рефералы")],
        [KeyboardButton(text="👥 Кланы"), KeyboardButton(text="💼 Работа")],
        [KeyboardButton(text="🎁 Кейсы"), KeyboardButton(text="🎒 Инвентарь")],
        [KeyboardButton(text="⚔️ Бой"), KeyboardButton(text="🎀 Ежедневка")],
        [KeyboardButton(text="🏆 Лидеры"), KeyboardButton(text="💎 Купить монеты")],
    ], resize_keyboard=True)

def back_button():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="◀️ Назад")]], resize_keyboard=True)

def profile_inline():
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

def my_clan_member_inline(clan_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Пополнить казну", callback_data=f"donate_{clan_id}")],
        [InlineKeyboardButton(text="🚪 Покинуть клан", callback_data=f"leave_clan_{clan_id}")]
    ])

def my_clan_owner_inline(clan_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Пополнить казну", callback_data=f"donate_{clan_id}")],
        [InlineKeyboardButton(text="📨 Пригласить игрока", callback_data=f"invite_{clan_id}")],
        [InlineKeyboardButton(text="🗑 Удалить клан", callback_data=f"delete_clan_{clan_id}")]
    ])

def invite_inline(invite_id):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_invite_{invite_id}"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline_invite_{invite_id}")
    ]])

def confirm_inline(action):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{action}"),
        InlineKeyboardButton(text="❌ Нет", callback_data="cancel_action")
    ]])

def cases_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚔️ Кейс оружия — 1000 монет", callback_data="case_weapon")],
        [InlineKeyboardButton(text="🛡 Кейс брони — 1000 монет", callback_data="case_armor")],
    ])

def confirm_case(case_type):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Открыть", callback_data=f"open_{case_type}"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_case")
    ]])

def battle_inline(challenger_id):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⚔️ Принять бой", callback_data=f"battle_accept_{challenger_id}"),
        InlineKeyboardButton(text="🏳 Отказаться", callback_data=f"battle_decline_{challenger_id}")
    ]])

def leaderboard_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 По монетам", callback_data="top_coins")],
        [InlineKeyboardButton(text="🎟 По рефералам", callback_data="top_referrals")],
        [InlineKeyboardButton(text="⚔️ По победам", callback_data="top_battles")],
    ])

def inventory_equip(item_id, item_type):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="👕 Надеть", callback_data=f"equip_{item_id}_{item_type}")
    ]])
