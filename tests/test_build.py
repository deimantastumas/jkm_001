import json

import pytest

import build
import kortele
import misija


@pytest.fixture(scope="module")
def nb():
    return build.sukurk_notebooka()


def test_notebookas_yra_galiojantis_json(nb):
    json.loads(json.dumps(nb))
    assert nb["nbformat"] == 4


def test_kiekvienas_md_turi_savo_kodo_langeli(nb):
    tipai = [c["cell_type"] for c in nb["cells"]]
    assert tipai == ["markdown", "code"] * (len(tipai) // 2)


def test_langeliu_skaicius_atitinka_turinio_failus(nb):
    from pathlib import Path
    assert len(nb["cells"]) == 2 * len(list(Path("turinys").glob("*.md")))


def test_kiekvienas_langelis_turi_unikalu_id(nb):
    idai = [c["id"] for c in nb["cells"]]
    assert len(idai) == len(set(idai))


def test_visas_kodas_kompiliuojasi(nb):
    for cele in nb["cells"]:
        if cele["cell_type"] == "code":
            kodas = "".join(cele["source"])
            compile(kodas, cele["id"], "exec")


def test_nelieka_nepakeistu_zymekliu(nb):
    visas = json.dumps(nb, ensure_ascii=False)
    assert "@@" not in visas


def test_placeholderiai_sutampa_su_variklio_reiksmemis(nb):
    visas = json.dumps(nb, ensure_ascii=False)
    assert kortele.PLACEHOLDERS["vardas"] in visas
    assert kortele.PLACEHOLDERS["faktas"] in visas
    assert misija.PAVYZDYS[1] in visas


def test_irasyk_notebooka_sukuria_faila(tmp_path):
    kelias = build.irasyk_notebooka(tmp_path / "test.ipynb")
    duomenys = json.loads(kelias.read_text(encoding="utf-8"))
    assert duomenys["cells"]
