from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from database import get_connection
from keyboards.reply import main_menu_keyboard
from keyboards.inline import subscription_keyboard
from config import OWNER_ID

router = Router()

async def check_user_subscriptions(user_id: int, bot) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mandatory_channels")
    mand_channels = cursor.fetchall()
    cursor.execute("SELECT * FROM request_channels")
    req_channels = cursor.fetchall()
    conn.close()

    # Majburiy obunalar tekshiruvi
    for ch in mand_channels:
        try:
            member = await bot.get_chat_member(chat_id=ch["channel_id"], user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception:
            return False
            
    # So'rovli kanallar tekshiruvi (join request yoki chat member)
    for rch in req_channels:
        try:
            member = await bot.get_chat_member(chat_id=rch["channel_id"], user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception:
            return False
            
    return True

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    
    args = message.text.split()
    referrer_id = None
    if len(args) > 1 and args[1].isdigit():
        ref_id = int(args[1])
        if ref_id != user_id:
            referrer_id = ref_id

    conn = get_connection()
    cursor = conn.cursor()
    
    # Foydalanuvchini bazaga qo'shish
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    existing = cursor.fetchone()
    
    if not existing:
        cursor.execute(
            "INSERT INTO users (user_id, full_name, username, referrer_id) VALUES (?, ?, ?, ?)",
            (user_id, full_name, username, referrer_id)
        )
        if referrer_id:
            try:
                cursor.execute("INSERT INTO referrals (referrer_id, referred_id) VALUES (?, ?)", (referrer_id, user_id))
            except Exception:
                pass
        conn.commit()
    conn.close()

    # Admin ekanligini tekshirish
    is_admin = (user_id == OWNER_ID)
    if not is_admin:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,))
        if cursor.fetchone():
            is_admin = True
        conn.close()

    # Obunalarni tekshirish
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mandatory_channels")
    mand_channels = cursor.fetchall()
    cursor.execute("SELECT * FROM request_channels")
    req_channels = cursor.fetchall()
    conn.close()

    if mand_channels or req_channels:
        is_subscribed = await check_user_subscriptions(user_id, message.bot)
        if not is_subscribed:
            await message.answer(
                "⚠️ Botdan foydalanish uchun quyidagi kanallarga obuna bo‘lishingiz kerak:",
                reply_markup=subscription_keyboard(mand_channels, req_channels)
            )
            return

    await message.answer(
        f"Assalomu alaykum, {full_name}!\nKino Bot Creator ga xush kelibsiz. O'z kino botingizni yarating va boshqaring.",
        reply_markup=main_menu_keyboard(is_admin)
    )

@router.callback_query(F.data == "check_subscription")
async def verify_sub_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_subscribed = await check_user_subscriptions(user_id, callback.bot)
    
    if not is_subscribed:
        await callback.answer("❌ Hali barcha kanallarga obuna bo‘lmadingiz!", show_alert=True)
        return
        
    await callback.message.delete()
    is_admin = (user_id == OWNER_ID)
    if not is_admin:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,))
        if cursor.fetchone():
            is_admin = True
        conn.close()
        
    await callback.message.answer(
        "✅ Obuna tasdiqlandi! Asosiy menyudasiz.",
        reply_markup=main_menu_keyboard(is_admin)
    )

