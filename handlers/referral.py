from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import get_connection
from datetime import datetime, timedelta

router = Router()

@router.message(F.text == "🎁 Tekin vaqt olish")
async def referral_menu(message: Message):
    user_id = message.from_user.id
    bot_info = await message.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM referrals WHERE referrer_id = ?", (user_id,))
    ref_count = cursor.fetchone()["count"]
    conn.close()
    
    text = (
        f"🎁 **Referral tizimi**\n\n"
        f"Har 2 ta taklif qilingan yangi foydalanuvchi uchun istalgan botingizga **+1 kun** vaqt qo‘shib beriladi!\n\n"
        f"Siz taklif qilganlar: {ref_count} ta\n\n"
        f"🔗 Sizning referral linkingiz:\n{ref_link}"
    )
    await message.answer(text)

