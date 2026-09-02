from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def botfather_link_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 BotFather'ni ochish", url="https://t.me/BotFather")],
        [InlineKeyboardButton(text="🆔 @userinfobot orqali ID olish", url="https://t.me/userinfobot")]
    ])

def subscription_keyboard(channels: list, request_channels: list) -> InlineKeyboardMarkup:
    buttons = []
    for ch in channels:
        buttons.append([InlineKeyboardButton(text=f"📢 {ch['channel_username']}", url=ch['channel_link'])])
    for rch in request_channels:
        buttons.append([InlineKeyboardButton(text=f"📨 So‘rovli kanal", url=rch['channel_link'])])
    
    buttons.append([InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_subscription")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def expired_bot_keyboard(owner_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📩 Ownerga yozish", url=f"tg://user?id={owner_id}")]
    ])

