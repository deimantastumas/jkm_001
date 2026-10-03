"""Surenka intro_kortele.ipynb iš turinys/ ir pastato JupyterLite svetainę.

Naudojimas:
    python build.py            # notebookas + JupyterLite į dist/
    python build.py --tik-nb   # tik notebookas
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import kortele
import misija

TURINYS = Path("turinys")
NOTEBOOKAS = Path("intro_kortele.ipynb")
BUNDLE = ["intro_kortele.ipynb", "kortele.py", "misija.py"]


def _sarasas_literalu(reiksmes):
    return "[" + ", ".join(f'"{r}"' for r in reiksmes) + "]"


def _pakeitimai():
    p = kortele.PLACEHOLDERS
    pav_vardas, pav_flagas, pav_interesas = misija.PAVYZDYS
    return {
        "@@vardas@@": p["vardas"],
        "@@amzius@@": str(p["amzius"]),
        "@@miestas@@": p["miestas"],
        "@@faktas@@": p["faktas"],
        "@@pomegiai@@": _sarasas_literalu(p["pomegiai"]),
        "@@pavyzdys_vardas@@": pav_vardas,
        "@@pavyzdys_flagas@@": pav_flagas,
        "@@pavyzdys_interesas@@": pav_interesas,
    }


PAKEITIMAI = _pakeitimai()


def pakeisk(tekstas):
    """Pakeičia @@žymeklius@@ tikromis reikšmėmis iš variklio modulių."""
    for zymeklis, reiksme in PAKEITIMAI.items():
        tekstas = tekstas.replace(zymeklis, reiksme)
    return tekstas


def _eilutes(tekstas):
    """Notebooko `source` formatas: eilutės su \\n gale, išskyrus paskutinę."""
    dalys = tekstas.rstrip("\n").split("\n")
    return [e + "\n" for e in dalys[:-1]] + [dalys[-1]]


def _md_langelis(celes_id, tekstas):
    return {"cell_type": "markdown", "id": celes_id, "metadata": {},
            "source": _eilutes(tekstas)}


def _kodo_langelis(celes_id, tekstas):
    return {"cell_type": "code", "id": celes_id, "metadata": {},
            "execution_count": None, "outputs": [], "source": _eilutes(tekstas)}


def sukurk_notebooka():
    """Surenka notebooko struktūrą iš turinys/ failų porų."""
    langeliai = []
    for md_failas in sorted(TURINYS.glob("*.md")):
        py_failas = md_failas.with_suffix(".py")
        if not py_failas.exists():
            raise FileNotFoundError(f"Trūksta kodo failo: {py_failas}")
        vardas = md_failas.stem
        langeliai.append(_md_langelis(f"md-{vardas}", pakeisk(md_failas.read_text("utf-8"))))
        langeliai.append(_kodo_langelis(f"py-{vardas}", pakeisk(py_failas.read_text("utf-8"))))

    return {
        "cells": langeliai,
        "metadata": {
            "kernelspec": {"name": "python", "display_name": "Python (Pyodide)",
                           "language": "python"},
            "language_info": {"name": "python", "file_extension": ".py",
                              "mimetype": "text/x-python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def irasyk_notebooka(kelias=NOTEBOOKAS):
    kelias = Path(kelias)
    kelias.write_text(
        json.dumps(sukurk_notebooka(), ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    return kelias


def _jupyter_vykdomasis():
    """Suranda `jupyter` šalia aktyvaus Python, nes PATH gali jo neturėti
    (pvz., kai venv neaktyvuotas, tik iškviestas per ./.venv/bin/python)."""
    kandidatas = Path(sys.executable).parent / "jupyter"
    if kandidatas.exists():
        return str(kandidatas)
    return "jupyter"


def statyk_svetaine(isvestis="dist"):
    # Patvirtinta komanda (žr. 10 užduoties 1 žingsnį): `jupyter lite build`
    # priima lygiai --contents <failas> (kartojamas) ir --output-dir <dir>,
    # patvirtinta `jupyter lite build --help` prieš jupyterlite-core 0.8.5.
    komanda = [_jupyter_vykdomasis(), "lite", "build", "--output-dir", isvestis]
    for failas in BUNDLE:
        komanda += ["--contents", failas]
    print("▶", " ".join(komanda))
    subprocess.run(komanda, check=True)


def main(argv=None):
    parseris = argparse.ArgumentParser()
    parseris.add_argument("--tik-nb", action="store_true")
    parseris.add_argument("--isvestis", default="dist")
    args = parseris.parse_args(argv)

    kelias = irasyk_notebooka()
    print(f"✅ {kelias} ({len(sukurk_notebooka()['cells'])} langeliai)")
    if not args.tik_nb:
        statyk_svetaine(args.isvestis)
        print(f"✅ {args.isvestis}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
