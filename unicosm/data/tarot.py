"""Tarot deck data — 78 cards. Major arcana hand-keyed; minors composed from
suit domain + rank theme (concise, consistent keywords)."""

from __future__ import annotations

# name -> (upright keywords, reversed keywords)
MAJOR = {
    "The Fool": ("new beginnings, leap of faith", "recklessness, hesitation"),
    "The Magician": ("will, manifestation, skill", "manipulation, untapped talent"),
    "The High Priestess": ("intuition, mystery, inner voice", "secrets, disconnection"),
    "The Empress": ("abundance, nurture, creativity", "smothering, blockage"),
    "The Emperor": ("structure, authority, order", "rigidity, domination"),
    "The Hierophant": ("tradition, guidance, learning", "dogma, rebellion"),
    "The Lovers": ("union, choice, values", "disharmony, misalignment"),
    "The Chariot": ("drive, willpower, victory", "scattered force, loss of control"),
    "Strength": ("courage, gentle power, patience", "self-doubt, raw force"),
    "The Hermit": ("solitude, inner search, wisdom", "isolation, withdrawal"),
    "Wheel of Fortune": ("change, cycles, turning point", "resistance, bad timing"),
    "Justice": ("truth, fairness, consequence", "imbalance, evasion"),
    "The Hanged Man": ("surrender, new perspective, pause", "stalling, martyrdom"),
    "Death": ("ending, transformation, release", "clinging, stagnation"),
    "Temperance": ("balance, blending, moderation", "excess, discord"),
    "The Devil": ("attachment, shadow, bondage", "release, awareness"),
    "The Tower": ("upheaval, revelation, collapse", "averted disaster, fear of change"),
    "The Star": ("hope, renewal, inspiration", "despair, disconnection"),
    "The Moon": ("illusion, the unconscious, dreams", "clarity emerging, confusion"),
    "The Sun": ("joy, vitality, success", "blocked joy, delay"),
    "Judgement": ("reckoning, awakening, calling", "self-doubt, avoidance"),
    "The World": ("completion, wholeness, arrival", "loose ends, near-finish"),
}

SUITS = {
    "Wands": "drive & creativity",
    "Cups": "emotion & connection",
    "Swords": "mind & truth",
    "Pentacles": "body, work & resources",
}

RANKS = {
    "Ace": "a new seed",
    "Two": "choice and balance",
    "Three": "early growth",
    "Four": "stability",
    "Five": "challenge and loss",
    "Six": "recovery and harmony",
    "Seven": "assessment, perseverance",
    "Eight": "movement and mastery",
    "Nine": "intensity near the end",
    "Ten": "culmination, its full weight",
    "Page": "a curious message",
    "Knight": "pursuit and momentum",
    "Queen": "nurturing mastery",
    "King": "authority and command",
}
