import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import init_db
from handlers import start, create_bot, referral

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # Bazani ishga tushirish
    init_db()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Routerlarni ulash
    dp.include_router(start.router)
    dp.include_router(create_bot.router)
    dp.include_router(referral.router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Bot muvaffaqiyatli ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

