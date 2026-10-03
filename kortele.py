"""Prisistatymo kortelė — pirmoji 001 pamokos užduotis.

Visos viešos funkcijos spausdina lietuviškas žinutes ir niekada nemeta klaidų.
"""

import unicodedata

_VIDUS = 46
_NULINIO_PLOCIO = {"\uFE0E", "\uFE0F", "\u200D"}

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
    if max_plotis <= 0:
        return ""
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


PLACEHOLDERS = {
    "vardas": "Jonas",
    "amzius": 16,
    "miestas": "Vilnius",
    "faktas": "moku groti gitara",
    "pomegiai": ["futbolas", "programavimas", "šunys"],
}

_paskutine_kortele = None


def _atstatyk():
    """Tik testams: pamiršta paskutinę atvaizduotą kortelę."""
    global _paskutine_kortele
    _paskutine_kortele = None


def _tinkama_interesu_pora(elementas):
    """Ar elementas yra (vardas, interesas) pora iš dviejų tekstų."""
    return (isinstance(elementas, (tuple, list)) and len(elementas) == 2
            and isinstance(elementas[0], str) and isinstance(elementas[1], str))


def _patikrink_ivesti(vardas, amzius, miestas, faktas, pomegiai, slapyvardis, tema,
                       bendri_interesai):
    """Grąžina lietuvišką žinutę apie pirmą rastą klaidą arba None."""
    for pavadinimas, reiksme in (("vardas", vardas), ("miestas", miestas), ("faktas", faktas)):
        if not isinstance(reiksme, str) or not reiksme.strip():
            return (f'❗ `{pavadinimas}` turi būti tekstas kabutėse, pvz. '
                    f'{pavadinimas} = "Birutė".')
    if isinstance(amzius, bool) or not isinstance(amzius, int):
        return "❗ `amzius` turi būti skaičius be kabučių, pvz. amzius = 16."
    if pomegiai is not None and not isinstance(pomegiai, list):
        return ('❗ `pomegiai` turi būti sąrašas laužtiniuose skliaustuose, pvz. '
                'pomegiai = ["futbolas", "šunys"].')
    if slapyvardis is not None and not isinstance(slapyvardis, str):
        return '❗ `slapyvardis` turi būti tekstas kabutėse.'
    if not isinstance(tema, str) or tema not in _TEMOS:
        return (f'❗ `tema` turi būti viena iš: ' + ", ".join(_TEMOS) +
                f'. Tu parašei „{tema}“.')
    if bendri_interesai is not None and (
            not isinstance(bendri_interesai, (list, tuple))
            or not all(_tinkama_interesu_pora(p) for p in bendri_interesai)):
        return ('❗ `bendri_interesai` turi būti sąrašas porų (vardas, interesas), pvz. '
                'bendri_interesai = [("Tomas", "krepšinis")].')
    return None


def _gauk_bendrus_interesus(bendri_interesai):
    if bendri_interesai is not None:
        return bendri_interesai
    try:
        import misija
    except ImportError:
        return []
    return misija.surinkti()


def rodyk_kortele(vardas, amzius, miestas, faktas, *, pomegiai=None,
                  slapyvardis=None, tema="klasika", bendri_interesai=None):
    """Atspausdina asmeninę kortelę."""
    global _paskutine_kortele

    klaida = _patikrink_ivesti(vardas, amzius, miestas, faktas, pomegiai, slapyvardis, tema,
                                bendri_interesai)
    if klaida:
        print(klaida)
        return

    t = _TEMOS[tema]
    virsus = t["vk"] + t["h"] * _VIDUS + t["vd"]
    skirtukas = t["sk"] + t["h"] * _VIDUS + t["sd"]
    apacia = t["ak"] + t["h"] * _VIDUS + t["ad"]

    eilutes = [virsus]
    eilutes.append(_eilute(f"  👤  {vardas.upper()}", t))
    eilutes.append(_eilute(f"      {amzius} m. · {miestas}", t))
    eilutes.append(skirtukas)
    eilutes.append(_eilute("  Apie mane:", t))
    eilutes.append(_eilute(f"    {faktas}", t))

    if pomegiai:
        eilutes.append(_eilute("  Pomėgiai:", t))
        for pomegis in pomegiai:
            eilutes.append(_eilute(f"    • {pomegis}", t))

    if slapyvardis:
        eilutes.append(_eilute(f"  Slapyvardis:  {slapyvardis}", t))

    interesai = _gauk_bendrus_interesus(bendri_interesai)
    if interesai:
        eilutes.append(skirtukas)
        eilutes.append(_eilute("  Bendri interesai:", t))
        for draugas, interesas in interesai:
            eilutes.append(_eilute(f"    su {draugas} – {interesas}", t))

    eilutes.append(apacia)
    print("\n".join(eilutes))

    _paskutine_kortele = {
        "vardas": vardas, "amzius": amzius, "miestas": miestas, "faktas": faktas,
        "pomegiai": pomegiai, "slapyvardis": slapyvardis, "tema": tema,
    }
