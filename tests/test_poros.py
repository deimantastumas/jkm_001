import pytest

import poros

LYGINIS = ["Birutė", "Tomas", "Eglė", "Kazys", "Rūta", "Jonas"]
NELYGINIS = LYGINIS + ["Austėja"]


def test_kolizijos_randa_vienoda_rasyba():
    assert poros.kolizijos(["Lukas", "lukas ", "Eglė"]) == ["lukas"]


def test_kolizijos_tuscias_kai_vardai_skiriasi():
    assert poros.kolizijos(LYGINIS) == []


def test_sudaryk_niekas_nesuporuotas_su_saviimi():
    for raundas in poros.sudaryk(LYGINIS, 3):
        for grupe in raundas:
            assert len(set(grupe)) == len(grupe)


def test_sudaryk_visi_dalyvauja_kiekviename_raunde():
    for raundas in poros.sudaryk(LYGINIS, 3):
        dalyvauja = [v for grupe in raundas for v in grupe]
        assert sorted(dalyvauja) == sorted(LYGINIS)


def test_sudaryk_nelyginis_skaicius_duoda_viena_trejeta():
    for raundas in poros.sudaryk(NELYGINIS, 3):
        trejetai = [g for g in raundas if len(g) == 3]
        assert len(trejetai) == 1
        dalyvauja = [v for grupe in raundas for v in grupe]
        assert sorted(dalyvauja) == sorted(NELYGINIS)


def test_sudaryk_priskirtos_poros_nesikartoja_tarp_raundu():
    matytos = set()
    for raundas in poros.sudaryk(LYGINIS, 3):
        for grupe in raundas:
            if len(grupe) == 2:
                pora = frozenset(grupe)
                assert pora not in matytos
                matytos.add(pora)


def test_sudaryk_per_daug_raundu_meta_klaida():
    with pytest.raises(ValueError):
        poros.sudaryk(["A", "B"], 3)


def test_lentele_tekstu_turi_visus_vardus():
    tekstas = poros.lentele_tekstu(poros.sudaryk(LYGINIS, 3))
    for vardas in LYGINIS:
        assert vardas in tekstas


def test_lentele_html_turi_vardus_ir_yra_html():
    html = poros.lentele_html(poros.sudaryk(LYGINIS, 3), "ZEBRAI2026")
    assert html.lstrip().startswith("<!DOCTYPE html>")
    assert "ZEBRAI2026" in html
    for vardas in LYGINIS:
        assert vardas in html


# ---- main(): mokytojo terminalo kelias ----
#
# C1: main() anksčiau krito su traceback'u keturiais numatomais atvejais, o
# pavojingiausias — neflaguojamas vardas — atspausdindavo PILNĄ, teisingai
# atrodančią trijų raundų lentelę ir tik tada nutrūkdavo, nepalikdamas
# poros_lentele.html. Mokytojas, peržvelgęs terminalą, tokią lentelę
# suprojektuotų, ir vienas mokinys niekada neužsiregistruotų.

def _paleisk(tmp_path, vardai, *, raundai=3, kodas="ZEBRAI2026", klase=None):
    if klase is None:
        klase = tmp_path / "klase.txt"
        klase.write_text("\n".join(vardai) + "\n", encoding="utf-8")
    html = tmp_path / "poros_lentele.html"
    kodas_grazinimo = poros.main([str(klase), "--kodas", kodas,
                                  "--raundai", str(raundai), "--html", str(html)])
    return kodas_grazinimo, html


def test_main_sekmingas_kelias(tmp_path, capsys):
    kodas, html = _paleisk(tmp_path, LYGINIS)
    isvestis = capsys.readouterr().out
    assert kodas == 0
    assert html.exists()
    assert "1 RAUNDAS" in isvestis
    assert "FLAGAI (tik mokytojui)" in isvestis
    for vardas in LYGINIS:
        assert vardas in isvestis


def test_main_truksta_failo(tmp_path, capsys):
    kodas, html = _paleisk(tmp_path, [], klase=tmp_path / "nera.txt")
    isvestis = capsys.readouterr().out
    assert kodas == 1
    assert "Nepavyko perskaityti failo" in isvestis
    assert not html.exists()


def test_main_tuscias_sarasas(tmp_path, capsys):
    klase = tmp_path / "klase.txt"
    klase.write_text("\n   \n\n", encoding="utf-8")
    kodas, html = _paleisk(tmp_path, [], klase=klase)
    isvestis = capsys.readouterr().out
    assert kodas == 1
    assert "Reikia bent dviejų" in isvestis
    assert not html.exists()


def test_main_vienas_vardas(tmp_path, capsys):
    kodas, html = _paleisk(tmp_path, ["Birutė"])
    assert kodas == 1
    assert "Reikia bent dviejų" in capsys.readouterr().out
    assert not html.exists()


def test_main_per_daug_raundu(tmp_path, capsys):
    kodas, html = _paleisk(tmp_path, ["Birutė", "Tomas", "Eglė"], raundai=3)
    isvestis = capsys.readouterr().out
    assert kodas == 1
    assert "daugiausia 2 raundus" in isvestis
    assert "RAUNDAS" not in isvestis
    assert not html.exists()


def test_main_nulis_raundu(tmp_path, capsys):
    kodas, html = _paleisk(tmp_path, LYGINIS, raundai=0)
    assert kodas == 1
    assert "turi būti bent 1" in capsys.readouterr().out
    assert not html.exists()


def test_main_kolizija_neiseveda_lenteles(tmp_path, capsys):
    kodas, html = _paleisk(tmp_path, ["Lukas", "lukas ", "Eglė", "Tomas"])
    isvestis = capsys.readouterr().out
    assert kodas == 1
    assert "sutampa po normalizavimo" in isvestis
    assert "RAUNDAS" not in isvestis
    assert not html.exists()


def test_main_neflaguojamas_vardas_neiseveda_lenteles(tmp_path, capsys):
    """Pavojingiausias C1 atvejis: lentelė atrodė visiškai teisinga."""
    kodas, html = _paleisk(tmp_path, ["Birutė", "Tomas", "Eglė", "J."])
    isvestis = capsys.readouterr().out
    assert kodas == 1
    assert "flago sudaryti neįmanoma" in isvestis
    assert "J." in isvestis
    assert "Pataisyk klase.txt" in isvestis
    assert "RAUNDAS" not in isvestis
    assert "FLAGAI" not in isvestis
    assert not html.exists()


@pytest.mark.parametrize("vardai, raundai", [
    (["Birutė", "Tomas", "Eglė", "J."], 3),
    (["Birutė"], 3),
    (["Birutė", "Tomas", "Eglė"], 3),
])
def test_main_niekada_nemeta_traceback(tmp_path, vardai, raundai, capsys):
    assert _paleisk(tmp_path, vardai, raundai=raundai)[0] == 1

