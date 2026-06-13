"""TCM organ clock — the hourly qi-circulation layer.

24 hours, 12 two-hour windows, each the peak time of one organ meridian.
Pairs naturally with the planetary hour and with practice timing.
"""

from __future__ import annotations

from ..models import Cadence, Layer, SystemReading

# start_hour -> (organ, guidance, keywords)
ORGANS = {
    3: ("Lung", "deep rest; ideal for breathwork near waking", ["breathe", "rest"]),
    5: ("Large Intestine", "wake, eliminate, hydrate", ["release", "hydrate"]),
    7: ("Stomach", "eat the biggest meal; nourish", ["nourish", "fuel"]),
    9: ("Spleen", "focused work, learning, digestion of ideas", ["focus", "work"]),
    11: ("Heart", "connection, joy, lighter food", ["connect", "uplift"]),
    13: ("Small Intestine", "sort and decide; main digestion", ["decide", "sort"]),
    15: ("Bladder", "study, store information, hydrate", ["study", "store"]),
    17: ("Kidney", "restore, gentle movement, light dinner", ["restore", "ground"]),
    19: ("Pericardium", "relationship, warmth, wind down", ["relate", "soften"]),
    21: ("Triple Burner", "settle, prepare for sleep", ["settle", "calm"]),
    23: ("Gallbladder", "be asleep; cellular repair, decisions", ["sleep", "repair"]),
    1: ("Liver", "deep sleep; detox and dreaming", ["sleep", "cleanse"]),
}


def _block_start(hour: int) -> int:
    # blocks start at odd hours 1,3,5,...,23
    return hour - 1 if hour % 2 == 0 else hour


def reading(ctx) -> SystemReading:
    h = ctx.now.hour
    start = _block_start(h)
    if start not in ORGANS:
        start = (start - 1) % 24 or 23
    organ, guide, kw = ORGANS[start]
    return SystemReading(
        key="tcm_organ",
        title="TCM organ clock",
        cadence=Cadence.HOURLY,
        layer=Layer.COSMIC,
        summary=f"{organ} time ({start:02d}:00–{(start+2) % 24:02d}:00) — {guide}.",
        detail={"organ": organ, "window": f"{start:02d}:00-{(start+2)%24:02d}:00"},
        keywords=kw,
    )
