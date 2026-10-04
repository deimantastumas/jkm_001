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

# ANSI spalvų kodai. Jupyter (ir JupyterLite) juos atvaizduoja kaip tikras
# spalvas. Spalva uždedama TIK ant galutinės, jau užpildytos eilutės — jei
# kodai patektų į tekstą anksčiau, `_plotis` juos skaičiuotų kaip matomus
# simbolius ir rėmelis sulūžtų.
_SPALVU_PABAIGA = "\033[0m"

_TEMOS = {
    "klasika": {"vk": "╔", "vd": "╗", "ak": "╚", "ad": "╝",
                "h": "═", "v": "║", "sk": "╠", "sd": "╣",
                "spalva": ""},
    "matrix":  {"vk": "+", "vd": "+", "ak": "+", "ad": "+",
                "h": "-", "v": "|", "sk": "+", "sd": "+",
                "spalva": "\033[92m"},
    "neonas":  {"vk": "┏", "vd": "┓", "ak": "┗", "ad": "┛",
                "h": "━", "v": "┃", "sk": "┣", "sd": "┫",
                "spalva": "\033[95m"},
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


def _lauzyk(tekstas, plotis):
    """Perkelia ilgą tekstą į kelias eilutes, laužydamas ties žodžių ribomis.

    Laisvo teksto laukus (`svajoniu_projektas`, `faktas`) mokinys skaito
    garsiai, tad jų nukirsti negalima. Matuojama `_plotis`, o ne `len`, kad
    emoji ir lietuviškos raidės būtų suskaičiuotos teisingai. Žodis, ilgesnis
    už visą eilutę, apkarpomas — kitaip rėmelis sulūžtų.
    """
    eilutes = []
    dabartine = ""
    for zodis in tekstas.split():
        if not dabartine:
            kandidatas = zodis
        else:
            kandidatas = f"{dabartine} {zodis}"
        if _plotis(kandidatas) <= plotis:
            dabartine = kandidatas
            continue
        if dabartine:
            eilutes.append(dabartine)
        while _plotis(zodis) > plotis:
            eilutes.append(_apkarpyk(zodis, plotis))
            zodis = ""
        dabartine = zodis
    if dabartine:
        eilutes.append(dabartine)
    return eilutes or [""]


def _nuspalvink(eilutes, tema):
    """Apgaubia kiekvieną GATAVĄ eilutę temos spalva.

    Daroma paskutiniu žingsniu, kai eilutės jau užpildytos iki `_VIDUS`, kad
    ANSI kodai niekada nepatektų į pločio skaičiavimą.
    """
    spalva = tema.get("spalva", "")
    if not spalva:
        return eilutes
    return [f"{spalva}{e}{_SPALVU_PABAIGA}" for e in eilutes]


def _eilutes_su_lauzymu(tekstas, iktrauka, tema):
    """Kortelės eilutės vienam laisvo teksto laukui, su įtrauka."""
    return [_eilute(f"{iktrauka}{e}", tema)
            for e in _lauzyk(tekstas, _VIDUS - _plotis(iktrauka))]


PLACEHOLDERS = {
    "vardas": "Deimantas",
    "amzius": 28,
    "svajoniu_projektas": "Nuotykių programėlė",
    "faktas": "Turiu dvi kates",
    "pomegiai": ["laipiojimas", "programavimas", "choras"],
}

def _tinkama_interesu_pora(elementas):
    """Ar elementas yra (vardas, interesas) pora iš dviejų tekstų."""
    return (isinstance(elementas, (tuple, list)) and len(elementas) == 2
            and isinstance(elementas[0], str) and isinstance(elementas[1], str))


def _patikrink_ivesti(vardas, amzius, svajoniu_projektas, faktas, pomegiai, slapyvardis, tema,
                       bendri_interesai):
    """Grąžina lietuvišką žinutę apie pirmą rastą klaidą arba None."""
    for pavadinimas, reiksme in (("vardas", vardas),
                                 ("svajoniu_projektas", svajoniu_projektas),
                                 ("faktas", faktas)):
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


def rodyk_kortele(vardas, amzius, svajoniu_projektas, faktas, *, pomegiai=None,
                  slapyvardis=None, tema="klasika", bendri_interesai=None):
    """Atspausdina asmeninę kortelę."""
    klaida = _patikrink_ivesti(vardas, amzius, svajoniu_projektas, faktas, pomegiai,
                                slapyvardis, tema,
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
    eilutes.append(_eilute(f"      {amzius} m.", t))
    eilutes.append(skirtukas)
    eilutes.append(_eilute("  Svajonių projektas:", t))
    eilutes.extend(_eilutes_su_lauzymu(svajoniu_projektas, "    ", t))
    eilutes.append(_eilute("  Apie mane:", t))
    eilutes.extend(_eilutes_su_lauzymu(faktas, "    ", t))

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
            # Be „su“: taisyklinga lietuvių kalba reikalautų įnagininko („su
            # Tomu“), o linksniavimas yra už šios pamokos ribų. Vardas
            # vardininku be prielinksnio skamba teisingai.
            eilutes.append(_eilute(f"    {draugas} – {interesas}", t))

    eilutes.append(apacia)
    print("\n".join(_nuspalvink(eilutes, t)))



def patikrink(lygis):
    """Pažymi, kad lygis atliktas.

    Sąmoningai nieko netikrina: mokytojas pats padeda, jei kam nors nesiseka.
    Automatinis tikrinimas buvo pašalintas — jis klaidingai priekaištaudavo
    mokiniams, kurie viską padarė teisingai, ir atimdavo iš mokytojo
    galimybę pamatyti, kur iš tikrųjų stringama.
    """
    print(f"✅ {lygis} lygis įveiktas!")
