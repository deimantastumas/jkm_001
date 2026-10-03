"""Flagų misija — antroji 001 pamokos užduotis.

Flagas išvedamas iš vardo ir klasės kodo, todėl niekur nereikia saugoti
mokinių sąrašo. Visos viešos funkcijos spausdina lietuviškas žinutes ir
niekada nemeta klaidų.
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

_mano_vardas = None
_mano_norm = None
_klases_kodas = None
_tikslas = 3
_draugai = []


def _atstatyk():
    """Tik testams: išvalo misijos būseną."""
    global _mano_vardas, _mano_norm, _klases_kodas, _tikslas, _draugai
    _mano_vardas = None
    _mano_norm = None
    _klases_kodas = None
    _tikslas = 3
    _draugai = []


def pradek_misija(vardas, klases_kodas, *, tikslas=3):
    """Užregistruoja mokinį ir parodo jo flagą."""
    global _mano_vardas, _mano_norm, _klases_kodas, _tikslas, _draugai

    if not isinstance(vardas, str) or not vardas.strip():
        print('❗ Įrašyk savo vardą kabutėse, pvz. pradek_misija("Birutė", "ZEBRAI2026").')
        return
    if not isinstance(klases_kodas, str) or not klases_kodas.strip():
        print("❗ Klasės kodas užrašytas ant lentos — įrašyk jį kabutėse.")
        return

    try:
        flagas = generuok_flaga(vardas, klases_kodas)
    except VardoKlaida:
        print(f"❗ Iš vardo „{vardas}“ flago sudaryti nepavyko — jame per mažai raidžių.")
        print("   Įrašyk vardą taip, kaip jis parašytas lentoje.")
        return

    naujas_norm = normalizuok(vardas)
    if naujas_norm != _mano_norm:
        _draugai = []

    _mano_vardas = vardas.strip()
    _mano_norm = naujas_norm
    _klases_kodas = klases_kodas
    _tikslas = tikslas

    print("🎒 Misija pradėta!")
    print(f"   Tavo flagas:     {flagas}")
    print(f"   Sakyk draugams:  {_mano_vardas}")
    print(f"   Tikslas:         {tikslas} pokalbiai")
    print("   Po kiekvieno pokalbio užpildyk ir paleisk kitą langelį.")
