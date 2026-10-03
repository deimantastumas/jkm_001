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
