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


# Anksčiau tikrintos tik 3 iš 8 žymeklių reikšmių: likusios galėjo nutolti nuo
# variklio ir testai to nepastebėtų. Dabar kiekvienas žymeklis privalo būti
# ir tikrai naudojamas turinyje, ir pakeistas savo variklio reikšme.
@pytest.mark.parametrize("zymeklis, reiksme", sorted(build.PAKEITIMAI.items()))
def test_kiekvienas_zymeklis_naudojamas_ir_pakeistas(nb, zymeklis, reiksme):
    from pathlib import Path
    saltiniai = "".join(f.read_text(encoding="utf-8")
                        for f in sorted(Path("turinys").iterdir()) if f.is_file())
    assert zymeklis in saltiniai, f"{zymeklis} nebenaudojamas nė viename turinys/ faile"
    # Ne per json.dumps: sąrašo literalo kabutės ten būtų kaip \" ir
    # palyginimas tyliai nebeatitiktų.
    langeliai = "".join("".join(c["source"]) for c in nb["cells"])
    assert reiksme in langeliai


def test_zymekliu_reiksmes_ateina_is_varikliu():
    p = kortele.PLACEHOLDERS
    assert build.PAKEITIMAI == {
        "@@vardas@@": p["vardas"],
        "@@amzius@@": str(p["amzius"]),
        "@@miestas@@": p["miestas"],
        "@@faktas@@": p["faktas"],
        "@@pomegiai@@": build._sarasas_literalu(p["pomegiai"]),
        "@@pavyzdys_vardas@@": misija.PAVYZDYS[0],
        "@@pavyzdys_flagas@@": misija.PAVYZDYS[1],
        "@@pavyzdys_interesas@@": misija.PAVYZDYS[2],
        "@@pavyzdys_kodas@@": misija.PLACEHOLDER_KODAS,
    }


# Kiekvienas markdown langelis turi stovėti greta SAVO kodo langelio: vien
# „markdown, code, markdown, code...“ seka praeitų ir tada, jei pora būtų
# sukeista vietomis arba suporuota su kitos sekcijos failu.
def test_kiekvienas_md_langelis_poruojamas_su_savo_kodo_langeliu(nb):
    from pathlib import Path
    vardai = [f.stem for f in sorted(Path("turinys").glob("*.md"))]
    poros = list(zip(nb["cells"][::2], nb["cells"][1::2]))
    assert len(poros) == len(vardai)
    for vardas, (md, kodas) in zip(vardai, poros):
        assert md["id"] == f"md-{vardas}"
        assert kodas["id"] == f"py-{vardas}"
        assert "".join(md["source"]) == build.pakeisk(
            Path(f"turinys/{vardas}.md").read_text(encoding="utf-8")).rstrip("\n")
        assert "".join(kodas["source"]) == build.pakeisk(
            Path(f"turinys/{vardas}.py").read_text(encoding="utf-8")).rstrip("\n")


# Notebookas yra commitintas artefaktas, o `dist/` statomas iš jo. Be šio
# testo pamirštas `build.py --tik-nb` praeitų visą paketą ir į pamoką
# nukeliautų sena turinio versija.
def test_commitintas_notebookas_sutampa_su_sugeneruotu(nb):
    from pathlib import Path
    issaugotas = json.loads(Path("intro_kortele.ipynb").read_text(encoding="utf-8"))
    assert issaugotas == nb, (
        "intro_kortele.ipynb pasenęs — paleisk `./.venv/bin/python build.py --tik-nb`"
    )


def test_irasyk_notebooka_sukuria_faila(tmp_path):
    kelias = build.irasyk_notebooka(tmp_path / "test.ipynb")
    duomenys = json.loads(kelias.read_text(encoding="utf-8"))
    assert duomenys["cells"]


# --- Kiekvienas langelis turi pats importuoti tai, ką naudoja --------------
#
# JupyterLite branduolys atsistato perkrovus puslapį, o senieji langelių
# rezultatai lieka matomi — mokiniui atrodo, kad importas jau įvykdytas.
# Jei importas būtų tik pirmame langelyje, bet kuris praleistas ar
# perkrautas seansas duotų `NameError: name 'rodyk_kortele' is not defined`.

VARIKLIO_FUNKCIJOS = {
    "rodyk_kortele": "kortele",
    "patikrink": "kortele",
    "pradek_misija": "misija",
    "irasyk_flaga": "misija",
    "misijos_bukle": "misija",
}


def _kodo_langeliai(nb):
    return [c for c in nb["cells"] if c["cell_type"] == "code"]


@pytest.mark.parametrize("funkcija,modulis", sorted(VARIKLIO_FUNKCIJOS.items()))
def test_kiekvienas_langelis_importuoja_ka_naudoja(nb, funkcija, modulis):
    for cele in _kodo_langeliai(nb):
        kodas = "".join(cele["source"])
        if f"{funkcija}(" not in kodas:
            continue
        importas = f"from {modulis} import"
        assert importas in kodas, (
            f"{cele['id']} kviečia {funkcija}(), bet neimportuoja jos. "
            f"Mokinys, paleidęs tik šį langelį, gaus NameError."
        )
        eilute = next(e for e in kodas.splitlines() if e.startswith(importas))
        assert funkcija in eilute, (
            f"{cele['id']} importuoja iš {modulis}, bet ne {funkcija}."
        )


def test_langelis_veikia_be_ankstesniu_importu(nb):
    """Pirmas kiekvieno iššūkio langelis turi veikti švariame branduolyje."""
    import pathlib
    import subprocess
    import sys

    langeliai = _kodo_langeliai(nb)
    kodas = "".join(langeliai[1]["source"])  # 1 lygis, be jokio ankstesnio langelio
    rezultatas = subprocess.run(
        [sys.executable, "-c", kodas],
        cwd=pathlib.Path(__file__).resolve().parent.parent,
        capture_output=True,
        text=True,
    )
    assert rezultatas.returncode == 0, rezultatas.stderr
    assert "NameError" not in rezultatas.stderr
