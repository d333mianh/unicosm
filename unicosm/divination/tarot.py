"""Tarot draw — 78-card deck, single card or three-card spread, with reversals."""

from __future__ import annotations

import random
from dataclasses import dataclass

from ..data.tarot import MAJOR, RANKS, SUITS


@dataclass
class DrawnCard:
    name: str
    upright_kw: str
    reversed_kw: str
    reversed: bool


def _deck() -> list[tuple[str, str, str]]:
    """(name, upright_kw, reversed_kw) for all 78 cards."""
    cards = [(n, up, rev) for n, (up, rev) in MAJOR.items()]
    for suit, domain in SUITS.items():
        for rank, theme in RANKS.items():
            name = f"{rank} of {suit}"
            up = f"{theme} — {domain}"
            rev = f"blocked/excess {theme.split(',')[0]} in {domain}"
            cards.append((name, up, rev))
    return cards


def draw_cards(rng: random.Random | None = None, n: int = 1) -> list[DrawnCard]:
    r = rng or random.Random()
    picks = r.sample(_deck(), n)
    return [DrawnCard(name, up, rev, r.random() < 0.5) for name, up, rev in picks]
