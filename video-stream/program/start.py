"""
Video + Music Stream Telegram Bot
Copyright (c) 2022-present levina=lab <https://github.com/levina-lab>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but without any warranty; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/licenses.html>
"""


import asyncio

from datetime import datetime
from sys import version_info
from time import time

from config import (
    ALIVE_IMG,
    ALIVE_NAME,
    BOT_USERNAME,
    GROUP_SUPPORT,
    OWNER_USERNAME,
    UPDATES_CHANNEL,
)
from driver.decorators import check_blacklist
from program import __version__
from driver.core import bot, me_bot, me_user
from driver.filters import command
from driver.database.dbchat import add_served_chat, is_served_chat
from driver.database.dbpunish import is_gbanned_user
from driver.database.dbusers import add_served_user
from driver.database.dblockchat import blacklisted_chats

from pyrogram import Client, filters, __version__ as pyrover
from pyrogram.errors import FloodWait
from pytgcalls import (__version__ as pytover)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ChatJoinRequest

__major__ = 0
__minor__ = 2
__micro__ = 1

__python_version__ = f"{version_info[0]}.{version_info[1]}.{version_info[2]}"


START_TIME = datetime.utcnow()
START_TIME_ISO = START_TIME.replace(microsecond=0).isoformat()
TIME_DURATION_UNITS = (
    ("week", 60 * 60 * 24 * 7),
    ("day", 60 * 60 * 24),
    ("hour", 60 * 60),
    ("min", 60),
    ("sec", 1),
)


async def _human_time_duration(seconds):
    if seconds == 0:
        return "inf"
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append("{} {}{}".format(amount, unit, "" if amount == 1 else "s"))
    return ", ".join(parts)


@Client.on_message(
    command(["start", f"start@{BOT_USERNAME}"]) & filters.private & ~filters.edited
)
@check_blacklist()
async def start_(c: Client, message: Message):
    await message.reply_text(
        f"""✨ ** خوش آمدیدی {message.from_user.mention()} !**\n
💭  **Iاین ربات این امکان را به شما می دهد تا آهنگ و یا ویدئو را در ویس چت گروه خود پخش کنید !! \n\n**

**دستورات را می توانید از ادمین درخواست کنید**
""",
        reply_markup=InlineKeyboardMarkup(
            [
                
                [

                    InlineKeyboardButton("❤️ ادمین", url=f"https://t.me/{OWNER_USERNAME}")
                ],
                [
    
                    InlineKeyboardButton(
                        "📣 کانال", url=f"https://t.me/{UPDATES_CHANNEL}"
                    ),
                ]
            ]
        ),
        disable_web_page_preview=True,
    )


@Client.on_message(
    command(["alive", f"alive@{BOT_USERNAME}"]) & filters.group & ~filters.edited
)
@check_blacklist()
async def alive(c: Client, message: Message):
    chat_id = message.chat.id
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✨ Group", url=f"https://t.me/{GROUP_SUPPORT}"),
                InlineKeyboardButton(
                    "📣 Channel", url=f"https://t.me/{UPDATES_CHANNEL}"
                ),
            ]
        ]
    )

    alive = f"**سلام {message.from_user.mention()}, من : {me_bot.first_name}**\n\n🧑🏼‍💻  ارباب من: [{ALIVE_NAME}](https://t.me/{OWNER_USERNAME})\n👾 Bot Version: `v{__version__}`\n🔥 Pyrogram Version: `{pyrover}`\n🐍 Python Version: `{__python_version__}`\n✨ PyTgCalls Version: `{pytover.__version__}`\n🆙 شروع از: `{uptime}`\n\n❤ ❤ ❤ ❤ ❤"

    await c.send_photo(
        chat_id,
        photo=f"{ALIVE_IMG}",
        caption=alive,
        reply_markup=keyboard,
    )


@Client.on_message(command(["ping","پینگ", f"ping@{BOT_USERNAME}"]) & ~filters.edited)
@check_blacklist()
async def ping_pong(c: Client, message: Message):
    start = time()
    m_reply = await message.reply_text("pinging...")
    delta_ping = time() - start
    await m_reply.edit_text("🏓 `PONG!!`\n" f"⚡️ `{delta_ping * 1000:.3f} ms`")


@Client.on_message(command(["uptime", f"uptime@{BOT_USERNAME}"]) & ~filters.edited)
@check_blacklist()
async def get_uptime(c: Client, message: Message):
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    await message.reply_text(
        "🤖 bot status:\n"
        f"• **uptime:** `{uptime}`\n"
        f"• **start time:** `{START_TIME_ISO}`"
    )


@Client.on_chat_join_request()
async def approve_join_chat(c: Client, m: ChatJoinRequest):
    if not m.from_user:
        return
    try:
        await c.approve_chat_join_request(m.chat.id, m.from_user.id)
    except FloodWait as e:
        await asyncio.sleep(e.x + 2)
        await c.approve_chat_join_request(m.chat.id, m.from_user.id)


@Client.on_message(filters.new_chat_members)
async def new_chat(c: Client, m: Message):
    chat_id = m.chat.id
    if await is_served_chat(chat_id):
        pass
    else:
        await add_served_chat(chat_id)
    for member in m.new_chat_members:
        if chat_id in await blacklisted_chats():
            await m.reply(
                "❗️ این چت بلاک شده است و دسترسی استفاده از ربات را نخواهد داشت."
            )
            return await bot.leave_chat(chat_id)
        if member.id == me_bot.id:
            return await m.reply(
                "❤️ مرسی من را دعوت کردید !\n\n"
                "من رو ادمین کنید و دسترسی بدهید  بعد دستور زیر را بنید تا دستیارم عضو بشه .\n\n"
                "`/userbotjoin` \n\n"
                "  بعد که جوین شد دستور زیر را بفرستید \n\n"
                "`/reload`",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("📣 کانال", url=f"https://t.me/{UPDATES_CHANNEL}"),
                            InlineKeyboardButton("💭 ادمین", url=f"https://t.me/{GROUP_SUPPORT}")
                        ],
                        [
                            InlineKeyboardButton("👤 دستیار", url=f"https://t.me/{me_user.username}")
                        ]
                    ]
                )
            )


chat_watcher_group = 10

@Client.on_message(group=chat_watcher_group)
async def chat_watcher_func(_, message: Message):
    if message.from_user:
        user_id = message.from_user.id
        await add_served_user(user_id)
        return
    try:
        userid = message.from_user.id
    except Exception:
        return
    suspect = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    if await is_gbanned_user(userid):
        try:
            await message.chat.ban_member(userid)
        except Exception:
            return
        await message.reply_text(
            f"👮🏼 (> {suspect} <)\n\n شخص بن گروهی یافت شد  این شخص توسط ادمین بلاک شده و اجازه دسترسی به امکانات من را ندارد !\n\n🚫 امکان استفاده  از ربات را نداربید دلیل اسپم یا ..."
        )
