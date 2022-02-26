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


from config import BOT_USERNAME
from driver.decorators import check_blacklist
from driver.filters import command
from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtube_search import YoutubeSearch


@Client.on_message(command(["search", f"search@{BOT_USERNAME}"]))
@check_blacklist()
async def ytsearch(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("/search **needs an argument !**")
    query = message.text.split(None, 1)[1]
    m = await message.reply_text("🔎 **Searching...**")
    results = YoutubeSearch(query, max_results=5).to_dict()
    text = ""
    for i in range(5):
        try:
            text += f"🏷 **اسم:** __{results[i]['title']}__\n"
            text += f"⏱ **مدت:** `{results[i]['duration']}`\n"
            text += f"👀 **بازدید:** `{results[i]['views']}`\n"
            text += f"📣 **کانال:** {results[i]['channel']}\n"
            text += f"🔗: https://www.youtube.com{results[i]['url_suffix']}\n\n"
        except IndexError:
            break
    await m.edit_text(
        text,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🗑 خروج", callback_data="close_panel")]]
        ),
    )
