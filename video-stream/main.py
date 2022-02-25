import asyncio
from pytgcalls import idle
from driver.core import calls, bot, user


async def start_bot():
    await bot.start()
    print("[INFO]: BOT & UBOT CLIENT STARTED !!")
    await calls.start()
    print("[INFO]: PY-TGCALLS CLIENT STARTED !!")
    await user.join_chat("VeezSupportGroup")
    await user.join_chat("levinachannel")
    await idle()
    print("[INFO]: STOPPING BOT & USERBOT")
    await bot.stop()

loop = asyncio.get_event_loop()
loop.run_until_complete(start_bot())
