"""The bot itself: a pure message handler plus a thin long-polling loop.

`reply_for` is where every command is decided — text in, HTML out, no network —
so the whole conversation surface is unit-testable. `run` and `send_daily` add
the only I/O: the Telegram client and the engine.
"""

from __future__ import annotations

import logging
import os
import time

from .. import store
from ..engine import daily_report
from . import format as fmt
from .api import TelegramClient, TelegramError
from .parse import DATE_RE, ParseError, parse_birth

log = logging.getLogger("unicosm.telegram")

HELP = (
    "<b>Unicosm</b> — your day, woven from many systems.\n\n"
    "/today — your full woven reading\n"
    "/blueprint — your fixed birth signature\n"
    "/analyze &lt;date time place&gt; — read another person's day, e.g.\n"
    "  <code>/analyze 1991-07-08 09:15 London</code>\n"
    "/profiles — saved profiles\n"
    "/help — this message\n\n"
    "Tip: just send birth data like <code>1990-03-21 14:30 Kyiv</code> "
    "and I'll analyze it."
)

UNKNOWN = (
    "I didn't catch that. Try /help, or send birth data like "
    "<code>1990-03-21 14:30 Kyiv</code>."
)


def _active(profile_name: str | None):
    return store.get_profile(profile_name) if profile_name else store.active_profile()


def reply_for(text: str, *, profile_name: str | None = None,
              use_llm: bool = False, now=None) -> str:
    """Map one incoming message to a reply. Pure (engine/store reads only)."""
    text = (text or "").strip()
    head, _, arg = text.partition(" ")
    cmd = head.lower().lstrip("/").split("@", 1)[0]  # strip @botname in groups
    arg = arg.strip()

    if cmd in ("start", "help", ""):
        return HELP

    if cmd == "profiles":
        names = store.list_profiles()
        if not names:
            return "No profiles saved yet. Create one with the CLI: <code>unicosm profile set …</code>"
        active = store.active_profile()
        active_name = active.name if active else None
        return "<b>Profiles</b>\n" + "\n".join(
            ("• <b>" + fmt.esc(n) + "</b>" if n == active_name else "• " + fmt.esc(n))
            for n in names
        )

    if cmd in ("today", "blueprint"):
        p = _active(profile_name)
        if not p:
            return ("No profile yet. Create one with the CLI: "
                    "<code>unicosm profile set --name You --birth \"1990-03-21 14:30\" --place Kyiv</code>")
        rep = daily_report(p, now, use_llm=use_llm and cmd == "today")
        return fmt.today_message(rep) if cmd == "today" else fmt.blueprint_message(rep)

    # /analyze <data>, or a bare message that already looks like birth data
    is_bare_birth = not text.startswith("/") and bool(DATE_RE.search(text))
    if cmd == "analyze" or is_bare_birth:
        body = arg if cmd == "analyze" else text
        if not body.strip():
            return ("Send birth data after the command, e.g.\n"
                    "<code>/analyze 1991-07-08 09:15 London</code>")
        try:
            subject, warns = parse_birth(body)
        except ParseError as exc:
            return "⚠ " + str(exc)
        rep = daily_report(subject, now, use_llm=False)
        return fmt.analysis_message(rep, warns)

    return UNKNOWN


# ---- network edge -------------------------------------------------------

def _allowed(chat_id) -> bool:
    """Optional allowlist via $UNICOSM_TELEGRAM_ALLOW (comma-separated chat ids)."""
    allow = os.environ.get("UNICOSM_TELEGRAM_ALLOW", "").strip()
    if not allow:
        return True
    return str(chat_id) in {x.strip() for x in allow.split(",") if x.strip()}


def send_daily(token: str, chat_id, *, profile_name: str | None = None,
               use_llm: bool = False, now=None, client: TelegramClient | None = None):
    """Push today's concise reading to one chat (the cron path)."""
    client = client or TelegramClient(token)
    p = _active(profile_name)
    if p is None:
        raise TelegramError("no profile to send — create one with `unicosm profile set`")
    rep = daily_report(p, now, use_llm=use_llm)
    client.send_message(chat_id, fmt.daily_message(rep))
    return rep


def run(token: str, *, profile_name: str | None = None, use_llm: bool = False,
        poll_timeout: int = 30, client: TelegramClient | None = None) -> None:
    """Long-poll for messages and answer them. Blocks until interrupted."""
    client = client or TelegramClient(token, timeout=poll_timeout + 5)
    me = client.get_me()
    log.info("bot @%s online — polling for messages", me.get("username"))
    offset: int | None = None
    while True:
        try:
            updates = client.get_updates(offset=offset, timeout=poll_timeout)
        except TelegramError as exc:
            log.warning("getUpdates failed: %s", exc)
            time.sleep(3)
            continue
        for u in updates:
            offset = u["update_id"] + 1
            msg = u.get("message") or u.get("edited_message")
            if not msg or "text" not in msg:
                continue
            chat_id = msg["chat"]["id"]
            if not _allowed(chat_id):
                log.info("ignoring chat %s (not in allowlist)", chat_id)
                continue
            try:
                reply = reply_for(msg["text"], profile_name=profile_name, use_llm=use_llm)
            except Exception as exc:  # one bad message must not kill the bot
                log.exception("handler error")
                reply = "⚠ internal error: " + fmt.esc(exc)
            try:
                client.send_message(chat_id, reply)
            except TelegramError as exc:
                log.warning("send to %s failed: %s", chat_id, exc)
