import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "58949832"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi. .env yoki hosting Environment Variables ni tekshiring.")
