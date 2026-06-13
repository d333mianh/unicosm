"""A small bundled city gazetteer for offline --place lookup.

name (lowercased) -> (latitude N+, longitude E+, IANA timezone). Not exhaustive
— a convenience so onboarding doesn't require manual coordinates. Unknown cities
fall back to manual --lat/--lon/--tz.
"""

from __future__ import annotations

CITIES: dict[str, tuple[float, float, str]] = {
    # Ukraine
    "kyiv": (50.4501, 30.5234, "Europe/Kyiv"),
    "kiev": (50.4501, 30.5234, "Europe/Kyiv"),
    "lviv": (49.8397, 24.0297, "Europe/Kyiv"),
    "kharkiv": (49.9935, 36.2304, "Europe/Kyiv"),
    "odesa": (46.4825, 30.7233, "Europe/Kyiv"),
    "odessa": (46.4825, 30.7233, "Europe/Kyiv"),
    "dnipro": (48.4647, 35.0462, "Europe/Kyiv"),
    # Europe
    "london": (51.5074, -0.1278, "Europe/London"),
    "paris": (48.8566, 2.3522, "Europe/Paris"),
    "berlin": (52.5200, 13.4050, "Europe/Berlin"),
    "madrid": (40.4168, -3.7038, "Europe/Madrid"),
    "rome": (41.9028, 12.4964, "Europe/Rome"),
    "amsterdam": (52.3676, 4.9041, "Europe/Amsterdam"),
    "warsaw": (52.2297, 21.0122, "Europe/Warsaw"),
    "vienna": (48.2082, 16.3738, "Europe/Vienna"),
    "lisbon": (38.7223, -9.1393, "Europe/Lisbon"),
    "athens": (37.9838, 23.7275, "Europe/Athens"),
    "istanbul": (41.0082, 28.9784, "Europe/Istanbul"),
    "moscow": (55.7558, 37.6173, "Europe/Moscow"),
    "dublin": (53.3498, -6.2603, "Europe/Dublin"),
    "stockholm": (59.3293, 18.0686, "Europe/Stockholm"),
    "zurich": (47.3769, 8.5417, "Europe/Zurich"),
    "prague": (50.0755, 14.4378, "Europe/Prague"),
    # Americas
    "new york": (40.7128, -74.0060, "America/New_York"),
    "los angeles": (34.0522, -118.2437, "America/Los_Angeles"),
    "chicago": (41.8781, -87.6298, "America/Chicago"),
    "toronto": (43.6532, -79.3832, "America/Toronto"),
    "mexico city": (19.4326, -99.1332, "America/Mexico_City"),
    "sao paulo": (-23.5505, -46.6333, "America/Sao_Paulo"),
    "buenos aires": (-34.6037, -58.3816, "America/Argentina/Buenos_Aires"),
    "san francisco": (37.7749, -122.4194, "America/Los_Angeles"),
    # Asia / Middle East
    "delhi": (28.6139, 77.2090, "Asia/Kolkata"),
    "mumbai": (19.0760, 72.8777, "Asia/Kolkata"),
    "bangkok": (13.7563, 100.5018, "Asia/Bangkok"),
    "singapore": (1.3521, 103.8198, "Asia/Singapore"),
    "hong kong": (22.3193, 114.1694, "Asia/Hong_Kong"),
    "beijing": (39.9042, 116.4074, "Asia/Shanghai"),
    "shanghai": (31.2304, 121.4737, "Asia/Shanghai"),
    "tokyo": (35.6762, 139.6503, "Asia/Tokyo"),
    "seoul": (37.5665, 126.9780, "Asia/Seoul"),
    "hanoi": (21.0278, 105.8342, "Asia/Ho_Chi_Minh"),
    "dubai": (25.2048, 55.2708, "Asia/Dubai"),
    "tel aviv": (32.0853, 34.7818, "Asia/Jerusalem"),
    "jerusalem": (31.7683, 35.2137, "Asia/Jerusalem"),
    # Oceania / Africa
    "sydney": (-33.8688, 151.2093, "Australia/Sydney"),
    "melbourne": (-37.8136, 144.9631, "Australia/Melbourne"),
    "auckland": (-36.8485, 174.7633, "Pacific/Auckland"),
    "cairo": (30.0444, 31.2357, "Africa/Cairo"),
    "lagos": (6.5244, 3.3792, "Africa/Lagos"),
    "johannesburg": (-26.2041, 28.0473, "Africa/Johannesburg"),
}


def lookup(place: str) -> tuple[float, float, str] | None:
    return CITIES.get(place.strip().lower())
