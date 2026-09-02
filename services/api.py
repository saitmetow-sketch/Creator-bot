import aiohttp

async def verify_bot_token(token: str):
    url = f"https://api.telegram.org/bot{token}/getMe"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("ok"):
                        result = data.get("result", {})
                        return {
                            "ok": True,
                            "id": result.get("id"),
                            "name": result.get("first_name"),
                            "username": result.get("username")
                        }
                return {"ok": False}
        except Exception:
            return {"ok": False}

