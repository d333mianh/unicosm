"""Minimal Telegram Bot API client — stdlib only, no extra dependency.

The network lives here and only here, so the rest of the package stays pure and
testable. Kept deliberately tiny: the three calls a personal bot needs
(getMe / sendMessage / getUpdates long-poll).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

API_ROOT = "https://api.telegram.org"


class TelegramError(RuntimeError):
    """Any failure talking to Telegram (network or API-level `ok: false`)."""


class TelegramClient:
    def __init__(self, token: str, *, timeout: int = 35, base: str = API_ROOT):
        if not token:
            raise TelegramError(
                "no bot token — set $UNICOSM_TELEGRAM_TOKEN (from @BotFather) "
                "or pass --token"
            )
        self.token = token
        self.timeout = timeout
        self._base = f"{base}/bot{token}"

    def _call(self, method: str, **params) -> object:
        url = f"{self._base}/{method}"
        clean = {k: v for k, v in params.items() if v is not None}
        data = urllib.parse.urlencode(clean).encode()
        req = urllib.request.Request(url, data=data)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                payload = json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            # Telegram returns useful JSON even on 4xx; surface its description.
            try:
                desc = json.loads(exc.read().decode()).get("description", str(exc))
            except Exception:
                desc = str(exc)
            raise TelegramError(f"{method} failed: {desc}") from exc
        except urllib.error.URLError as exc:
            raise TelegramError(f"network error calling {method}: {exc.reason}") from exc
        if not payload.get("ok"):
            raise TelegramError(f"{method} failed: {payload.get('description')}")
        return payload["result"]

    def get_me(self) -> dict:
        return self._call("getMe")  # type: ignore[return-value]

    def send_message(self, chat_id, text: str, *, parse_mode: str | None = "HTML",
                     disable_preview: bool = True) -> dict:
        return self._call(  # type: ignore[return-value]
            "sendMessage",
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            disable_web_page_preview="true" if disable_preview else None,
        )

    def get_updates(self, offset: int | None = None, timeout: int = 30) -> list[dict]:
        return self._call("getUpdates", offset=offset, timeout=timeout)  # type: ignore[return-value]
