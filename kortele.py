"""Prisistatymo kortelė — pirmoji 001 pamokos užduotis.

Visos viešos funkcijos spausdina lietuviškas žinutes ir niekada nemeta klaidų.
"""

import unicodedata

_VIDUS = 46
_NULINIO_PLOCIO = {"︎", "️", "‍"}

_EMOJI_REZIAI = (
    (0x1F300, 0x1FAFF),
    (0x1F000, 0x1F2FF),
    (0x2600, 0x27BF),
)

_TEMOS = {
    "klasika": {"vk": "╔", "vd": "╗", "ak": "╚", "ad": "╝",
                "h": "═", "v": "║", "sk": "╠", "sd": "╣"},
    "matrix":  {"vk": "+", "vd": "+", "ak": "+", "ad": "+",
                "h": "-", "v": "|", "sk": "+", "sd": "+"},
    "neonas":  {"vk": "┏", "vd": "┓", "ak": "┗", "ad": "┛",
                "h": "━", "v": "┃", "sk": "┣", "sd": "┫"},
}


def _yra_emoji(simbolis):
    kodas = ord(simbolis)
    return any(pradzia <= kodas <= pabaiga for pradzia, pabaiga in _EMOJI_REZIAI)


def _plotis(tekstas):
    """Kiek stulpelių užima tekstas monospace šrifte."""
    suma = 0
    for simbolis in tekstas:
        if unicodedata.combining(simbolis) or simbolis in _NULINIO_PLOCIO:
            continue
        if unicodedata.east_asian_width(simbolis) in ("W", "F") or _yra_emoji(simbolis):
            suma += 2
        else:
            suma += 1
    return suma


def _apkarpyk(tekstas, max_plotis):
    """Sutrumpina tekstą, kad kortelės rėmelis nesulūžtų."""
    if _plotis(tekstas) <= max_plotis:
        return tekstas
    surinkta = ""
    for simbolis in tekstas:
        if _plotis(surinkta + simbolis) > max_plotis - 1:
            break
        surinkta += simbolis
    return surinkta + "…"


def _eilute(turinys, tema):
    """Viena kortelės eilutė su rėmeliu iš abiejų pusių."""
    apkarpyta = _apkarpyk(turinys, _VIDUS)
    uzpildas = " " * (_VIDUS - _plotis(apkarpyta))
    return f"{tema['v']}{apkarpyta}{uzpildas}{tema['v']}"
