"""Gene Keys — the Activation Sequence (the four Prime Gifts).

Uses the same gate calculation as Human Design. Life's Work + Evolution from the
Personality (birth) Sun/Earth; Radiance + Purpose from the Design (88° prior)
Sun/Earth. Each gate maps to a Shadow → Gift → Siddhi spectrum.
"""

from __future__ import annotations

from ..core import hd
from ..data.gene_keys import SPECTRUM
from ..models import Cadence, Layer, SystemReading

# (label, side, body)
PRIME_GIFTS = [
    ("Life's Work", "personality", "Sun"),
    ("Evolution", "personality", "Earth"),
    ("Radiance", "design", "Sun"),
    ("Purpose", "design", "Earth"),
]


def reading(ctx) -> SystemReading:
    pers = hd.activations(ctx.natal.jd)
    des = hd.activations(hd.design_jd(ctx.natal.jd))
    sides = {"personality": pers, "design": des}

    gifts = {}
    for label, side, body in PRIME_GIFTS:
        gate = sides[side][body][1]
        line = sides[side][body][2]
        shadow, gift, siddhi = SPECTRUM[gate]
        gifts[label] = {
            "gene_key": gate, "line": line,
            "shadow": shadow, "gift": gift, "siddhi": siddhi,
        }

    lw = gifts["Life's Work"]
    summary = (
        f"Life's Work GK{lw['gene_key']}.{lw['line']} — "
        f"contemplate the path from {lw['shadow']} through {lw['gift']} "
        f"to {lw['siddhi']}."
    )
    return SystemReading(
        key="gene_keys",
        title="Gene Keys (Activation Sequence)",
        cadence=Cadence.BLUEPRINT,
        layer=Layer.BLUEPRINT,
        summary=summary,
        detail={
            label: (f"GK{g['gene_key']}.{g['line']}  "
                    f"{g['shadow']} → {g['gift']} → {g['siddhi']}")
            for label, g in gifts.items()
        },
        keywords=[gifts["Life's Work"]["gift"].lower(),
                  gifts["Purpose"]["gift"].lower()],
    )
