import sys

from git import Repo
from os import system, execle, environ
from git.exc import InvalidGitRepositoryError

from pyrogram.types import Message
from pyrogram import Client, filters
from config import UPSTREAM_REPO, BOT_USERNAME

from driver.filters import command
from driver.decorators import bot_creator


def gen_chlog(repo, diff):
    upstream_repo_url = Repo().remotes[0].config_reader.get("url").replace(".git", "")
    ac_br = repo.active_branch.name
    ch_log = ""
    tldr_log = ""
    ch = f"<b>updates for <a href={upstream_repo_url}/tree/{ac_br}>[{ac_br}]</a>:</b>"
    ch_tl = f"updates for {ac_br}:"
    d_form = "%d/%m/%y || %H:%M"
    for c in repo.iter_commits(diff):
        ch_log += (
            f"\n\n💬 <b>{c.count()}</b> 🗓 <b>[{c.committed_datetime.strftime(d_form)}]</b>\n<b>"
            f"<a href={upstream_repo_url.rstrip('/')}/commit/{c}>[{c.summary}]</a></b> 👨‍💻 <code>{c.author}</code>"
        )
        tldr_log += f"\n\n💬 {c.count()} 🗓 [{c.committed_datetime.strftime(d_form)}]\n[{c.summary}] 👨‍💻 {c.author}"
    if ch_log:
        return str(ch + ch_log), str(ch_tl + tldr_log)
    return ch_log, tldr_log


def updater():
    try:
        repo = Repo()
    except InvalidGitRepositoryError:
        repo = Repo.init()
        origin = repo.create_remote("upstream", UPSTREAM_REPO)
        origin.fetch()
        repo.create_head("main", origin.refs.main)
        repo.heads.main.set_tracking_branch(origin.refs.main)
        repo.heads.main.checkout(True)
    ac_br = repo.active_branch.name
    if "upstream" in repo.remotes:
        ups_rem = repo.remote("upstream")
    else:
        ups_rem = repo.create_remote("upstream", UPSTREAM_REPO)
    ups_rem.fetch(ac_br)
    changelog, tl_chnglog = gen_chlog(repo, f"HEAD..upstream/{ac_br}")
    return bool(changelog)


@Client.on_message(command(["update", f"update@{BOT_USERNAME}"]) & ~filters.edited)
@bot_creator
async def update_bot(_, message: Message):
    chat_id = message.chat.id
    msg = await message.reply("❖ Checking updates...")
    update_avail = updater()
    if update_avail:
        await msg.edit("✅ Update finished !\n\n• Bot restarting, back active again in 1 minutes.")
        system("git pull -f && pip3 install --no-cache-dir -r requirements.txt")
        execle(sys.executable, sys.executable, "main.py", environ)
        return
    await msg.edit(f"❖ bot is **up-to-date** with [main]({UPSTREAM_REPO}/tree/main) ❖", disable_web_page_preview=True)


@Client.on_message(command(["restart","شروع مجدد", f"restart@{BOT_USERNAME}"]) & ~filters.edited)
@bot_creator
async def restart_bot(_, message: Message):
    msg = await message.reply("❖ شروع مجدد بات...")
    args = [sys.executable, "main.py"]
    await msg.edit("✅ ربات ری استارت شد !\n\n• تا یک دقیقه صبر کنید تا ربات ریبوت شود .")
    execle(sys.executable, *args, environ)
    return
