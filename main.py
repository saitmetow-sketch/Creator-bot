import asyncio
import logging
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_TOKEN, OWNER_ID
from database import init_db, DATABASE_NAME

import aiosqlite


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

dp = Dispatcher()


def main_menu(user_id: int):
    buttons = [
        [
            InlineKeyboardButton(
                text="🎬 Yangi bot yaratish",
                callback_data="create_bot"
            )
        ],
        [
            InlineKeyboardButton(
                text="🤖 Mening botlarim",
                callback_data="my_bots"
            )
        ],
        [
            InlineKeyboardButton(
                text="🎁 Tekin vaqt olish",
                callback_data="referral"
            )
        ],
        [
            InlineKeyboardButton(
                text="🆘 Yordam",
                callback_data="help"
            )
        ]
    ]

    if user_id == OWNER_ID:
        buttons.append([
            InlineKeyboardButton(
                text="👑 Admin panel",
                callback_data="admin_panel"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def save_user(message: Message, referred_by=None):
    user = message.from_user

    async with aiosqlite.connect(DATABASE_NAME) as db:
        cursor = await db.execute(
            "SELECT user_id FROM users WHERE user_id = ?",
            (user.id,)
        )
        exists = await cursor.fetchone()

        if not exists:
            await db.execute(
                """
                INSERT INTO users
                (user_id, full_name, username, registered_at, referred_by)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user.id,
                    user.full_name,
                    user.username,
                    datetime.now(timezone.utc).isoformat(),
                    referred_by
                )
            )

            if referred_by and referred_by != user.id:
                await db.execute(
                    """
                    UPDATE users
                    SET referral_count = referral_count + 1
                    WHERE user_id = ?
                    """,
                    (referred_by,)
                )

                await db.execute(
                    """
                    INSERT OR IGNORE INTO referrals
                    (referrer_id, referred_id, created_at)
                    VALUES (?, ?, ?)
                    """,
                    (
                        referred_by,
                        user.id,
                        datetime.now(timezone.utc).isoformat()
                    )
                )

        await db.commit()


@dp.message(CommandStart())
async def start_handler(message: Message):
    args = message.text.split(maxsplit=1)

    referred_by = None

    if len(args) == 2:
        try:
            referred_by = int(args[1])
        except ValueError:
            referred_by = None

    await save_user(message, referred_by)

    text = (
        f"👋 Salom, {message.from_user.full_name}!\n\n"
        "🎬 <b>Kino Bot Creator</b>ga xush kelibsiz!\n\n"
        "Bu bot orqali o‘zingizning Kino Botingizni yaratishingiz "
        "va boshqarishingiz mumkin.\n\n"
        "Quyidagi menyudan kerakli bo‘limni tanlang:"
    )

    await message.answer(
        text,
        reply_markup=main_menu(message.from_user.id),
        parse_mode="HTML"
    )


@dp.callback_query(F.data == "create_bot")
async def create_bot(callback):
    await callback.answer()

    text = (
        "🎬 <b>Yangi Kino Bot yaratish</b>\n\n"
        "1️⃣ Telegramni oching.\n\n"
        "2️⃣ BotFather'ga kiring.\n\n"
        "👇 Quyidagi tugmani bosing:"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🤖 BotFather'ni ochish",
                    url="https://t.me/BotFather"
                )
            ],
            [
                InlineKeyboardButton(
                    text="➡️ Keyingi qadam",
                    callback_data="botfather_step"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@dp.callback_query(F.data == "botfather_step")
async def botfather_step(callback):
    await callback.answer()

    text = (
        "📱 <b>BotFather'da quyidagilarni bajaring:</b>\n\n"
        "1. /newbot buyrug‘ini bosing.\n\n"
        "2. Bot nomini yozing.\n"
        "Masalan: <b>Kino Bot Sunday</b>\n\n"
        "3. Username yozing.\n"
        "Username oxiri <b>bot</b> bilan tugashi kerak.\n"
        "Masalan: <b>SundayKinoBot</b>\n\n"
        "4. BotFather sizga <b>Token</b> beradi.\n\n"
        "5. Tokenni nusxalab, shu Creator Botga yuboring.\n\n"
        "⚠️ Tokenni boshqa odamlarga yubormang."
    )

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🤖 BotFather",
                        url="https://t.me/BotFather"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="⬅️ Orqaga",
                        callback_data="back_menu"
                    )
                ]
            ]
        ),
        parse_mode="HTML"
    )


@dp.callback_query(F.data == "my_bots")
async def my_bots(callback):
    await callback.answer()

    async with aiosqlite.connect(DATABASE_NAME) as db:
        cursor = await db.execute(
            """
            SELECT bot_username, bot_name, bot_id, expires_at, active
            FROM created_bots
            WHERE owner_id = ?
            ORDER BY id DESC
            """,
            (callback.from_user.id,)
        )

        bots = await cursor.fetchall()

    if not bots:
        text = (
            "🤖 <b>Mening botlarim</b>\n\n"
            "Siz hali Kino Bot yaratmagansiz."
        )
    else:
        lines = ["🤖 <b>Mening botlarim:</b>\n"]

        for bot_username, bot_name, bot_id, expires_at, active in bots:
            try:
                expiry = datetime.fromisoformat(expires_at)
                now = datetime.now(timezone.utc)

                seconds = int((expiry - now).total_seconds())

                if seconds > 0:
                    days = seconds // 86400
                    hours = (seconds % 86400) // 3600
                    minutes = (seconds % 3600) // 60

                    remaining = (
                        f"{days} kun {hours} soat "
                        f"{minutes} daqiqa"
                    )

                    status = "🟢 Aktiv"
                else:
                    remaining = "0 kun 0 soat 0 daqiqa"
                    status = "🔴 Muddati tugagan"

            except Exception:
                remaining = "0 kun 0 soat 0 daqiqa"
                status = "🔴 Noma'lum"

            username = (
                f"@{bot_username}"
                if bot_username
                else "Username yo‘q"
            )

            lines.append(
                f"🤖 <b>{username}</b>\n"
                f"🆔 ID: <code>{bot_id}</code>\n"
                f"⏳ Qolgan: {remaining}\n"
                f"{status}\n"
            )

        text = "\n".join(lines)

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⬅️ Orqaga",
                        callback_data="back_menu"
                    )
                ]
            ]
        ),
        parse_mode="HTML"
    )


@dp.callback_query(F.data == "referral")
async def referral(callback):
    await callback.answer()

    me = await callback.bot.get_me()

    link = (
        f"https://t.me/{me.username}"
        f"?start={callback.from_user.id}"
    )

    async with aiosqlite.connect(DATABASE_NAME) as db:
        cursor = await db.execute(
            """
            SELECT referral_count
            FROM users
            WHERE user_id = ?
            """,
            (callback.from_user.id,)
        )

        result = await cursor.fetchone()

    count = result[0] if result else 0

    text = (
        "🎁 <b>Tekin vaqt olish</b>\n\n"
        f"👥 Siz taklif qilgan yangi foydalanuvchilar: "
        f"<b>{count}</b>\n\n"
        "🎯 Har 2 ta haqiqiy yangi foydalanuvchi "
        "uchun +1 kun bepul vaqt beriladi.\n\n"
        "🔗 <b>Sizning referral linkingiz:</b>\n"
        f"<code>{link}</code>\n\n"
        "⚠️ O‘zingizni referral qilish hisoblanmaydi."
    )

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⬅️ Orqaga",
                        callback_data="back_menu"
                    )
                ]
            ]
        ),
        parse_mode="HTML"
    )


@dp.callback_query(F.data == "help")
async def help_handler(callback):
    await callback.answer()

    text = (
        "🆘 <b>Yordam</b>\n\n"
        "🎬 Yangi bot yaratish — yangi Kino Bot yaratish.\n\n"
        "🤖 Mening botlarim — yaratgan botlaringizni ko‘rish.\n\n"
        "🎁 Tekin vaqt olish — referral orqali bepul vaqt olish.\n\n"
        "Bot yaratishda muammo bo‘lsa Owner bilan bog‘laning."
    )

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⬅️ Orqaga",
                        callback_data="back_menu"
                    )
                ]
            ]
        ),
        parse_mode="HTML"
    )


@dp.callback_query(F.data == "admin_panel")
async def admin_panel(callback):
    if callback.from_user.id != OWNER_ID:
        await callback.answer(
            "⛔ Sizda ruxsat yo‘q.",
            show_alert=True
        )
        return

    await callback.answer()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👥 Adminlar",
                    callback_data="admins"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📢 Kanallar",
                    callback_data="channels"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Statistika",
                    callback_data="statistics"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🤖 Yaratilgan botlar",
                    callback_data="all_bots"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📣 Reklama tarqatish",
                    callback_data="broadcast"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Orqaga",
                    callback_data="back_menu"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        "👑 <b>Admin panel</b>\n\nKerakli bo‘limni tanlang:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@dp.callback_query(F.data == "back_menu")
async def back_menu(callback):
    await callback.answer()

    await callback.message.edit_text(
        "🏠 <b>Asosiy menyu</b>\n\nBo‘limni tanlang:",
        reply_markup=main_menu(callback.from_user.id),
        parse_mode="HTML"
    )


async def main():
    await init_db()

    bot = Bot(token=BOT_TOKEN)

    me = await bot.get_me()

    logging.info(
        "Bot ishga tushdi: @%s (%s)",
        me.username,
        me.id
    )

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
