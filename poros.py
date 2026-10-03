"""Mokytojo įrankis: poros, flagų sąrašas ir projektuojama lentelė.

NIEKADA nekeliama į `dist/` ir nepublikuojama. `klase.txt` yra .gitignore.

Naudojimas:
    python poros.py klase.txt --kodas ZEBRAI2026 --raundai 3
"""

import argparse
import html
import sys
from collections import Counter
from pathlib import Path

import misija

_TUSCIA = object()


def kolizijos(vardai):
    """Vardai, kurie normalizuojasi vienodai, tad gautų tą patį flagą."""
    skaitiklis = Counter(misija.normalizuok(v) for v in vardai)
    return sorted(n for n, kiek in skaitiklis.items() if kiek > 1)


def sudaryk(vardai, raundai=3):
    """Abipusės poros per kelis raundus (apskritimo metodas)."""
    dalyviai = list(vardai)
    if len(dalyviai) < 2:
        raise ValueError("Reikia bent dviejų dalyvių.")
    if raundai > len(dalyviai) - 1:
        raise ValueError(
            f"Su {len(dalyviai)} dalyviais be pasikartojimų galima daugiausia "
            f"{len(dalyviai) - 1} raundus."
        )

    eile = dalyviai[:]
    if len(eile) % 2 == 1:
        eile.append(_TUSCIA)

    rezultatas = []
    for _ in range(raundai):
        n = len(eile)
        grupes = []
        laisvas = None
        for i in range(n // 2):
            a, b = eile[i], eile[n - 1 - i]
            if a is _TUSCIA:
                laisvas = b
            elif b is _TUSCIA:
                laisvas = a
            else:
                grupes.append((a, b))
        if laisvas is not None:
            pirma = grupes[0]
            grupes[0] = (pirma[0], pirma[1], laisvas)
        rezultatas.append(grupes)
        eile = [eile[0], eile[-1]] + eile[1:-1]
    return rezultatas


def lentele_tekstu(raundai_sarasas):
    eilutes = []
    for nr, raundas in enumerate(raundai_sarasas, start=1):
        eilutes.append(f"\n=== {nr} RAUNDAS ===")
        for grupe in raundas:
            eilutes.append("   " + "  ↔  ".join(grupe))
    return "\n".join(eilutes)


def lentele_html(raundai_sarasas, klases_kodas):
    dalys = [
        "<!DOCTYPE html>",
        '<html lang="lt"><head><meta charset="utf-8">',
        "<title>Flagų misija — poros</title>",
        "<style>body{font-family:system-ui,sans-serif;font-size:28px;margin:2rem}"
        "h1{font-size:36px}h2{margin-top:2rem}li{margin:.3rem 0}</style>",
        "</head><body>",
        f"<h1>Klasės kodas: {html.escape(klases_kodas)}</h1>",
    ]
    for nr, raundas in enumerate(raundai_sarasas, start=1):
        dalys.append(f"<h2>{nr} raundas</h2><ul>")
        for grupe in raundas:
            dalys.append("<li>" + " ↔ ".join(html.escape(v) for v in grupe) + "</li>")
        dalys.append("</ul>")
    dalys.append("</body></html>")
    return "\n".join(dalys)


def _skaityk_vardus(kelias):
    tekstas = Path(kelias).read_text(encoding="utf-8")
    return [e.strip() for e in tekstas.splitlines() if e.strip()]


def main(argv=None):
    parseris = argparse.ArgumentParser(description="Flagų misijos poros ir flagai.")
    parseris.add_argument("klase", help="failas su vardais, po vieną eilutėje")
    parseris.add_argument("--kodas", required=True, help="klasės kodas (rašomas ant lentos)")
    parseris.add_argument("--raundai", type=int, default=3)
    parseris.add_argument("--html", default="poros_lentele.html")
    args = parseris.parse_args(argv)

    # Viskas, kas gali nepavykti, patikrinama PRIEŠ pirmą spausdinimą: mokytojas,
    # pamatęs pusę teisingai atrodančios lentelės, ją suprojektuotų, o scenarijus
    # tuo metu jau būtų nutrūkęs ir poros_lentele.html liktų nesukurtas.
    try:
        vardai = _skaityk_vardus(args.klase)
    except OSError as klaida:
        print(f"❌ Nepavyko perskaityti failo „{args.klase}“: {klaida.strerror}.")
        print("   Sukurk jį ir surašyk vardus po vieną eilutėje.")
        return 1

    if len(vardai) < 2:
        print(f"❌ Faile „{args.klase}“ radau vardų: {len(vardai)}. Reikia bent dviejų.")
        print("   Surašyk klasės vardus po vieną eilutėje ir paleisk iš naujo.")
        return 1

    if args.raundai < 1:
        print(f"❌ --raundai turi būti bent 1, o nurodyta {args.raundai}.")
        return 1

    if args.raundai > len(vardai) - 1:
        print(f"❌ Su {len(vardai)} dalyviais be pasikartojimų galima daugiausia "
              f"{len(vardai) - 1} raundus, o nurodyta {args.raundai}.")
        print("   Sumažink --raundai arba papildyk klase.txt.")
        return 1

    bedos = kolizijos(vardai)
    if bedos:
        print("❌ Šie vardai sutampa po normalizavimo ir gautų tą patį flagą:")
        for vardas in bedos:
            print(f"   {vardas}")
        print("   Pataisyk klase.txt (pvz. „Lukas B.“) ir paleisk iš naujo.")
        return 1

    flagai = []
    beflagiai = []
    for vardas in sorted(vardai):
        try:
            flagai.append((vardas, misija.generuok_flaga(vardas, args.kodas)))
        except misija.VardoKlaida:
            beflagiai.append(vardas)
    if beflagiai:
        print("❌ Iš šių vardų flago sudaryti neįmanoma (per mažai lotyniškų raidžių):")
        for vardas in beflagiai:
            print(f"   {vardas}")
        print("   Pataisyk klase.txt (pvz. „Lukas B.“) ir paleisk iš naujo.")
        return 1

    raundai_sarasas = sudaryk(vardai, args.raundai)

    print(f"Klasės kodas: {args.kodas}")
    print(lentele_tekstu(raundai_sarasas))
    print("\n=== FLAGAI (tik mokytojui) ===")
    for vardas, flagas in flagai:
        print(f"   {vardas:<20} {flagas}")

    Path(args.html).write_text(lentele_html(raundai_sarasas, args.kodas), encoding="utf-8")
    print(f"\n📺 Projektuoti: {args.html}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
