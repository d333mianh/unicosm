"""Daily reach — a concise morning message dispatched as an OS notification.

Best-effort across Linux (notify-send), macOS (osascript / terminal-notifier);
falls back to stdout. Pair with `--cron` for a once-a-day push.
"""

from __future__ import annotations

import shutil
import subprocess

from .engine import DailyReport


def build_message(rep: DailyReport) -> tuple[str, str]:
    title = f"☉ Unicosm · {rep.now:%a %d %b}"
    lines = [rep.synthesis.headline]
    if rep.synthesis.accents:
        lines.append("• " + rep.synthesis.accents[0])
    dt = rep.timing
    if dt and dt.sunrise:
        bad = dt.active_inauspicious(rep.now)
        cur = dt.current_choghadiya(rep.now)
        if bad:
            lines.append(f"⚠ {bad.label} until {bad.end:%H:%M}")
        elif cur and cur.quality == "good":
            lines.append(f"✓ good window now ({cur.label.split()[-1]})")
    return title, "\n".join(lines)


def dispatch(title: str, body: str) -> bool:
    """Send an OS notification. Returns True if a notifier handled it."""
    if shutil.which("notify-send"):
        cmd = ["notify-send", title, body]
    elif shutil.which("terminal-notifier"):
        cmd = ["terminal-notifier", "-title", title, "-message", body]
    elif shutil.which("osascript"):
        safe = body.replace('"', "'")
        cmd = ["osascript", "-e",
               f'display notification "{safe}" with title "{title}"']
    else:
        return False
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=10)
        return True
    except Exception:
        return False
