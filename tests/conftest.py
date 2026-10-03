"""Bendra visų testų izoliacija.

`misija` būseną laiko modulio lygmens kintamuosiuose, tad bet kuris testas,
kuris ką nors užregistruoja, nuteka į kitus failus. Kortelės testai
(`rodyk_kortele` su `bendri_interesai=None` tingiai kviečia `misija.surinkti()`)
anksčiau rėmėsi `test_misija.py` fiksatoriumi — o tai veikė tik dėl failų
vykdymo eiliškumo. Šis autouse fiksatorius tą priklausomybę pašalina.
"""

import pytest

import misija


@pytest.fixture(autouse=True)
def svari_misijos_busena():
    misija._atstatyk()
    yield
    misija._atstatyk()
