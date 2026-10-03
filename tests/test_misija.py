import pytest
import re

import misija


@pytest.mark.parametrize(
    "ivestis",
    ["Birutė", "Birute", "birutė", "BIRUTĖ", "  Birutė  ", "birutė "],
)
def test_normalizuok_suvienodina_rasybos_variantus(ivestis):
    assert misija.normalizuok(ivestis) == "birute"


def test_normalizuok_nuima_visus_lietuviskus_diakritikus():
    assert misija.normalizuok("ĄČĘĖĮŠŲŪŽ ąčęėįšųūž") == "aceeisuuz aceeisuuz"


def test_normalizuok_suspaudzia_vidinius_tarpus():
    assert misija.normalizuok("  Birutė   Jonaitytė ") == "birute jonaityte"


def test_normalizuok_ne_teksta_paverciamas_tuscia_eilute():
    assert misija.normalizuok(None) == ""
    assert misija.normalizuok(17) == ""


FLAGO_FORMATAS = re.compile(r"^[A-Z]{2,4}-\d{4}$")


def test_generuok_flaga_formatas():
    assert FLAGO_FORMATAS.match(misija.generuok_flaga("Birutė", "ZEBRAI2026"))


def test_generuok_flaga_stabilus_visiems_rasybos_variantams():
    etalonas = misija.generuok_flaga("Birutė", "ZEBRAI2026")
    for variantas in ["Birute", "  birutė ", "BIRUTĖ"]:
        assert misija.generuok_flaga(variantas, "ZEBRAI2026") == etalonas


def test_generuok_flaga_skiriasi_skirtingiems_vardams():
    a = misija.generuok_flaga("Birutė", "ZEBRAI2026")
    b = misija.generuok_flaga("Tomas", "ZEBRAI2026")
    assert a != b


def test_generuok_flaga_skiriasi_skirtingiems_klases_kodams():
    a = misija.generuok_flaga("Birutė", "ZEBRAI2026")
    b = misija.generuok_flaga("Birutė", "LAPINAI2026")
    assert a != b


# Review Focus 1: pupils will type the class code inconsistently.
@pytest.mark.parametrize("kodas", ["zebrai2026", "ZEBRAI2026", " ZEBRAI2026 ", "Zebrai2026"])
def test_generuok_flaga_nepriklauso_nuo_klases_kodo_registro(kodas):
    etalonas = misija.generuok_flaga("Birutė", "ZEBRAI2026")
    assert misija.generuok_flaga("Birutė", kodas) == etalonas


def test_generuok_flaga_trumpas_vardas_meta_vardo_klaida():
    with pytest.raises(misija.VardoKlaida):
        misija.generuok_flaga("Ą", "ZEBRAI2026")
    with pytest.raises(misija.VardoKlaida):
        misija.generuok_flaga("7", "ZEBRAI2026")


def test_generuok_flaga_triju_raidziu_vardas_veikia():
    assert misija.generuok_flaga("Ema", "ZEBRAI2026").startswith("EMA-")
