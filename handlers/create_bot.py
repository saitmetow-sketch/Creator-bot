from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
from database import get_connection
from states.creator import BotCreationStates
from keyboards.inline import botfather_link_keyboard
from services.api import verify_bot_token

router = Router()

@router.message(F.text == "🎬 Yangi bot yaratish")
async def start_bot_creation(message: Message, state: FSMContext):
    text = (
        "1️⃣ Telegramni oching.\n"
        "2️⃣ BotFather'ga kiring va /newbot buyrug‘ini bosing.\n"
        "3️⃣ Bot nomini yuboring (Masalan: Kino Bot Sunday).\n"
        "4️⃣ Username yuboring (Oxiri 'bot' bilan tugasin, masalan: SundayKinoBot).\n\n"
        "🔑 BotFather bergan TOKENni nusxalang va shu yerga yuboring."
    )
    await message.answer(text, reply_markup=botfather_link_keyboard())
    await state.set_state(BotCreationStates.waiting_for_token)

@router.message(BotCreationStates.waiting_for_token)
async def process_bot_token(message: Message, state: FSMContext):
    token = message.text.strip()
    result = await verify_bot_token(token)
    
    if not result.get("ok"):
        await message.answer("❌ Token noto‘g‘ri yoki ishlamayapti. Iltimos, qaytadan tekshirib to‘g‘ri token yuboring:")
        return
        
    bot_id = result["id"]
    bot_name = result["name"]
    bot_username = result["username"]
    owner_id = message.from_user.id
    
    # 3 kunlik bepul muddat hisoblash
    now = datetime.now()
    expires_at = now + timedelta(days=3)
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO created_bots (bot_id, owner_id, bot_name, bot_username, bot_token, expires_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (bot_id, owner_id, bot_name, bot_username, token, expires_at.isoformat())
        )
        conn.commit()
    except Exception:
        await message.answer("⚠️ Bu bot allaqachon ro‘yxatdan o‘tkazilgan!")
        conn.close()
        await state.clear()
        return
    conn.close()
    
    await state.clear()
    await message.answer(
        f"✅ Bot muvaffaqiyatli ulandi!\n\n"
        f"🤖 Nomi: {bot_name}\n"
        f"👤 Username: @{bot_username}\n"
        f"🆔 Bot ID: {bot_id}\n\n"
        f"⏳ Bepul muddat: 3 kun."
    )

