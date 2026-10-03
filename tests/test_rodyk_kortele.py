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


@pytest.fixture(autouse=True)
def svari_kortele():
    kortele._atstatyk()
    yield
    kortele._atstatyk()


def _eilutes(capsys):
    return [e for e in capsys.readouterr().out.split("\n") if e]


def test_kortele_visos_eilutes_vienodo_plocio(capsys):
    kortele.rodyk_kortele("Birutė", 16, "Vilnius", "turiu du šunis")
    plociai = {kortele._plotis(e) for e in _eilutes(capsys)}
    assert len(plociai) == 1


def test_kortele_su_visais_laukais_lieka_lygi(capsys):
    kortele.rodyk_kortele(
        "Birutė", 16, "Vilnius", "turiu du šunis",
        pomegiai=["futbolas", "programavimas"],
        slapyvardis="BIR-32",
        bendri_interesai=[("Tomas", "krepšinis")],
    )
    plociai = {kortele._plotis(e) for e in _eilutes(capsys)}
    assert len(plociai) == 1


def test_kortele_labai_ilga_reiksme_nesulauzo_remelio(capsys):
    kortele.rodyk_kortele("Birutė", 16, "Vilnius", "x" * 500)
    plociai = {kortele._plotis(e) for e in _eilutes(capsys)}
    assert len(plociai) == 1


@pytest.mark.parametrize("tema", ["klasika", "matrix", "neonas"])
def test_visos_temos_atvaizduojamos(tema, capsys):
    kortele.rodyk_kortele("Birutė", 16, "Vilnius", "faktas", tema=tema)
    assert _eilutes(capsys)


def test_nezinoma_tema_duoda_zinute(capsys):
    kortele.rodyk_kortele("Birutė", 16, "Vilnius", "faktas", tema="vienaragis")
    isvestis = capsys.readouterr().out
    assert "tema" in isvestis.lower()
    assert "klasika" in isvestis


# Review Focus 5: the most common beginner mistakes.
def test_amzius_kaip_tekstas_duoda_zinute_o_ne_klaida(capsys):
    kortele.rodyk_kortele("Birutė", "16", "Vilnius", "faktas")
    assert "amzius" in capsys.readouterr().out


def test_tuscias_vardas_duoda_zinute(capsys):
    kortele.rodyk_kortele("", 16, "Vilnius", "faktas")
    assert "vardas" in capsys.readouterr().out


def test_pomegiai_ne_sarasas_duoda_zinute(capsys):
    kortele.rodyk_kortele("Birutė", 16, "Vilnius", "faktas", pomegiai="futbolas")
    assert "pomegiai" in capsys.readouterr().out


def test_bloga_ivestis_nepalieka_paskutines_korteles(capsys):
    kortele.rodyk_kortele("Birutė", "16", "Vilnius", "faktas")
    assert kortele._paskutine_kortele is None


def test_paskutine_kortele_irasoma(capsys):
    kortele.rodyk_kortele("Birutė", 16, "Vilnius", "faktas", pomegiai=["a", "b"])
    assert kortele._paskutine_kortele["vardas"] == "Birutė"
    assert kortele._paskutine_kortele["pomegiai"] == ["a", "b"]
    assert kortele._paskutine_kortele["slapyvardis"] is None


def test_bendri_interesai_paimami_is_misijos_kai_nenurodyti(capsys):
    import misija
    misija._atstatyk()
    try:
        misija.pradek_misija("Birutė", "ZEBRAI2026")
        misija.irasyk_flaga("Tomas", misija.generuok_flaga("Tomas", "ZEBRAI2026"), "krepšinis")
        capsys.readouterr()
        kortele.rodyk_kortele("Birutė", 16, "Vilnius", "faktas")
        assert "krepšinis" in capsys.readouterr().out
    finally:
        misija._atstatyk()
