import pytest

import kortele


def test_plotis_ascii():
    assert kortele._plotis("Birute") == 6


def test_plotis_lietuviski_raides_yra_vieno_plocio():
    assert kortele._plotis("Birutė") == 6
    assert kortele._plotis("ąčęėįšųūž") == 9


def test_plotis_emoji_yra_dvieju():
    assert kortele._plotis("👤") == 2


def test_plotis_ignoruoja_variacijos_selektoriu():
    assert kortele._plotis("☀️") == 2


def test_apkarpyk_palieka_trumpa_teksta_nepakeista():
    assert kortele._apkarpyk("Birutė", 20) == "Birutė"


def test_apkarpyk_sutrumpina_ilga_teksta_iki_plocio():
    rezultatas = kortele._apkarpyk("a" * 80, 10)
    assert kortele._plotis(rezultatas) <= 10
    assert rezultatas.endswith("…")


def test_eilute_visada_to_paties_plocio():
    tema = kortele._TEMOS["klasika"]
    trumpa = kortele._eilute("a", tema)
    ilga = kortele._eilute("Birutė ąčęėįšųūž", tema)
    assert kortele._plotis(trumpa) == kortele._plotis(ilga)


def test_apkarpyk_nuline_plocis_grazina_tuscia():
    assert kortele._apkarpyk("Birutė", 0) == ""


def test_apkarpyk_vieno_plocio_grazina_elipsi():
    assert kortele._apkarpyk("abc", 1) == "…"
