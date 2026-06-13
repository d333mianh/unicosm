"""Human Design — the bodygraph from birth (Personality) + Design (88° prior).

Computes type, strategy, authority, profile, definition, defined centers and
channels. Blueprint layer. Also exposes a daily transit-Sun gate reading.
"""

from __future__ import annotations

from ..core import hd
from ..data.gene_keys import SPECTRUM
from ..data.human_design import (
    CENTER_LABEL,
    CHANNELS,
    GATE_CENTER,
    MOTORS,
    PROFILE_LINE,
)
from ..models import Cadence, Layer, SystemReading

STRATEGY = {
    "Manifestor": "to inform, then initiate",
    "Generator": "to respond (wait for something to respond to)",
    "Manifesting Generator": "to respond, then inform before you act",
    "Projector": "to wait for the invitation (to be recognized)",
    "Reflector": "to wait a full lunar cycle before deciding",
}


def _components(centers: set[str], channels: list[tuple[str, str]]) -> int:
    """Number of connected components among defined centers."""
    if not centers:
        return 0
    adj: dict[str, set[str]] = {c: set() for c in centers}
    for ca, cb in channels:
        if ca in centers and cb in centers and ca != cb:
            adj[ca].add(cb)
            adj[cb].add(ca)
    seen: set[str] = set()
    comps = 0
    for c in centers:
        if c in seen:
            continue
        comps += 1
        stack = [c]
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            stack.extend(adj[n] - seen)
    return comps


def _connected(a: str, b: str, centers: set[str],
               channels: list[tuple[str, str]]) -> bool:
    if a not in centers or b not in centers:
        return False
    adj: dict[str, set[str]] = {c: set() for c in centers}
    for ca, cb in channels:
        if ca in centers and cb in centers:
            adj[ca].add(cb)
            adj[cb].add(ca)
    stack, seen = [a], set()
    while stack:
        n = stack.pop()
        if n == b:
            return True
        seen.add(n)
        stack.extend(adj[n] - seen)
    return False


def _definition_label(n: int) -> str:
    return {0: "No definition", 1: "Single", 2: "Split",
            3: "Triple split", 4: "Quadruple split"}.get(n, f"{n}-way split")


def compute_chart(birth_jd: float) -> dict:
    pers = hd.activations(birth_jd)
    des = hd.activations(hd.design_jd(birth_jd))

    active = {g for _, g, _ in pers.values()} | {g for _, g, _ in des.values()}
    center_channels = [
        (GATE_CENTER[a], GATE_CENTER[b])
        for a, b in CHANNELS if a in active and b in active
    ]
    defined_channels = [(a, b) for a, b in CHANNELS if a in active and b in active]
    defined_centers = {c for pair in center_channels for c in pair}

    sacral = "Sacral" in defined_centers
    throat = "Throat" in defined_centers
    motor_to_throat = throat and any(
        _connected("Throat", m, defined_centers, center_channels)
        for m in MOTORS if m in defined_centers
    )

    if not defined_centers:
        typ = "Reflector"
    elif sacral and motor_to_throat:
        typ = "Manifesting Generator"
    elif sacral:
        typ = "Generator"
    elif motor_to_throat:
        typ = "Manifestor"
    else:
        typ = "Projector"

    if "Solar Plexus" in defined_centers:
        authority = "Emotional (Solar Plexus) — wait out the wave"
    elif sacral:
        authority = "Sacral — trust the gut response"
    elif "Spleen" in defined_centers:
        authority = "Splenic — the quiet in-the-moment knowing"
    elif "Heart" in defined_centers:
        authority = "Ego (Heart) — what do you have the will for"
    elif "G" in defined_centers:
        authority = "Self-projected (G) — hear yourself talk it out"
    elif defined_centers & {"Head", "Ajna", "Throat"}:
        authority = "Mental (none) — use a sounding board"
    else:
        authority = "Lunar (Reflector) — a full lunar cycle"

    p_line, d_line = pers["Sun"][2], des["Sun"][2]
    profile = f"{p_line}/{d_line}"
    profile_name = f"{PROFILE_LINE[p_line]}/{PROFILE_LINE[d_line]}"
    definition = _definition_label(_components(defined_centers, center_channels))

    return {
        "type": typ,
        "strategy": STRATEGY[typ],
        "authority": authority,
        "profile": profile,
        "profile_name": profile_name,
        "definition": definition,
        "defined_centers": sorted(defined_centers),
        "channels": [f"{a}-{b}" for a, b in defined_channels],
        "personality": pers,
        "design": des,
        "incarnation_cross": {
            "personality_sun": f"{pers['Sun'][1]}.{pers['Sun'][2]}",
            "personality_earth": f"{pers['Earth'][1]}.{pers['Earth'][2]}",
            "design_sun": f"{des['Sun'][1]}.{des['Sun'][2]}",
            "design_earth": f"{des['Earth'][1]}.{des['Earth'][2]}",
        },
    }


def reading(ctx) -> SystemReading:
    c = compute_chart(ctx.natal.jd)
    centers_label = ", ".join(CENTER_LABEL.get(x, x) for x in c["defined_centers"]) or "none"
    summary = (
        f"{c['type']} · {c['profile']} {c['profile_name']} · "
        f"{c['authority'].split(' — ')[0]} authority. "
        f"Strategy: {c['strategy']}. "
        f"{c['definition']} ({len(c['defined_centers'])}/9 centers defined)."
    )
    return SystemReading(
        key="human_design",
        title="Human Design",
        cadence=Cadence.BLUEPRINT,
        layer=Layer.BLUEPRINT,
        summary=summary,
        detail={
            "type": c["type"], "strategy": c["strategy"],
            "authority": c["authority"], "profile": f"{c['profile']} ({c['profile_name']})",
            "definition": c["definition"],
            "defined_centers": centers_label,
            "channels": ", ".join(c["channels"]) or "none",
            "incarnation_cross": " | ".join(c["incarnation_cross"].values()),
        },
        keywords=[c["type"].lower(), "strategy"],
    )


def transit(ctx) -> SystemReading:
    """Daily layer: the gate the transiting Sun is moving through today."""
    acts = hd.activations(ctx.jd_now)
    gate, line = acts["Sun"][1], acts["Sun"][2]
    shadow, gift, siddhi = SPECTRUM[gate]
    return SystemReading(
        key="hd_transit",
        title="HD transit (Sun gate)",
        cadence=Cadence.DAILY,
        layer=Layer.COSMIC,
        summary=(
            f"Transit Sun in Gate {gate}.{line} — the collective theme moves from "
            f"{shadow.lower()} toward {gift.lower()}."
        ),
        detail={"gate": gate, "line": line, "shadow": shadow,
                "gift": gift, "siddhi": siddhi},
        keywords=[gift.lower()],
    )
