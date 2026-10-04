"""Flagų misija — antroji 001 pamokos užduotis.

Flagas išvedamas iš vardo ir klasės kodo, todėl niekur nereikia saugoti
mokinių sąrašo. Visos mokiniui skirtos funkcijos (`pradek_misija`,
`irasyk_flaga`, `misijos_bukle`) spausdina lietuviškas žinutes ir niekada
nemeta klaidų. `generuok_flaga` yra vidinė santechnika — ją naudoja šis
modulis ir mokytojo `poros.py`, ir ji meta `VardoKlaida`, kai iš vardo
flago sudaryti neįmanoma; kviečiantysis privalo tą klaidą pagauti.
"""

import hashlib
import hmac
import re
import unicodedata


class VardoKlaida(ValueError):
    """Vidinė klaida: iš vardo neįmanoma sudaryti flago."""


def normalizuok(vardas):
    """Suvienodina vardo rašybą: be diakritikų, mažosiomis, be tarpų perteklių."""
    if not isinstance(vardas, str):
        return ""
    isskaidytas = unicodedata.normalize("NFD", vardas)
    be_kirciu = "".join(c for c in isskaidytas if not unicodedata.combining(c))
    return " ".join(be_kirciu.casefold().split())


_TIK_RAIDES = re.compile(r"[^a-z]")


def _normalizuok_koda(klases_kodas):
    """Klasės kodas rašomas ant lentos, tad registras ir tarpai nesvarbūs."""
    if not isinstance(klases_kodas, str):
        return ""
    return klases_kodas.strip().upper()


