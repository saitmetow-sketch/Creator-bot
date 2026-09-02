from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="🎬 Yangi bot yaratish"), KeyboardButton(text="🤖 Mening botlarim")],
        [KeyboardButton(text="🎁 Tekin vaqt olish"), KeyboardButton(text="🆘 Yordam")]
    ]
    if is_admin:
        keyboard.append([KeyboardButton(text="👑 Admin panel")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def admin_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="👥 Adminlar"), KeyboardButton(text="📢 Kanallar")],
        [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="🤖 Yaratilgan botlar")],
        [KeyboardButton(text="📣 Reklama tarqatish"), KeyboardButton(text="⚙️ Sozlamalar")],
        [KeyboardButton(text="🔙 Asosiy menyu")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

