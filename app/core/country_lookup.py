import re

COUNTRY_ALIASES = {
    "egypt": "EG",
    "مصر": "EG",
    "united states": "US",
    "usa": "US",
    "america": "US",
    "united kingdom": "GB",
    "uk": "GB",
    "britain": "GB",
    "saudi arabia": "SA",
    "ksa": "SA",
    "saudi": "SA",
    "united arab emirates": "AE",
    "uae": "AE",
    "emirates": "AE",
}


def match_country(text: str) -> str | None:
    lowered = text.lower()
    for alias in sorted(COUNTRY_ALIASES, key=len, reverse=True):
        if re.search(rf"\b{re.escape(alias)}\b", lowered):
            return COUNTRY_ALIASES[alias]
    return None