def generuok_flaga(vardas, klases_kodas):
    """Grąžina flagą pavidalu RAID-1234. Meta VardoKlaida, jei vardas netinka."""
    normalizuotas = normalizuok(vardas)
    raides = _TIK_RAIDES.sub("", normalizuotas)[:4].upper()
    if len(raides) < 2:
        raise VardoKlaida(vardas)
    parasas = hmac.new(
        _normalizuok_koda(klases_kodas).encode("utf-8"),
        normalizuotas.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    skaitmenys = int.from_bytes(parasas[:4], "big") % 10000
    return f"{raides}-{skaitmenys:04d}"


PAVYZDYS = ("Vardenis", "VARD-0000", "krepšinis")

# Klasės kodo vietaženklis, kuris atkeliauja į `turinys/05_misija.py` per
# build.py žymeklį @@pavyzdys_kodas@@. Tikras kodas visada ateina nuo lentos,
# tad lygybė su šiuo tekstu reiškia, kad langelis dar nepataisytas.
PLACEHOLDER_KODAS = "KLASES-KODAS"


def _vardo_vietazenklis():
    """Vardo vietaženklis iš kortele.py arba None, jei to modulio nėra.

    Importas tingus ir apsaugotas: `kortele` priklauso nuo `misija` (tingiu
    importu funkcijos viduje), tad modulio lygmens importas čia uždarytų ratą,
    o `misija.py` turi likti paleidžiamas ir vienas.
    """
    try:
        import kortele
    except ImportError:
        return None
    return kortele.PLACEHOLDERS.get("vardas")


_mano_vardas = None
_mano_norm = None
_klases_kodas = None
_draugai = []


def _atstatyk():
    """Tik testams: išvalo misijos būseną."""
    global _mano_vardas, _mano_norm, _klases_kodas, _draugai
    _mano_vardas = None
    _mano_norm = None
    _klases_kodas = None
    _draugai = []


def pradek_misija(vardas, klases_kodas):
    """Užregistruoja mokinį ir parodo jo flagą."""
    global _mano_vardas, _mano_norm, _klases_kodas, _draugai

    if not isinstance(vardas, str) or not vardas.strip():
        print('❗ Įrašyk savo vardą kabutėse, pvz. pradek_misija("Birutė", "ZEBRAI2026").')
        return
    if not isinstance(klases_kodas, str) or not klases_kodas.strip():
        print("❗ Klasės kodas užrašytas ant lentos — įrašyk jį kabutėse.")
        return
    # Nepataisytas langelis: klasės kodas yra vienintelis vienareikšmis ženklas —
    # tikras kodas visada ateina nuo lentos, tad niekas jo taip nepavadins.
    # Registruoti negalima: tokiu atveju mokinys gautų svetimą flagą ir visus
    # tris raundus klaidingai kaltintų draugus.
    if _normalizuok_koda(klases_kodas) == PLACEHOLDER_KODAS:
        print("✋ Čia dar pavyzdiniai duomenys — misija nepradėta.")
        print("   Įrašyk savo vardą (tokį, koks parašytas porų lentelėje) ir klasės")
        print('   kodą nuo lentos, pvz. pradek_misija("Birutė", "ZEBRAI2026").')
        return

    # Vardas, priešingai, dviprasmis: „Jonas“ yra ir vietaženklis, ir labai
    # dažnas tikras vardas. Blokuoti tikrą Joną reikštų visai neįleisti jo į
    # antrą pamokos dalį, tad čia tik priminimas — registracija vyksta.
    vardo_vietazenklis = _vardo_vietazenklis()
    if vardo_vietazenklis and normalizuok(vardas) == normalizuok(vardo_vietazenklis):
        print(f"✋ Vardas vis dar „{vardo_vietazenklis}“ — jei tai ne tavo vardas,")
        print("   pakeisk jį savo ir paleisk langelį iš naujo.")

    try:
        flagas = generuok_flaga(vardas, klases_kodas)
    except VardoKlaida:
        print(f"❗ Iš vardo „{vardas}“ flago sudaryti nepavyko — jame per mažai raidžių.")
        print("   Įrašyk vardą taip, kaip jis parašytas lentoje.")
        return

    naujas_norm = normalizuok(vardas)
    if naujas_norm != _mano_norm:
        # Vardo pataisymas yra būtent tai, ko vadove prašoma iš mokinio, kurio
        # rašyba nesutampa su lentele — tad tylus surinktų flagų ištrynimas
        # nutiktų blogiausiu įmanomu momentu. Ištrinam, bet pasakom.
        if _draugai:
            print("⚠ Pakeitei vardą, tad anksčiau surinkti flagai nebegalioja —"
                  " jie buvo susieti su ankstesne rašyba.")
        _draugai = []

    _mano_vardas = vardas.strip()
    _mano_norm = naujas_norm
    _klases_kodas = klases_kodas

    print("🎒 Misija pradėta!")
    print(f"   Tavo flagas:     {flagas}")
    print(f"   Sakyk draugams:  {_mano_vardas}")
    print("   Po kiekvieno pokalbio užpildyk ir paleisk kitą langelį.")


def irasyk_flaga(vardas, flagas, bendras_interesas):
    """Patikrina draugo flagą ir įrašo jūsų bendrą interesą."""
    if _mano_norm is None:
        print("❗ Pirmiausia paleisk langelį su pradek_misija(...).")
        return

    if not isinstance(vardas, str) or not isinstance(flagas, str):
        print('❗ Vardas ir flagas rašomi kabutėse, pvz. irasyk_flaga("Tomas", "TOMA-4417", "krepšinis").')
        return

    pavyzdinis_vardas, pavyzdinis_flagas, _ = PAVYZDYS
    if (normalizuok(vardas) == normalizuok(pavyzdinis_vardas)
            and flagas.strip().upper() == pavyzdinis_flagas):
        print("👀 Čia pavyzdys — įrašyk tikro draugo vardą, jo flagą ir jūsų bendrą interesą.")
        return

    if not isinstance(bendras_interesas, str) or not bendras_interesas.strip():
        print("❗ Įrašyk, koks jūsų bendras interesas — be to flagas neužskaitomas.")
        return

    svetimas_norm = normalizuok(vardas)
    if svetimas_norm == _mano_norm:
        print("🙃 Savo paties flago įrašyti negalima. Eik pas tą žmogų, kuris nurodytas lentoje.")
        return

    if any(d["norm"] == svetimas_norm for d in _draugai):
        print(f"ℹ Su {vardas} jau apsikeitėte. Eik pas kitą!")
        return

    try:
        laukiamas = generuok_flaga(vardas, _klases_kodas)
    except VardoKlaida:
        print(f"❗ Iš vardo „{vardas}“ flago sudaryti nepavyko. Patikrink rašybą.")
        return

    if flagas.strip().upper() != laukiamas:
        print(f"❌ Flagas netinka. Patikrink: ar gerai nurašei vardą „{vardas}“ ir jo flagą?")
        print(f"   Jo flagas turėtų prasidėti „{laukiamas.split('-')[0]}-“.")
        print("   Jei visi flagai netinka — patikrink savo pradek_misija(...)"
              " eilutę: vardą ir klasės kodą.")
        return

    _draugai.append({
        "vardas": vardas.strip(),
        "norm": svetimas_norm,
        "interesas": bendras_interesas.strip(),
    })
    print(f"✅ {vardas.strip()} — {bendras_interesas.strip()}")


def surinkti():
    """Grąžina [(vardas, bendras interesas), ...] įrašymo tvarka."""
    return [(d["vardas"], d["interesas"]) for d in _draugai]


def misijos_bukle():
    """Parodo, kiek pokalbių jau įskaityta."""
    if _mano_norm is None:
        print("❗ Pirmiausia paleisk langelį su pradek_misija(...).")
        return
    print(f"📋 Surinkta flagų: {len(_draugai)}")
    for draugas in _draugai:
        print(f"   ✅ {draugas['vardas']} – {draugas['interesas']}")
