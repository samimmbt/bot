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

from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import FloodWait

from driver.core import me_bot
from driver.filters import command, other_filters
from driver.decorators import bot_creator
from driver.database.dbchat import get_served_chats
from driver.database.dbpunish import add_gban_user, is_gbanned_user, remove_gban_user

from config import OWNER_ID, SUDO_USERS, BOT_USERNAME as bn


@Client.on_message(command(["gban", "بن کل", f"gban@{bn}"]) & other_filters)
@bot_creator
async def global_banned(c: Client, message: Message):
    BOT_NAME = me_bot.first_name
    if not message.reply_to_message:
        if len(message.command) < 2:
            await message.reply_text("**usage:**\n\n/gban [username | user_id]")
            return
        user = message.text.split(None, 2)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await c.get_users(user)
        from_user = message.from_user
        BOT_ID = me_bot.id
        if user.id == from_user.id:
            await message.reply_text("خودتو نمیتونی بن کنی !")
        elif user.id == BOT_ID:
            await message.reply_text("خودمو نمیتونم بن کنم !")
        elif user.id in SUDO_USERS:
            await message.reply_text("نمیتونی ادمین رو بن کنی  !")
        elif user.id in OWNER_ID:
            await message.reply_text("نمیتونی سازنده رو بن کنی  !")
        else:
            await add_gban_user(user.id)
            served_chats = []
            chats = await get_served_chats()
            for chat in chats:
                served_chats.append(int(chat["chat_id"]))
            m = await message.reply_text(
                f"🚷 ** بن گلوبال {user.mention}**\n⏱ زمان پیشبینی شده: `{len(served_chats)}`"
            )
            number_of_chats = 0
            for num in served_chats:
                try:
                    await c.ban_chat_member(num, user.id)
                    number_of_chats += 1
                    await asyncio.sleep(1)
                except FloodWait as e:
                    await asyncio.sleep(int(e.x))
                except Exception:
                    pass
            ban_text = f"""
🚷 **فرد جدید در گلوبال بن [{BOT_NAME}](https://t.me/{bn})

**Origin:** {message.chat.title} [`{message.chat.id}`]
**Sudo User:** {from_user.mention}
**Banned User:** {user.mention}
**Banned User ID:** `{user.id}`
**Chats:** `{number_of_chats}`"""
            try:
                await m.delete()
            except Exception:
                pass
            await message.reply_text(
                f"{ban_text}",
                disable_web_page_preview=True,
            )
        return
    from_user_id = message.from_user.id
    from_user_mention = message.from_user.mention
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention
    BOT_ID = me_bot.id
    if user_id == from_user_id:
        await message.reply_text("خودتو نمیتونی بن کنی!")
    elif user_id == BOT_ID:
        await message.reply_text("نمیتونم خودمو بن  ننم  !")
    elif user_id in SUDO_USERS:
        await message.reply_text("نمیتونی ادمین رو بن کنی  !")
    elif user_id in OWNER_ID:
        await message.reply_text("سازنده رو نمیتونی بن کنی  !")
    else:
        is_gbanned = await is_gbanned_user(user_id)
        if is_gbanned:
            await message.reply_text(" ایشون بن شده !")
        else:
            await add_gban_user(user_id)
            served_chats = []
            chats = await get_served_chats()
            for chat in chats:
                served_chats.append(int(chat["chat_id"]))
            m = await message.reply_text(
                f"🚷 **Globally banning {mention}**\n⏱ Expected time: `{len(served_chats)}`"
            )
            number_of_chats = 0
            for num in served_chats:
                try:
                    await c.ban_chat_member(num, user_id)
                    number_of_chats += 1
                    await asyncio.sleep(1)
                except FloodWait as e:
                    await asyncio.sleep(int(e.x))
                except Exception:
                    pass
            ban_text = f"""
🚷 **New Global ban on [{BOT_NAME}](https://t.me/{bn})

**Origin:** {message.chat.title} [`{message.chat.id}`]
**Sudo User:** {from_user_mention}
**Banned User:** {mention}
**Banned User ID:** `{user_id}`
**Chats:** `{number_of_chats}`"""
            try:
                await m.delete()
            except Exception:
                pass
            await message.reply_text(
                f"{ban_text}",
                disable_web_page_preview=True,
            )
            return


@Client.on_message(command(["ungban","آنبن کل", f"ungban@{bn}"]) & other_filters)
@bot_creator
async def ungban_global(c: Client, message: Message):
    chat_id = message.chat.id
    if not message.reply_to_message:
        if len(message.command) != 2:
            await message.reply_text(
                "**usage:**\n\n/ungban [username | user_id]"
            )
            return
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await c.get_users(user)
        from_user = message.from_user
        BOT_ID = me_bot.id
        if user.id == from_user.id:
            await message.reply_text("خودتو نمیتونی از بن در بیاری چون هرگز بن نمیشی !")
        elif user.id == BOT_ID:
            await message.reply_text("من نمیتونم از بن در بیام چون بن نمی شم !")
        elif user.id in SUDO_USERS:
            await message.reply_text("ادمینا نمیتوننن کخ با این حرکات بن بشن gbanned/ungbanned !")
        elif user.id in OWNER_ID:
            await message.reply_text(" سازنده رو چشمم جا داره اصلا فکر آن بن و بن کردنش نباش دیگه!")
        else:
            is_gbanned = await is_gbanned_user(user.id)
            if not is_gbanned:
                await message.reply_text("این فرد بن نشده  !")
            else:
                msg = await message.reply_text("» از بن در آوردن ...")
                await remove_gban_user(user.id)
                served_chats = []
                chats = await get_served_chats()
                for chat in chats:
                    served_chats.append(int(chat["chat_id"]))
                number_of_chats = 0
                for num in served_chats:
                    try:
                        await c.unban_chat_member(num, user.id)
                        number_of_chats += 1
                        await asyncio.sleep(1)
                    except FloodWait as e:
                        await asyncio.sleep(int(e.x))
                    except BaseException:
                        pass
                await msg.edit_text("✅ This user has ungbanned")
        return
    from_user_id = message.from_user.id
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention
    BOT_ID = me_bot.id
    if user_id == from_user_id:
        await message.reply_text("You can't ungban yourself because you can't be gbanned !")
    elif user_id == BOT_ID:
        await message.reply_text("I can't ungban myself because i can't be gbanned !")
    elif user_id in SUDO_USERS:
        await message.reply_text("Sudo users can't be gbanned/ungbanned !")
    elif user_id in OWNER_ID:
        await message.reply_text("Bot creator can't be gbanned/ungbanned !")
    else:
        is_gbanned = await is_gbanned_user(user_id)
        if not is_gbanned:
            await message.reply_text("This user is not gbanned !")
        else:
            msg = await message.reply_text("» ungbanning user...")
            await remove_gban_user(user_id)
            served_chats = []
            chats = await get_served_chats()
            for chat in chats:
                served_chats.append(int(chat["chat_id"]))
            number_of_chats = 0
            for num in served_chats:
                try:
                    await c.unban_chat_member(num, user_id)
                    number_of_chats += 1
                    await asyncio.sleep(1)
                except FloodWait as e:
                    await asyncio.sleep(int(e.x))
                except BaseException:
                    pass
                await msg.edit_text("✅ This user has ungbanned")
