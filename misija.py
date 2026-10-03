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
