"""Elder Futhark — 24 runes. (name, glyph, meaning, reversed/merkstave, invertible)

Eight symmetric runes have no reversed form (invertible=False)."""

from __future__ import annotations

# (name, glyph, upright meaning, merkstave meaning, invertible)
RUNES = [
    ("Fehu", "ᚠ", "wealth, abundance, earned gain", "loss, greed, dependency", True),
    ("Uruz", "ᚢ", "vitality, raw strength, will", "weakness, misused force", True),
    ("Thurisaz", "ᚦ", "catalyst, defense, a hard gate", "danger, reactivity", True),
    ("Ansuz", "ᚨ", "insight, communication, the word", "miscommunication, deceit", True),
    ("Raidho", "ᚱ", "journey, rhythm, right action", "disruption, aimless travel", True),
    ("Kenaz", "ᚲ", "vision, the torch, craft", "loss of clarity, burnout", True),
    ("Gebo", "ᚷ", "gift, exchange, partnership", "", False),
    ("Wunjo", "ᚹ", "joy, harmony, belonging", "discord, alienation", True),
    ("Hagalaz", "ᚺ", "disruption, the necessary storm", "", False),
    ("Nauthiz", "ᚾ", "need, constraint, resilience", "lack, friction, haste", True),
    ("Isa", "ᛁ", "stillness, ice, a needed pause", "", False),
    ("Jera", "ᛃ", "harvest, cycles, just reward", "", False),
    ("Eihwaz", "ᛇ", "endurance, the axis, transition", "", False),
    ("Perthro", "ᛈ", "mystery, chance, the hidden", "stagnation, secrets kept", True),
    ("Algiz", "ᛉ", "protection, the higher self", "vulnerability, drained boundaries", True),
    ("Sowilo", "ᛋ", "sun, success, wholeness", "", False),
    ("Tiwaz", "ᛏ", "honor, justice, courage", "injustice, waning drive", True),
    ("Berkano", "ᛒ", "growth, birth, tending", "stunted growth, neglect", True),
    ("Ehwaz", "ᛖ", "movement, trust, partnership", "stalled progress, disharmony", True),
    ("Mannaz", "ᛗ", "the self, humanity, the social", "isolation, self-deception", True),
    ("Laguz", "ᛚ", "water, flow, the unconscious", "overwhelm, avoidance", True),
    ("Ingwaz", "ᛜ", "fertility, gestation, completion", "", False),
    ("Othala", "ᛟ", "heritage, home, what endures", "rootlessness, clinging to past", True),
    ("Dagaz", "ᛞ", "breakthrough, dawn, awakening", "", False),
]
