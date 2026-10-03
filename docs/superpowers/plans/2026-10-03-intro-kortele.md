# Lesson 001 — Kortelė + Flagų misija: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a zero-install, zero-account JupyterLite site where Lithuanian 9th–11th graders print a personal ID card in Python, then exchange derived "flags" with named classmates to force real conversations.

**Architecture:** Two stdlib-only engine modules (`kortele.py`, `misija.py`) are bundled as real files into a JupyterLite site. A generated notebook imports them, so pupils only ever write 2–6 trivial lines per level. Flags are HMAC-derived from a normalised name plus a class code, so no roster, no pupil names, and no secrets ever reach the repo or the deployed site. `build.py` assembles the notebook from markdown/starter-code pairs; GitHub Actions publishes to Pages.

**Tech Stack:** Python 3.11+ (stdlib only for engines), pytest, jupyterlite-core, jupyterlite-pyodide-kernel, GitHub Actions + GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-10-03-intro-kortele-design.md`

## Global Constraints

- **Engines are stdlib-only.** `kortele.py` and `misija.py` may import only from the Python standard library. They run under Pyodide; a third-party import breaks the lesson.
- **All pupil-facing output is Lithuanian.** Identifiers, function names and parameters are ASCII Lithuanian without diacritics (`vardas`, `pomegiai`, `slapyvardis`). Printed strings use proper Lithuanian with diacritics.
- **No pupil-facing function ever raises.** Every bad input produces a printed Lithuanian hint naming what to check. Internal helpers may raise module-private exceptions; public functions catch them.
- **No personal data in the repo or the deployed site.** `klase.txt` and `poros_*.html` are gitignored. Only `kortele.py`, `misija.py` and the notebook are bundled into `dist/`. `poros.py` is never deployed.
- **Public pupil-facing functions return `None`.** A returned value would print under the notebook cell. Tests assert against captured stdout or against private `_`-prefixed helpers that do return values.
- **Placeholder values have one source of truth.** `kortele.PLACEHOLDERS` and `misija.PAVYZDYS` are the only definitions; `build.py` substitutes them into starter cells.
- Repo root is the `001/` directory; all paths in this plan are relative to it.

## Review Focus

1. **Class code case/whitespace variance** — one pupil types `zebrai2026`, another `ZEBRAI2026 `. Both must derive identical flags for the whole class, or every exchange between them silently fails. Test in Task 1.
2. **Flag pasted with stray whitespace or wrong case** — ` biru-8271 ` must verify. Teenagers copy sloppily. Test in Task 2.
3. **`pradek_misija` re-run mid-mission** — a pupil who re-runs the setup cell must not lose collected flags. Test in Task 2.
4. **`patikrink` called before any card was rendered** — `_paskutine_kortele` is `None`; must print a hint, not crash with `TypeError`. Test in Task 5.
5. **`rodyk_kortele` given `amzius="16"` or an empty `vardas`** — the single most common beginner mistake. Must print a hint naming the parameter, not crash. Test in Task 4.

---

### Task 1: Project scaffolding + name normalisation + flag derivation

**Files:**
- Create: `requirements-dev.txt`
- Create: `misija.py`
- Create: `tests/test_misija.py`
- Modify: `.gitignore` (already contains `dist/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `klase.txt`, `poros_*.html` — verify only)

**Interfaces:**
- Consumes: nothing.
- Produces: `misija.normalizuok(vardas: str) -> str`; `misija.generuok_flaga(vardas: str, klases_kodas: str) -> str`; `misija.VardoKlaida(ValueError)`.

- [ ] **Step 1: Create `requirements-dev.txt`**

```
jupyterlite-core>=0.4
jupyterlite-pyodide-kernel>=0.4
pytest>=8
```

Then run `python -m pip install -r requirements-dev.txt` and record the resolved versions in a comment at the top of the file, so the build is reproducible:

```bash
python -m pip install -r requirements-dev.txt
python -m pip freeze | grep -iE 'jupyterlite|pytest'
```

- [ ] **Step 2: Write the failing normalisation test**

Create `tests/test_misija.py`:

```python
import pytest

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
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `python -m pytest tests/test_misija.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'misija'`

- [ ] **Step 4: Implement `normalizuok`**

Create `misija.py`:

```python
"""Flagų misija — antroji 001 pamokos užduotis.

Flagas išvedamas iš vardo ir klasės kodo, todėl niekur nereikia saugoti
mokinių sąrašo. Visos viešos funkcijos spausdina lietuviškas žinutes ir
niekada nemeta klaidų.
"""

import unicodedata


class VardoKlaida(ValueError):
    """Vidinė klaida: iš vardo neįmanoma sudaryti flago."""


def normalizuok(vardas):
    """Suvienodina vardo rašybą: be diakritikų, mažosiomis, be tarpų perteklių."""
    if not isinstance(vardas, str):
        return ""
    isskaidytas = unicodedata.normalize("NFD", vardas)
    be_kirciu = "".join(c for c in isskaidytas if not unicodedata.combining(c))
    return " ".join(be_kirciu.casefold().split())
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `python -m pytest tests/test_misija.py -v`
Expected: PASS (4 tests, the parametrised one counting as 6 cases)

- [ ] **Step 6: Write the failing flag-derivation tests**

Append to `tests/test_misija.py`:

```python
import re

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
```

- [ ] **Step 7: Run the tests to verify they fail**

Run: `python -m pytest tests/test_misija.py -v`
Expected: FAIL — `AttributeError: module 'misija' has no attribute 'generuok_flaga'`

- [ ] **Step 8: Implement `generuok_flaga`**

Add to `misija.py` (imports go at the top of the file):

```python
import hashlib
import hmac
import re

_TIK_RAIDES = re.compile(r"[^a-z]")


def _normalizuok_koda(klases_kodas):
    """Klasės kodas rašomas ant lentos, tad registras ir tarpai nesvarbūs."""
    if not isinstance(klases_kodas, str):
        return ""
    return klases_kodas.strip().upper()


def generuok_flaga(vardas, klases_kodas):
    """Grąžina flagą pavidalu RAID-1234. Meta VardoKlaida, jei vardas netinka."""
    normalizuotas = normalizuok(vardas)
    raides = _TIK_RAIDES.sub("", normalizuotas)[:4].upper()
    if len(raides) < 2:
        raise VardoKlaida(vardas)
    parasas = hmac.new(
        _normalizuok_koda(klases_kodas).encode("utf-8"),
        normalizuotas.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    skaitmenys = int.from_bytes(parasas[:4], "big") % 10000
    return f"{raides}-{skaitmenys:04d}"
```

- [ ] **Step 9: Run the tests to verify they pass**

Run: `python -m pytest tests/test_misija.py -v`
Expected: PASS, all tests

- [ ] **Step 10: Commit**

```bash
git add requirements-dev.txt misija.py tests/test_misija.py .gitignore
git commit -m "feat: name normalisation and HMAC flag derivation"
```

---

### Task 2: Mission state — register, record, report

**Files:**
- Modify: `misija.py`
- Modify: `tests/test_misija.py`

**Interfaces:**
- Consumes: `misija.normalizuok`, `misija.generuok_flaga`, `misija.VardoKlaida` (Task 1).
- Produces:
  - `misija.PAVYZDYS: tuple[str, str, str]` — the starter cell's example triple `("Vardenis", "VARD-0000", "krepšinis")`.
  - `misija.pradek_misija(vardas: str, klases_kodas: str, *, tikslas: int = 3) -> None`
  - `misija.irasyk_flaga(vardas: str, flagas: str, bendras_interesas: str) -> None`
  - `misija.misijos_bukle() -> None`
  - `misija.surinkti() -> list[tuple[str, str]]` — `[(display name, shared interest)]` in insertion order.
  - `misija._atstatyk() -> None` — test-only state reset.

The example name is `Vardenis` (the Lithuanian "John Doe") rather than a plausible first name, so a real classmate can never be mistaken for the starter placeholder.

- [ ] **Step 1: Write the failing registration tests**

Append to `tests/test_misija.py`:

```python
@pytest.fixture(autouse=True)
def svari_misija():
    misija._atstatyk()
    yield
    misija._atstatyk()


def test_pradek_misija_parodo_flaga_ir_vardo_rasyba(capsys):
    misija.pradek_misija("Birutė", "ZEBRAI2026")
    isvestis = capsys.readouterr().out
    assert misija.generuok_flaga("Birutė", "ZEBRAI2026") in isvestis
    assert "Birutė" in isvestis


def test_pradek_misija_su_netinkamu_vardu_nemeta_klaidos(capsys):
    misija.pradek_misija("Ą", "ZEBRAI2026")
    assert "vard" in capsys.readouterr().out.lower()


# Review Focus 3: re-running the setup cell must not wipe progress.
def test_pradek_misija_pakartotinai_tuo_paciu_vardu_islaiko_surinktus():
    misija.pradek_misija("Birutė", "ZEBRAI2026")
    tomo_flagas = misija.generuok_flaga("Tomas", "ZEBRAI2026")
    misija.irasyk_flaga("Tomas", tomo_flagas, "krepšinis")
    misija.pradek_misija("Birutė", "ZEBRAI2026")
    assert misija.surinkti() == [("Tomas", "krepšinis")]


def test_pradek_misija_kitu_vardu_pradeda_is_naujo():
    misija.pradek_misija("Birutė", "ZEBRAI2026")
    misija.irasyk_flaga("Tomas", misija.generuok_flaga("Tomas", "ZEBRAI2026"), "krepšinis")
    misija.pradek_misija("Eglė", "ZEBRAI2026")
    assert misija.surinkti() == []
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_misija.py -v`
Expected: FAIL — `AttributeError: module 'misija' has no attribute '_atstatyk'`

- [ ] **Step 3: Implement registration state**

Add to `misija.py`:

```python
PAVYZDYS = ("Vardenis", "VARD-0000", "krepšinis")

_mano_vardas = None
_mano_norm = None
_klases_kodas = None
_tikslas = 3
_draugai = []


def _atstatyk():
    """Tik testams: išvalo misijos būseną."""
    global _mano_vardas, _mano_norm, _klases_kodas, _tikslas, _draugai
    _mano_vardas = None
    _mano_norm = None
    _klases_kodas = None
    _tikslas = 3
    _draugai = []


def pradek_misija(vardas, klases_kodas, *, tikslas=3):
    """Užregistruoja mokinį ir parodo jo flagą."""
    global _mano_vardas, _mano_norm, _klases_kodas, _tikslas, _draugai

    if not isinstance(vardas, str) or not vardas.strip():
        print('❗ Įrašyk savo vardą kabutėse, pvz. pradek_misija("Birutė", "ZEBRAI2026").')
        return
    if not isinstance(klases_kodas, str) or not klases_kodas.strip():
        print("❗ Klasės kodas užrašytas ant lentos — įrašyk jį kabutėse.")
        return

    try:
        flagas = generuok_flaga(vardas, klases_kodas)
    except VardoKlaida:
        print(f"❗ Iš vardo „{vardas}“ flago sudaryti nepavyko — jame per mažai raidžių.")
        print("   Įrašyk vardą taip, kaip jis parašytas lentoje.")
        return

    naujas_norm = normalizuok(vardas)
    if naujas_norm != _mano_norm:
        _draugai = []

    _mano_vardas = vardas.strip()
    _mano_norm = naujas_norm
    _klases_kodas = klases_kodas
    _tikslas = tikslas

    print("🎒 Misija pradėta!")
    print(f"   Tavo flagas:     {flagas}")
    print(f"   Sakyk draugams:  {_mano_vardas}")
    print(f"   Tikslas:         {tikslas} pokalbiai")
    print("   Po kiekvieno pokalbio užpildyk ir paleisk kitą langelį.")
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_misija.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add misija.py tests/test_misija.py
git commit -m "feat: mission registration state"
```

- [ ] **Step 6: Write the failing exchange tests**

Append to `tests/test_misija.py`:

```python
def _pradek():
    misija.pradek_misija("Birutė", "ZEBRAI2026")


def test_irasyk_flaga_teisingas_irasomas(capsys):
    _pradek()
    misija.irasyk_flaga("Tomas", misija.generuok_flaga("Tomas", "ZEBRAI2026"), "krepšinis")
    assert misija.surinkti() == [("Tomas", "krepšinis")]
    assert "✅" in capsys.readouterr().out


# Review Focus 2: flags get copied sloppily.
@pytest.mark.parametrize("apdaila", ["{}", " {} ", "{}\n", "@lower@"])
def test_irasyk_flaga_atlaidus_tarpams_ir_registrui(apdaila):
    _pradek()
    flagas = misija.generuok_flaga("Tomas", "ZEBRAI2026")
    ivestis = flagas.lower() if apdaila == "@lower@" else apdaila.format(flagas)
    misija.irasyk_flaga("Tomas", ivestis, "krepšinis")
    assert misija.surinkti() == [("Tomas", "krepšinis")]


def test_irasyk_flaga_pavyzdys_nera_klaida(capsys):
    _pradek()
    misija.irasyk_flaga(*misija.PAVYZDYS)
    assert misija.surinkti() == []
    assert "pavyzdys" in capsys.readouterr().out.lower()


def test_irasyk_flaga_atmeta_savo_varda(capsys):
    _pradek()
    misija.irasyk_flaga("Birutė", misija.generuok_flaga("Birutė", "ZEBRAI2026"), "aš pats")
    assert misija.surinkti() == []
    assert "sav" in capsys.readouterr().out.lower()


def test_irasyk_flaga_atmeta_pakartotina_varda(capsys):
    _pradek()
    flagas = misija.generuok_flaga("Tomas", "ZEBRAI2026")
    misija.irasyk_flaga("Tomas", flagas, "krepšinis")
    capsys.readouterr()
    misija.irasyk_flaga("tomas ", flagas, "kas nors kita")
    assert len(misija.surinkti()) == 1
    assert "jau" in capsys.readouterr().out.lower()


def test_irasyk_flaga_atmeta_neteisinga_flaga(capsys):
    _pradek()
    misija.irasyk_flaga("Tomas", "TOMA-0001", "krepšinis")
    assert misija.surinkti() == []
    assert "flag" in capsys.readouterr().out.lower()


def test_irasyk_flaga_pries_pradek_misija_yra_zinute(capsys):
    misija.irasyk_flaga("Tomas", "TOMA-0001", "krepšinis")
    assert "pradek_misija" in capsys.readouterr().out


def test_irasyk_flaga_reikalauja_bendro_intereso(capsys):
    _pradek()
    misija.irasyk_flaga("Tomas", misija.generuok_flaga("Tomas", "ZEBRAI2026"), "")
    assert misija.surinkti() == []
    assert "interes" in capsys.readouterr().out.lower()


def test_surinkti_islaiko_rasyba_ir_eiliskuma():
    _pradek()
    for vardas, interesas in [("Tomas", "krepšinis"), ("Eglė", "šunys")]:
        misija.irasyk_flaga(vardas, misija.generuok_flaga(vardas, "ZEBRAI2026"), interesas)
    assert misija.surinkti() == [("Tomas", "krepšinis"), ("Eglė", "šunys")]


def test_misijos_bukle_rodo_progresa(capsys):
    _pradek()
    misija.irasyk_flaga("Tomas", misija.generuok_flaga("Tomas", "ZEBRAI2026"), "krepšinis")
    capsys.readouterr()
    misija.misijos_bukle()
    isvestis = capsys.readouterr().out
    assert "1/3" in isvestis
    assert "Tomas" in isvestis
```

- [ ] **Step 7: Run the tests to verify they fail**

Run: `python -m pytest tests/test_misija.py -v`
Expected: FAIL — `AttributeError: module 'misija' has no attribute 'irasyk_flaga'`

- [ ] **Step 8: Implement the exchange**

Add to `misija.py`:

```python
def irasyk_flaga(vardas, flagas, bendras_interesas):
    """Patikrina draugo flagą ir įrašo jūsų bendrą interesą."""
    if _mano_norm is None:
        print("❗ Pirmiausia paleisk langelį su pradek_misija(...).")
        return

    if not isinstance(vardas, str) or not isinstance(flagas, str):
        print('❗ Vardas ir flagas rašomi kabutėse, pvz. irasyk_flaga("Tomas", "TOMA-4417", "krepšinis").')
        return

    pavyzdinis_vardas, pavyzdinis_flagas, _ = PAVYZDYS
    if (normalizuok(vardas) == normalizuok(pavyzdinis_vardas)
            and flagas.strip().upper() == pavyzdinis_flagas):
        print("👀 Čia pavyzdys — įrašyk tikro draugo vardą, jo flagą ir jūsų bendrą interesą.")
        return

    if not isinstance(bendras_interesas, str) or not bendras_interesas.strip():
        print("❗ Įrašyk, ką radote bendro — be to flagas neužskaitomas.")
        return

    svetimas_norm = normalizuok(vardas)
    if svetimas_norm == _mano_norm:
        print("🙃 Savo paties flago įrašyti negalima. Eik pas tą žmogų, kuris nurodytas lentoje.")
        return

    if any(d["norm"] == svetimas_norm for d in _draugai):
        print(f"ℹ️ Su {vardas} jau apsikeitėte. Eik pas kitą!")
        return

    try:
        laukiamas = generuok_flaga(vardas, _klases_kodas)
    except VardoKlaida:
        print(f"❗ Iš vardo „{vardas}“ flago sudaryti nepavyko. Patikrink rašybą.")
        return

    if flagas.strip().upper() != laukiamas:
        print(f"❌ Flagas netinka. Patikrink: ar gerai nurašei vardą „{vardas}“ ir jo flagą?")
        print(f"   Jo flagas turėtų prasidėti „{laukiamas.split('-')[0]}-“.")
        return

    _draugai.append({
        "vardas": vardas.strip(),
        "norm": svetimas_norm,
        "interesas": bendras_interesas.strip(),
    })
    print(f"✅ {vardas.strip()} — {bendras_interesas.strip()}")
    misijos_bukle()


def surinkti():
    """Grąžina [(vardas, bendras interesas), ...] įrašymo tvarka."""
    return [(d["vardas"], d["interesas"]) for d in _draugai]


def misijos_bukle():
    """Parodo, kiek pokalbių jau įskaityta."""
    if _mano_norm is None:
        print("❗ Pirmiausia paleisk langelį su pradek_misija(...).")
        return
    print(f"📋 Misijos būklė: {len(_draugai)}/{_tikslas}")
    for draugas in _draugai:
        print(f"   ✅ {draugas['vardas']} – {draugas['interesas']}")
    truksta = _tikslas - len(_draugai)
    if truksta > 0:
        print(f"   Liko pokalbių: {truksta}")
    else:
        print("   🎉 Misija įvykdyta!")
```

- [ ] **Step 9: Run the tests to verify they pass**

Run: `python -m pytest tests/test_misija.py -v`
Expected: PASS, all tests

- [ ] **Step 10: Commit**

```bash
git add misija.py tests/test_misija.py
git commit -m "feat: flag exchange with placeholder, duplicate and mismatch handling"
```

---

### Task 3: Card rendering primitives — display width, truncation, borders

**Files:**
- Create: `kortele.py`
- Create: `tests/test_rodyk_kortele.py`

**Interfaces:**
- Consumes: nothing.
- Produces (all module-private, used only by Task 4 and tests):
  - `kortele._plotis(tekstas: str) -> int`
  - `kortele._apkarpyk(tekstas: str, max_plotis: int) -> str`
  - `kortele._TEMOS: dict[str, dict[str, str]]` — keys `"klasika"`, `"matrix"`, `"neonas"`; each value has keys `vk`, `vd`, `ak`, `ad`, `h`, `v`, `sk`, `sd` (viršus kairė/dešinė, apačia kairė/dešinė, horizontali, vertikali, skirtukas kairė/dešinė).
  - `kortele._VIDUS = 46` — interior width in columns.
  - `kortele._eilute(turinys: str, tema: dict) -> str`

- [ ] **Step 1: Write the failing width and truncation tests**

Create `tests/test_rodyk_kortele.py`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_rodyk_kortele.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'kortele'`

- [ ] **Step 3: Implement the primitives**

Create `kortele.py`:

```python
"""Prisistatymo kortelė — pirmoji 001 pamokos užduotis.

Visos viešos funkcijos spausdina lietuviškas žinutes ir niekada nemeta klaidų.
"""

import unicodedata

_VIDUS = 46
_NULINIO_PLOCIO = {"\uFE0E", "\uFE0F", "\u200D"}

_EMOJI_REZIAI = (
    (0x1F300, 0x1FAFF),
    (0x1F000, 0x1F2FF),
    (0x2600, 0x27BF),
)

_TEMOS = {
    "klasika": {"vk": "╔", "vd": "╗", "ak": "╚", "ad": "╝",
                "h": "═", "v": "║", "sk": "╠", "sd": "╣"},
    "matrix":  {"vk": "+", "vd": "+", "ak": "+", "ad": "+",
                "h": "-", "v": "|", "sk": "+", "sd": "+"},
    "neonas":  {"vk": "┏", "vd": "┓", "ak": "┗", "ad": "┛",
                "h": "━", "v": "┃", "sk": "┣", "sd": "┫"},
}


def _yra_emoji(simbolis):
    kodas = ord(simbolis)
    return any(pradzia <= kodas <= pabaiga for pradzia, pabaiga in _EMOJI_REZIAI)


def _plotis(tekstas):
    """Kiek stulpelių užima tekstas monospace šrifte."""
    suma = 0
    for simbolis in tekstas:
        if unicodedata.combining(simbolis) or simbolis in _NULINIO_PLOCIO:
            continue
        if unicodedata.east_asian_width(simbolis) in ("W", "F") or _yra_emoji(simbolis):
            suma += 2
        else:
            suma += 1
    return suma


def _apkarpyk(tekstas, max_plotis):
    """Sutrumpina tekstą, kad kortelės rėmelis nesulūžtų."""
    if _plotis(tekstas) <= max_plotis:
        return tekstas
    surinkta = ""
    for simbolis in tekstas:
        if _plotis(surinkta + simbolis) > max_plotis - 1:
            break
        surinkta += simbolis
    return surinkta + "…"


def _eilute(turinys, tema):
    """Viena kortelės eilutė su rėmeliu iš abiejų pusių."""
    apkarpyta = _apkarpyk(turinys, _VIDUS)
    uzpildas = " " * (_VIDUS - _plotis(apkarpyta))
    return f"{tema['v']}{apkarpyta}{uzpildas}{tema['v']}"
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_rodyk_kortele.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add kortele.py tests/test_rodyk_kortele.py
git commit -m "feat: card rendering primitives with display-width handling"
```

---

### Task 4: `rodyk_kortele` — the public card API

**Files:**
- Modify: `kortele.py`
- Modify: `tests/test_rodyk_kortele.py`

**Interfaces:**
- Consumes: `kortele._plotis`, `_apkarpyk`, `_eilute`, `_TEMOS`, `_VIDUS` (Task 3); `misija.surinkti` (Task 2), imported lazily inside the function body.
- Produces:
  - `kortele.PLACEHOLDERS: dict` with keys `vardas`, `amzius`, `miestas`, `faktas`, `pomegiai`.
  - `kortele.rodyk_kortele(vardas, amzius, miestas, faktas, *, pomegiai=None, slapyvardis=None, tema="klasika", bendri_interesai=None) -> None`
  - `kortele._paskutine_kortele: dict | None` — the keyword-normalised arguments of the most recent successful render.
  - `kortele._atstatyk() -> None` — test-only reset of `_paskutine_kortele`.

- [ ] **Step 1: Write the failing render tests**

Append to `tests/test_rodyk_kortele.py`:

```python
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
    misija.pradek_misija("Birutė", "ZEBRAI2026")
    misija.irasyk_flaga("Tomas", misija.generuok_flaga("Tomas", "ZEBRAI2026"), "krepšinis")
    capsys.readouterr()
    kortele.rodyk_kortele("Birutė", 16, "Vilnius", "faktas")
    assert "krepšinis" in capsys.readouterr().out
    misija._atstatyk()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_rodyk_kortele.py -v`
Expected: FAIL — `AttributeError: module 'kortele' has no attribute '_atstatyk'`

- [ ] **Step 3: Implement `rodyk_kortele`**

Add to `kortele.py`:

```python
PLACEHOLDERS = {
    "vardas": "Jonas",
    "amzius": 16,
    "miestas": "Vilnius",
    "faktas": "moku groti gitara",
    "pomegiai": ["futbolas", "programavimas", "šunys"],
}

_paskutine_kortele = None


def _atstatyk():
    """Tik testams: pamiršta paskutinę atvaizduotą kortelę."""
    global _paskutine_kortele
    _paskutine_kortele = None


def _patikrink_ivesti(vardas, amzius, miestas, faktas, pomegiai, slapyvardis, tema):
    """Grąžina lietuvišką žinutę apie pirmą rastą klaidą arba None."""
    for pavadinimas, reiksme in (("vardas", vardas), ("miestas", miestas), ("faktas", faktas)):
        if not isinstance(reiksme, str) or not reiksme.strip():
            return (f'❗ `{pavadinimas}` turi būti tekstas kabutėse, pvz. '
                    f'{pavadinimas} = "Birutė".')
    if isinstance(amzius, bool) or not isinstance(amzius, int):
        return "❗ `amzius` turi būti skaičius be kabučių, pvz. amzius = 16."
    if pomegiai is not None and not isinstance(pomegiai, list):
        return ('❗ `pomegiai` turi būti sąrašas laužtiniuose skliaustuose, pvz. '
                'pomegiai = ["futbolas", "šunys"].')
    if slapyvardis is not None and not isinstance(slapyvardis, str):
        return '❗ `slapyvardis` turi būti tekstas kabutėse.'
    if tema not in _TEMOS:
        return f"❗ Tokios temos nėra: „{tema}“. Galimos: " + ", ".join(_TEMOS) + "."
    return None


def _gauk_bendrus_interesus(bendri_interesai):
    if bendri_interesai is not None:
        return bendri_interesai
    try:
        import misija
    except ImportError:
        return []
    return misija.surinkti()


def rodyk_kortele(vardas, amzius, miestas, faktas, *, pomegiai=None,
                  slapyvardis=None, tema="klasika", bendri_interesai=None):
    """Atspausdina asmeninę kortelę."""
    global _paskutine_kortele

    klaida = _patikrink_ivesti(vardas, amzius, miestas, faktas, pomegiai, slapyvardis, tema)
    if klaida:
        print(klaida)
        return

    t = _TEMOS[tema]
    virsus = t["vk"] + t["h"] * _VIDUS + t["vd"]
    skirtukas = t["sk"] + t["h"] * _VIDUS + t["sd"]
    apacia = t["ak"] + t["h"] * _VIDUS + t["ad"]

    eilutes = [virsus]
    eilutes.append(_eilute(f"  👤  {vardas.upper()}", t))
    eilutes.append(_eilute(f"      {amzius} m. · {miestas}", t))
    eilutes.append(skirtukas)
    eilutes.append(_eilute("  Apie mane:", t))
    eilutes.append(_eilute(f"    {faktas}", t))

    if pomegiai:
        eilutes.append(_eilute("  Pomėgiai:", t))
        for pomegis in pomegiai:
            eilutes.append(_eilute(f"    • {pomegis}", t))

    if slapyvardis:
        eilutes.append(_eilute(f"  Slapyvardis:  {slapyvardis}", t))

    interesai = _gauk_bendrus_interesus(bendri_interesai)
    if interesai:
        eilutes.append(skirtukas)
        eilutes.append(_eilute("  Bendri interesai:", t))
        for draugas, interesas in interesai:
            eilutes.append(_eilute(f"    su {draugas} – {interesas}", t))

    eilutes.append(apacia)
    print("\n".join(eilutes))

    _paskutine_kortele = {
        "vardas": vardas, "amzius": amzius, "miestas": miestas, "faktas": faktas,
        "pomegiai": pomegiai, "slapyvardis": slapyvardis, "tema": tema,
    }
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_rodyk_kortele.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add kortele.py tests/test_rodyk_kortele.py
git commit -m "feat: rodyk_kortele with themes, validation and mission fallback"
```

---

### Task 5: `patikrink` — the per-level self-checks

**Files:**
- Modify: `kortele.py`
- Create: `tests/test_patikrink.py`

**Interfaces:**
- Consumes: `kortele.PLACEHOLDERS`, `kortele._paskutine_kortele` (Task 4).
- Produces:
  - `kortele._ivertink(lygis: int, erdve: dict) -> tuple[bool, list[str]]` — `(passed, lines to print)`. Tests use this; it is the only check helper that returns a value.
  - `kortele.patikrink(lygis: int, *, erdve: dict | None = None) -> None` — prints the lines, returns nothing.

- [ ] **Step 1: Write the failing check tests**

Create `tests/test_patikrink.py`:

```python
import pytest

import kortele


@pytest.fixture(autouse=True)
def svari_kortele():
    kortele._atstatyk()
    yield
    kortele._atstatyk()


def _erdve_1(**pakeitimai):
    erdve = {
        "vardas": "Birutė", "amzius": 16,
        "miestas": "Kaunas", "faktas": "turiu du šunis",
    }
    erdve.update(pakeitimai)
    return erdve


def _atvaizduok(erdve, **papildomai):
    kortele.rodyk_kortele(
        erdve["vardas"], erdve["amzius"], erdve["miestas"], erdve["faktas"], **papildomai
    )


# ---- Lygis 1 ----

def test_lygis1_praeina(capsys):
    erdve = _erdve_1()
    _atvaizduok(erdve)
    assert kortele._ivertink(1, erdve)[0] is True


def test_lygis1_su_nepakeistais_placeholderiais_nepraeina(capsys):
    erdve = _erdve_1(**{k: v for k, v in kortele.PLACEHOLDERS.items() if k != "pomegiai"})
    _atvaizduok(erdve)
    praejo, eilutes = kortele._ivertink(1, erdve)
    assert praejo is False
    assert any("✋" in e for e in eilutes)


def test_lygis1_truksta_kintamojo(capsys):
    erdve = _erdve_1()
    _atvaizduok(erdve)
    del erdve["miestas"]
    praejo, eilutes = kortele._ivertink(1, erdve)
    assert praejo is False
    assert any("miestas" in e for e in eilutes)


def test_lygis1_blogas_tipas(capsys):
    erdve = _erdve_1(amzius="16")
    praejo, eilutes = kortele._ivertink(1, erdve)
    assert praejo is False
    assert any("amzius" in e for e in eilutes)


# Review Focus 4: nothing rendered yet.
def test_lygis1_be_atvaizduotos_korteles_nepraeina_ir_nelunka():
    praejo, eilutes = kortele._ivertink(1, _erdve_1())
    assert praejo is False
    assert any("rodyk_kortele" in e for e in eilutes)


def test_patikrink_be_atvaizduotos_korteles_nelunka(capsys):
    kortele.patikrink(1, erdve=_erdve_1())
    assert capsys.readouterr().out


# ---- Lygis 2 ----

def test_lygis2_praeina(capsys):
    erdve = _erdve_1(pomegiai=["futbolas", "šunys"])
    _atvaizduok(erdve, pomegiai=erdve["pomegiai"])
    assert kortele._ivertink(2, erdve)[0] is True


def test_lygis2_apibreztas_bet_neperduotas_nepraeina(capsys):
    erdve = _erdve_1(pomegiai=["futbolas", "šunys"])
    _atvaizduok(erdve)
    praejo, eilutes = kortele._ivertink(2, erdve)
    assert praejo is False
    assert any("rodyk_kortele" in e for e in eilutes)


def test_lygis2_per_mazai_pomegiu(capsys):
    erdve = _erdve_1(pomegiai=["futbolas"])
    _atvaizduok(erdve, pomegiai=erdve["pomegiai"])
    assert kortele._ivertink(2, erdve)[0] is False


def test_lygis2_ne_sarasas(capsys):
    erdve = _erdve_1(pomegiai="futbolas")
    assert kortele._ivertink(2, erdve)[0] is False


# ---- Lygis 3 ----

def test_lygis3_praeina(capsys):
    erdve = _erdve_1(pomegiai=["futbolas", "šunys"], slapyvardis="BIR-32")
    _atvaizduok(erdve, pomegiai=erdve["pomegiai"], slapyvardis=erdve["slapyvardis"])
    assert kortele._ivertink(3, erdve)[0] is True


def test_lygis3_slapyvardis_lygus_vardui_nepraeina(capsys):
    erdve = _erdve_1(pomegiai=["futbolas", "šunys"], slapyvardis="Birutė")
    _atvaizduok(erdve, pomegiai=erdve["pomegiai"], slapyvardis=erdve["slapyvardis"])
    assert kortele._ivertink(3, erdve)[0] is False


def test_lygis3_apibreztas_bet_neperduotas_nepraeina(capsys):
    erdve = _erdve_1(pomegiai=["futbolas", "šunys"], slapyvardis="BIR-32")
    _atvaizduok(erdve, pomegiai=erdve["pomegiai"])
    assert kortele._ivertink(3, erdve)[0] is False


# ---- Lygis 4 ----

@pytest.mark.parametrize("erdve", [
    {},
    {"slapyvardis_is": lambda v, a: f"{v[:3].upper()}-{a}"},
    {"slapyvardis_is": lambda v, a: "VISADA_TAS_PATS"},
    {"slapyvardis_is": "ne funkcija"},
    {"random": __import__("random")},
])
def test_lygis4_niekada_nepranesa_klaidos(erdve):
    praejo, eilutes = kortele._ivertink(4, dict(erdve))
    assert praejo is True
    assert eilutes


def test_lygis4_atpazista_veikiancia_funkcija():
    erdve = {"slapyvardis_is": lambda v, a: f"{v[:3].upper()}-{a}"}
    _, eilutes = kortele._ivertink(4, erdve)
    assert any("slapyvardis_is" in e for e in eilutes)


def test_lygis4_atpazista_pakeista_tema():
    kortele.rodyk_kortele("Birutė", 16, "Kaunas", "faktas", tema="matrix")
    _, eilutes = kortele._ivertink(4, {})
    assert any("matrix" in e for e in eilutes)


# ---- Bendra ----

def test_nezinomas_lygis_duoda_zinute():
    praejo, eilutes = kortele._ivertink(99, {})
    assert praejo is False
    assert eilutes


def test_patikrink_nieko_negrazina(capsys):
    erdve = _erdve_1()
    _atvaizduok(erdve)
    assert kortele.patikrink(1, erdve=erdve) is None
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_patikrink.py -v`
Expected: FAIL — `AttributeError: module 'kortele' has no attribute '_ivertink'`

- [ ] **Step 3: Implement the checks**

Add to `kortele.py` (`import sys` goes at the top of the file):

```python
import sys


def _truksta_arba_blogas_tipas(erdve, pavadinimas, tipas, aprasas):
    if pavadinimas not in erdve:
        return f"❌ Nerandu kintamojo `{pavadinimas}`. Ar paleidai langelį?"
    reiksme = erdve[pavadinimas]
    if isinstance(reiksme, bool) or not isinstance(reiksme, tipas):
        return f"❌ `{pavadinimas}` turi būti {aprasas}."
    if isinstance(reiksme, str) and not reiksme.strip():
        return f"❌ `{pavadinimas}` tuščias — įrašyk savo duomenis."
    return None


def _ivertink_1(erdve):
    eilutes = []
    laukai = (
        ("vardas", str, 'tekstas kabutėse, pvz. "Birutė"'),
        ("miestas", str, 'tekstas kabutėse, pvz. "Kaunas"'),
        ("faktas", str, "tekstas kabutėse"),
        ("amzius", int, "skaičius be kabučių, pvz. 16"),
    )
    for pavadinimas, tipas, aprasas in laukai:
        klaida = _truksta_arba_blogas_tipas(erdve, pavadinimas, tipas, aprasas)
        if klaida:
            return False, [klaida]

    nepakeisti = [p for p in ("vardas", "amzius", "miestas", "faktas")
                  if erdve[p] == PLACEHOLDERS[p]]
    if nepakeisti:
        eilutes.append("✋ Kortelė veikia! Dabar įrašyk savo duomenis 🙂")
        eilutes.append("   Dar nepakeisti: " + ", ".join(f"`{p}`" for p in nepakeisti))
        return False, eilutes

    if _paskutine_kortele is None:
        return False, ["❌ Dar neatvaizdavai kortelės — paleisk `rodyk_kortele(...)` eilutę."]

    return True, ["✅ 1 lygis įveiktas! Tavo kortelė pasiruošusi."]


def _ivertink_2(erdve):
    praejo, eilutes = _ivertink_1(erdve)
    if not praejo:
        return False, eilutes

    if "pomegiai" not in erdve:
        return False, ["❌ Nerandu kintamojo `pomegiai`."]
    pomegiai = erdve["pomegiai"]
    if not isinstance(pomegiai, list):
        return False, ['❌ `pomegiai` turi būti sąrašas, pvz. ["futbolas", "šunys"].']
    tinkami = [p for p in pomegiai if isinstance(p, str) and p.strip()]
    if len(tinkami) < 2:
        return False, ["❌ Įrašyk bent du pomėgius į sąrašą."]
    if pomegiai == PLACEHOLDERS["pomegiai"]:
        return False, ["✋ Čia dar Jono pomėgiai — įrašyk savo."]
    if _paskutine_kortele is None or _paskutine_kortele.get("pomegiai") != pomegiai:
        return False, ["❌ `pomegiai` jau yra, bet dar neperduoti kortelei.",
                       "   Pridėk `pomegiai=pomegiai` į `rodyk_kortele(...)`."]

    return True, ["✅ 2 lygis įveiktas! Pomėgiai jau kortelėje."]


def _ivertink_3(erdve):
    praejo, eilutes = _ivertink_2(erdve)
    if not praejo:
        return False, eilutes

    if "slapyvardis" not in erdve:
        return False, ["❌ Nerandu kintamojo `slapyvardis`."]
    slapyvardis = erdve["slapyvardis"]
    if not isinstance(slapyvardis, str) or not slapyvardis.strip():
        return False, ["❌ `slapyvardis` turi būti netuščias tekstas."]
    if slapyvardis == erdve["vardas"]:
        return False, ["❌ Slapyvardis toks pat kaip vardas — apskaičiuok jį iš vardo."]
    if _paskutine_kortele is None or _paskutine_kortele.get("slapyvardis") != slapyvardis:
        return False, ["❌ `slapyvardis` jau yra, bet dar neperduotas kortelei.",
                       "   Pridėk `slapyvardis=slapyvardis` į `rodyk_kortele(...)`."]

    return True, ["✅ 3 lygis įveiktas! Palygink slapyvardį su kaimynu."]


def _ivertink_4(erdve):
    eilutes = ["🚀 4 lygis — laisvas režimas. Štai ką radau:"]

    funkcija = erdve.get("slapyvardis_is")
    if callable(funkcija):
        try:
            a = funkcija("Testas", 15)
            b = funkcija("Kitas", 17)
        except Exception:
            eilutes.append("   ⚠️ `slapyvardis_is` yra, bet su mano duomenimis nesuveikė.")
        else:
            if isinstance(a, str) and isinstance(b, str) and a.strip() and a != b:
                eilutes.append(f"   ✅ `slapyvardis_is` veikia: Testas → {a}, Kitas → {b}")
            else:
                eilutes.append("   ⚠️ `slapyvardis_is` grąžina tą patį visiems — pasinaudok argumentais.")
    elif funkcija is not None:
        eilutes.append("   ⚠️ `slapyvardis_is` yra, bet tai ne funkcija.")

    if "random" in erdve:
        eilutes.append("   ✅ Naudoji `random` — atsitiktinumas įjungtas.")

    if _paskutine_kortele and _paskutine_kortele.get("tema") != "klasika":
        eilutes.append(f"   ✅ Radai slaptą temą: {_paskutine_kortele['tema']}")

    if len(eilutes) == 1:
        eilutes.append("   Dar nieko — pasirink a), b) arba c) ir bandyk!")
    eilutes.append("   Čia teisingo atsakymo nėra. Daryk, kas įdomu.")
    return True, eilutes


_VERTINTOJAI = {1: _ivertink_1, 2: _ivertink_2, 3: _ivertink_3, 4: _ivertink_4}


def _ivertink(lygis, erdve):
    """Grąžina (ar praėjo, eilučių sąrašas). Tik vidiniam naudojimui ir testams."""
    vertintojas = _VERTINTOJAI.get(lygis)
    if vertintojas is None:
        return False, [f"❓ Tokio lygio nėra: {lygis}. Galimi: 1, 2, 3, 4."]
    return vertintojas(erdve)


def patikrink(lygis, *, erdve=None):
    """Patikrina, ar lygis įveiktas, ir paaiškina, ko trūksta."""
    if erdve is None:
        erdve = sys._getframe(1).f_globals
    _, eilutes = _ivertink(lygis, erdve)
    for eilute in eilutes:
        print(eilute)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_patikrink.py -v`
Expected: PASS

- [ ] **Step 5: Run the whole suite**

Run: `python -m pytest -v`
Expected: PASS, all tests from Tasks 1–5

- [ ] **Step 6: Commit**

```bash
git add kortele.py tests/test_patikrink.py
git commit -m "feat: per-level patikrink self-checks"
```

---

### Task 6: Reference solutions and the drift-catching test

**Files:**
- Create: `sprendimai.py`
- Create: `tests/test_sprendimai.py`

**Interfaces:**
- Consumes: `kortele.rodyk_kortele`, `kortele._ivertink`, `kortele._atstatyk` (Tasks 4–5).
- Produces: `sprendimai.sprendimas_1()` … `sprendimas_4()`, each returning the `dict` namespace it built.

- [ ] **Step 1: Write the failing test**

Create `tests/test_sprendimai.py`:

```python
import pytest

import kortele
import sprendimai


@pytest.fixture(autouse=True)
def svari_kortele():
    kortele._atstatyk()
    yield
    kortele._atstatyk()


@pytest.mark.parametrize("lygis", [1, 2, 3, 4])
def test_pavyzdinis_sprendimas_praeina_savo_lygio_patikra(lygis, capsys):
    erdve = getattr(sprendimai, f"sprendimas_{lygis}")()
    praejo, eilutes = kortele._ivertink(lygis, erdve)
    assert praejo is True, "\n".join(eilutes)


@pytest.mark.parametrize("lygis", [1, 2, 3, 4])
def test_pavyzdinis_sprendimas_nenaudoja_placeholderiu(lygis, capsys):
    erdve = getattr(sprendimai, f"sprendimas_{lygis}")()
    for raktas, placeholderis in kortele.PLACEHOLDERS.items():
        assert erdve.get(raktas) != placeholderis
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest tests/test_sprendimai.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sprendimai'`

- [ ] **Step 3: Write the reference solutions**

Create `sprendimai.py`:

```python
"""Pavyzdiniai sprendimai mokytojui.

Kiekviena funkcija grąžina erdvę (dict), kurią galima perduoti
`kortele._ivertink(lygis, erdve)`. Testai tuo naudojasi, kad patikros ir
atsakymai niekada neišsiskirtų.
"""

import random

from kortele import rodyk_kortele


def sprendimas_1():
    vardas = "Birutė"
    amzius = 17
    miestas = "Kaunas"
    faktas = "turiu du šunis"

    rodyk_kortele(vardas, amzius, miestas, faktas)
    return {"vardas": vardas, "amzius": amzius, "miestas": miestas, "faktas": faktas}


def sprendimas_2():
    erdve = sprendimas_1()
    pomegiai = ["krepšinis", "fotografija", "animė"]

    rodyk_kortele(erdve["vardas"], erdve["amzius"], erdve["miestas"], erdve["faktas"],
                  pomegiai=pomegiai)
    erdve["pomegiai"] = pomegiai
    return erdve


def sprendimas_3():
    erdve = sprendimas_2()
    slapyvardis = f"{erdve['vardas'][:3].upper()}-{erdve['amzius'] * 2}"

    rodyk_kortele(erdve["vardas"], erdve["amzius"], erdve["miestas"], erdve["faktas"],
                  pomegiai=erdve["pomegiai"], slapyvardis=slapyvardis)
    erdve["slapyvardis"] = slapyvardis
    return erdve


def slapyvardis_is(vardas, amzius):
    """4 lygio a) variantas."""
    return f"{vardas[:3].upper()}-{amzius * 2}"


def sprendimas_4():
    erdve = sprendimas_3()
    faktai = ["turiu du šunis", "moku žongliruoti", "buvau Islandijoje"]

    rodyk_kortele(erdve["vardas"], erdve["amzius"], erdve["miestas"],
                  random.choice(faktai),
                  pomegiai=erdve["pomegiai"], slapyvardis=erdve["slapyvardis"],
                  tema="matrix")
    erdve["slapyvardis_is"] = slapyvardis_is
    erdve["random"] = random
    erdve["faktai"] = faktai
    return erdve
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m pytest tests/test_sprendimai.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add sprendimai.py tests/test_sprendimai.py
git commit -m "test: reference solutions pinned to the level checks"
```

---

### Task 7: `poros.py` — the teacher's pairing script

**Files:**
- Create: `poros.py`
- Create: `tests/test_poros.py`

**Interfaces:**
- Consumes: `misija.normalizuok`, `misija.generuok_flaga` (Task 1).
- Produces:
  - `poros.kolizijos(vardai: list[str]) -> list[str]` — normalised names appearing more than once.
  - `poros.sudaryk(vardai: list[str], raundai: int = 3) -> list[list[tuple[str, ...]]]` — one list per round; each entry is a 2-tuple, or a 3-tuple when the headcount is odd. Raises `ValueError` if `raundai` exceeds what round-robin can produce without repeating a pair.
  - `poros.lentele_tekstu(raundai_sarasas) -> str`
  - `poros.lentele_html(raundai_sarasas, klases_kodas) -> str`
  - CLI: `python poros.py klase.txt --kodas ZEBRAI2026 --raundai 3`

- [ ] **Step 1: Write the failing pairing tests**

Create `tests/test_poros.py`:

```python
import pytest

import poros

LYGINIS = ["Birutė", "Tomas", "Eglė", "Kazys", "Rūta", "Jonas"]
NELYGINIS = LYGINIS + ["Austėja"]


def _poros_rinkinys(raundas):
    """Visos 2 asmenų kombinacijos raunde, įskaitant trejetus."""
    rinkinys = set()
    for grupe in raundas:
        for i in range(len(grupe)):
            for j in range(i + 1, len(grupe)):
                rinkinys.add(frozenset((grupe[i], grupe[j])))
    return rinkinys


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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_poros.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'poros'`

- [ ] **Step 3: Implement `poros.py`**

Create `poros.py`:

```python
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

    vardai = _skaityk_vardus(args.klase)

    bedos = kolizijos(vardai)
    if bedos:
        print("❌ Šie vardai sutampa po normalizavimo ir gautų tą patį flagą:")
        for vardas in bedos:
            print(f"   {vardas}")
        print("   Pataisyk klase.txt (pvz. „Lukas B.“) ir paleisk iš naujo.")
        return 1

    raundai_sarasas = sudaryk(vardai, args.raundai)

    print(f"Klasės kodas: {args.kodas}")
    print(lentele_tekstu(raundai_sarasas))
    print("\n=== FLAGAI (tik mokytojui) ===")
    for vardas in sorted(vardai):
        print(f"   {vardas:<20} {misija.generuok_flaga(vardas, args.kodas)}")

    Path(args.html).write_text(lentele_html(raundai_sarasas, args.kodas), encoding="utf-8")
    print(f"\n📺 Projektuoti: {args.html}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_poros.py -v`
Expected: PASS

- [ ] **Step 5: Verify the CLI end to end**

```bash
printf 'Birutė\nTomas\nEglė\nKazys\nRūta\nJonas\nAustėja\n' > /tmp/klase_test.txt
python poros.py /tmp/klase_test.txt --kodas ZEBRAI2026 --html /tmp/poros_test.html
```

Expected: three rounds printed, each containing exactly one trio; a flag table;
`/tmp/poros_test.html` written. Then confirm the collision guard:

```bash
printf 'Lukas\nlukas\nEglė\nTomas\n' > /tmp/klase_kolizija.txt
python poros.py /tmp/klase_kolizija.txt --kodas ZEBRAI2026; echo "exit=$?"
```

Expected: the collision message and `exit=1`.

- [ ] **Step 6: Commit**

```bash
git add poros.py tests/test_poros.py
git commit -m "feat: teacher pairing script with collision guard"
```

---

### Task 8: Lesson content — markdown and starter cells

**Files:**
- Create: `turinys/00_ivadas.md`, `turinys/00_ivadas.py`
- Create: `turinys/01_lygis.md`, `turinys/01_lygis.py`
- Create: `turinys/02_lygis.md`, `turinys/02_lygis.py`
- Create: `turinys/03_lygis.md`, `turinys/03_lygis.py`
- Create: `turinys/04_lygis.md`, `turinys/04_lygis.py`
- Create: `turinys/05_misija.md`, `turinys/05_misija.py`
- Create: `turinys/06_mainai.md`, `turinys/06_mainai.py`
- Create: `turinys/07_finalas.md`, `turinys/07_finalas.py`

**Interfaces:**
- Consumes: the public APIs from Tasks 2, 4, 5.
- Produces: content files consumed by `build.py` (Task 9).

**Placeholder substitution syntax:** starter `.py` files use `@@name@@` tokens,
**not** `{}` — Level 3's starter contains an f-string with literal braces, so
`str.format` would break it. `build.py` does plain string replacement.
Available tokens: `@@vardas@@`, `@@amzius@@`, `@@miestas@@`, `@@faktas@@`,
`@@pomegiai@@`, `@@pavyzdys_vardas@@`, `@@pavyzdys_flagas@@`,
`@@pavyzdys_interesas@@`.

- [ ] **Step 1: Write the intro cells**

`turinys/00_ivadas.md`:

```markdown
# 👋 Sveiki! Šiandien susipažinsime su Python pagalba

Per artimiausias minutes kiekvienas parašysite programą, kuri atspausdins
jūsų asmeninę **kortelę**. Paskui su ja eisite ieškoti bendraklasių.

Nebijokite, jei Python matote pirmą kartą — pirmas lygis yra keturios
eilutės, ir jos jau beveik parašytos.

**Kaip dirbti:**
1. Spustelėkite ant langelio su kodu.
2. Pakeiskite tai, ko prašoma.
3. Paspauskite ▶️ (arba `Shift + Enter`), kad paleistumėte.

Pradėkime — paleiskite šį langelį:
```

`turinys/00_ivadas.py`:

```python
from kortele import rodyk_kortele, patikrink

print("Viskas paruošta! 🎉")
```

- [ ] **Step 2: Write the Level 1 cells**

`turinys/01_lygis.md`:

```markdown
## 1 lygis — Kas tu esi?

Apačioje yra keturi **kintamieji**. Kintamasis — tai vardas, kurį duodame
reikšmei, kad vėliau galėtume ja naudotis.

Pakeiskite Jono duomenis savais ir paleiskite langelį.

> 💡 Tekstas rašomas tarp kabučių: `"Vilnius"`. Skaičiui kabučių nereikia: `16`.
```

`turinys/01_lygis.py`:

```python
vardas  = "@@vardas@@"
amzius  = @@amzius@@
miestas = "@@miestas@@"
faktas  = "@@faktas@@"

rodyk_kortele(vardas, amzius, miestas, faktas)
patikrink(1)
```

- [ ] **Step 3: Write the Level 2 cells**

`turinys/02_lygis.md`:

```markdown
## 2 lygis — Ką mėgsti?

Vienas pomėgis kortelėje atrodytų liūdnai, todėl surašysime kelis iš karto.
Tam reikia **sąrašo** (angl. *list*) — reikšmių rinkinio laužtiniuose
skliaustuose, atskirtų kableliais.

Surašykite 2–4 savo pomėgius ir paleiskite langelį.

> 💡 Nepamirškite kablelio tarp pomėgių.
```

`turinys/02_lygis.py`:

```python
pomegiai = @@pomegiai@@

rodyk_kortele(vardas, amzius, miestas, faktas, pomegiai=pomegiai)
patikrink(2)
```

- [ ] **Step 4: Write the Level 3 cells**

`turinys/03_lygis.md`:

```markdown
## 3 lygis — Slaptas programuotojo vardas

Dabar reikšmės neįrašysime, o **apskaičiuosime** iš to, ką jau turime.

- `vardas[:3]` — pirmos trys vardo raidės
- `.upper()` — paverčia raides DIDŽIOSIOMIS
- `f"..."` — leidžia į tekstą įterpti reikšmes per `{ }`

Paleiskite ir pažiūrėkite, koks slapyvardis gavosi. Palyginkite su kaimynu!
```

`turinys/03_lygis.py`:

```python
slapyvardis = f"{vardas[:3].upper()}-{amzius * 2}"

rodyk_kortele(vardas, amzius, miestas, faktas, pomegiai=pomegiai, slapyvardis=slapyvardis)
patikrink(3)
```

- [ ] **Step 5: Write the Level 4 cells**

`turinys/04_lygis.md`:

```markdown
## 4 lygis — Laisvas režimas 🚀

Spėjote iki čia? Puiku. Toliau vieno teisingo atsakymo nėra.
Pasirinkite bent vieną užduotį arba sugalvokite savo:

**a) Slapyvardžių generatorius.** Parašykite funkciją
`slapyvardis_is(vardas, amzius)`, kuri grąžina slapyvardį bet kam — ne tik
jums. `patikrink(4)` ją išbandys su savais duomenimis.

**b) Atsitiktinis faktas.** Susikurkite kelių faktų sąrašą ir padarykite, kad
kortelė kaskart rodytų vis kitą. Užuomina: `import random` ir `random.choice(...)`.

**c) Kortelės tema.** `rodyk_kortele` turi slaptą argumentą `tema=`. Kokios
temos egzistuoja? Atsakymas yra faile `kortele.py` — atidarykite jį kairėje
esančiame failų sąraše.
```

`turinys/04_lygis.py`:

```python
# Rašyk čia 👇


patikrink(4)
```

- [ ] **Step 6: Write the mission cells**

`turinys/05_misija.md`:

```markdown
---

# 🏴 Antra užduotis: Flagų misija

Kiekvienas iš jūsų turi savo **flagą** — slaptą kodą. Jo nematote niekur,
išskyrus savo ekraną.

Jūsų tikslas: nueiti pas lentoje nurodytus bendraklasius, rasti su jais
**ką nors bendro**, ir apsikeisti flagais.

Įrašykite savo vardą (tokį, koks parašytas lentoje) ir klasės kodą:
```

`turinys/05_misija.py`:

```python
from misija import pradek_misija, irasyk_flaga, misijos_bukle

pradek_misija("@@vardas@@", "KLASES-KODAS")
```

- [ ] **Step 7: Write the exchange cells**

`turinys/06_mainai.md`:

```markdown
## Apsikeitimas

Po kiekvieno pokalbio pakeiskite duomenis ir paleiskite šį langelį iš naujo.

> 💡 Jei flagas nepriimamas — patikrinkite, ar gerai nurašėte vardą.
> Lietuviškos raidės ir didžiosios/mažosios nesvarbu.

**Greitiesiems:** tą patį galima padaryti su **žodynu** (`dict`) ir ciklu:
>
> ```python
> draugai = {
>     "Tomas": ("TOMA-4417", "krepšinis"),
>     "Eglė":  ("EGLE-9930", "šunys"),
> }
> for vardas, (flagas, interesas) in draugai.items():
>     irasyk_flaga(vardas, flagas, interesas)
> ```
```

`turinys/06_mainai.py`:

```python
irasyk_flaga("@@pavyzdys_vardas@@", "@@pavyzdys_flagas@@", "@@pavyzdys_interesas@@")
```

- [ ] **Step 8: Write the finale cells**

`turinys/07_finalas.md`:

```markdown
## Finalas — pilna kortelė

Dabar atvaizduokite kortelę dar kartą. Joje atsirado naujas skyrius su
žmonėmis, kuriuos šiandien pažinote.

Šią kortelę perskaitysite garsiai visai grupei.

> 💡 Jei spėjote 3 lygį, pridėkite `slapyvardis=slapyvardis`.
> Jei radote slaptą temą — pridėkite ir `tema="..."`.
```

`turinys/07_finalas.py`:

```python
rodyk_kortele(vardas, amzius, miestas, faktas, pomegiai=pomegiai)
```

The starter deliberately stops at Level 2's arguments. A pupil who never
reached Level 3 has no `slapyvardis` variable, and referencing it here would
raise a bare `NameError` in the lesson's final cell — the one moment when
everything must work. The markdown invites the ones who got further to add it.

- [ ] **Step 9: Verify every starter file is valid Python after substitution**

```bash
python - <<'PY'
from pathlib import Path
import kortele, misija

p = kortele.PLACEHOLDERS
pav_v, pav_f, pav_i = misija.PAVYZDYS
pakeitimai = {
    "@@vardas@@": p["vardas"], "@@amzius@@": str(p["amzius"]),
    "@@miestas@@": p["miestas"], "@@faktas@@": p["faktas"],
    "@@pomegiai@@": "[" + ", ".join(f'"{x}"' for x in p["pomegiai"]) + "]",
    "@@pavyzdys_vardas@@": pav_v, "@@pavyzdys_flagas@@": pav_f,
    "@@pavyzdys_interesas@@": pav_i,
}
for f in sorted(Path("turinys").glob("*.py")):
    src = f.read_text(encoding="utf-8")
    for k, v in pakeitimai.items():
        src = src.replace(k, v)
    compile(src, str(f), "exec")
    assert "@@" not in src, f"liko nepakeistas žymeklis: {f}"
    print("ok", f)
PY
```

Expected: `ok turinys/00_ivadas.py` through `ok turinys/07_finalas.py`, no errors.

- [ ] **Step 10: Commit**

```bash
git add turinys/
git commit -m "feat: Lithuanian lesson content and starter cells"
```

---

### Task 9: `build.py` — assemble the notebook

**Files:**
- Create: `build.py`
- Create: `tests/test_build.py`

**Interfaces:**
- Consumes: `kortele.PLACEHOLDERS` (Task 4), `misija.PAVYZDYS` (Task 2), `turinys/` (Task 8).
- Produces:
  - `build.PAKEITIMAI: dict[str, str]` — the `@@token@@` → literal map.
  - `build.pakeisk(tekstas: str) -> str`
  - `build.sukurk_notebooka() -> dict` — the notebook as a JSON-ready dict.
  - `build.irasyk_notebooka(kelias: str = "intro_kortele.ipynb") -> Path`
  - CLI: `python build.py` writes the notebook, then runs `jupyter lite build`.

- [ ] **Step 1: Write the failing build tests**

Create `tests/test_build.py`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_build.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'build'`

- [ ] **Step 3: Implement `build.py`**

Create `build.py`:

```python
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


def statyk_svetaine(isvestis="dist"):
    # Patvirtinta komanda (žr. 10 užduoties 1 žingsnį):
    komanda = ["jupyter", "lite", "build", "--output-dir", isvestis]
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_build.py -v`
Expected: PASS

- [ ] **Step 5: Generate the notebook and run the full suite**

```bash
python build.py --tik-nb
python -m pytest -v
```

Expected: `intro_kortele.ipynb` written; all tests pass.

- [ ] **Step 6: Commit**

```bash
git add build.py tests/test_build.py intro_kortele.ipynb
git commit -m "feat: build notebook from content files"
```

---

### Task 10: JupyterLite site build and GitHub Pages deploy

**Files:**
- Modify: `build.py` (only if the CLI check in Step 1 shows a different invocation)
- Create: `.github/workflows/deploy.yml`

**Interfaces:**
- Consumes: `build.main` (Task 9).
- Produces: a published site; no Python interface.

- [ ] **Step 1: Verify the actual JupyterLite CLI invocation**

The exact entry point and flag names must be confirmed against the installed
version rather than assumed:

```bash
python -m pip show jupyterlite-core | head -3
jupyter lite --help
jupyter lite build --help | grep -iE 'contents|output-dir'
```

`statyk_svetaine` is written against `jupyter lite build --contents <file>
--output-dir <dir>`. If `--help` reports different flag names for the installed
version, update `statyk_svetaine` to match and amend the comment above it. Do
not guess — this is the one step with an external dependency.

- [ ] **Step 2: Build the site locally**

```bash
python build.py
ls dist/
```

Expected: `dist/` contains `index.html`, a `lab/` or `notebooks/` directory, and
the bundled contents.

- [ ] **Step 3: Verify the bundled files are present and `poros.py` is not**

```bash
find dist -name 'kortele.py' -o -name 'misija.py' -o -name 'intro_kortele.ipynb' | sort
find dist -name 'poros.py' -o -name 'klase.txt' | wc -l
```

Expected: the first command lists all three files; the second prints `0`.

- [ ] **Step 4: Smoke-test the site in a browser**

```bash
python -m http.server 8000 --directory dist
```

Open `http://localhost:8000`, open `intro_kortele.ipynb`, and run every cell top
to bottom. Confirm: the setup cell imports cleanly; Level 1 prints a card and the
`✋` placeholder message; `kortele.py` and `misija.py` are visible in the file
browser; the Level 4 markdown's instruction to open `kortele.py` actually works.

Stop the server when done.

- [ ] **Step 5: Write the deploy workflow**

Create `.github/workflows/deploy.yml`:

```yaml
name: deploy

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install -r requirements-dev.txt
      - run: python -m pytest -v
      - run: python build.py
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: dist

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 6: Commit**

```bash
git add .github/workflows/deploy.yml build.py
git commit -m "ci: build and publish JupyterLite site to GitHub Pages"
```

- [ ] **Step 7: Push and verify the deploy**

Requires the GitHub remote and Pages source set to "GitHub Actions" in the
repository settings. Push, watch the Action, then open the published URL and
repeat the Step 4 smoke test against it. Record the live URL — Task 11 needs it.

---

### Task 11: Teacher guide and README

**Files:**
- Create: `mokytojui.md`
- Create: `README.md`

**Interfaces:**
- Consumes: the live Pages URL from Task 10 Step 7.
- Produces: documentation only.

- [ ] **Step 1: Write `mokytojui.md`**

Write it with these sections, filling the real URL in place of `<PAGES-URL>`:

1. **Nuoroda mokiniams** — `<PAGES-URL>`, plus the offline fallback: copy
   `dist/` to a USB stick, `python -m http.server 8000 --directory dist`,
   pupils open `http://<laptop-ip>:8000`. Note that many school networks use
   client isolation, which blocks this — test it before relying on it.
2. **Prieš pamoką (checklist)** — run from the school network, not from home:
   - open `<PAGES-URL>` on a phone over school wifi; confirm Pyodide finishes
     loading and a cell runs;
   - confirm the content filter does not block `github.io`;
   - run `python poros.py klase.txt --kodas <KODAS>` and resolve any name
     collisions it reports;
   - print or project `poros_lentele.html`; write the class code on the board.
3. **Eiga** — the minute-by-minute table from spec §4.4, noting that round
   length (5 min) is the dial to turn on the day.
4. **Pavyzdiniai sprendimai** — point at `sprendimai.py` and show the Level 1–4
   answers inline.
5. **Dažniausios klaidos** — each with the one-line Lithuanian fix:
   - text without quotes → `vardas = Birutė` vs `vardas = "Birutė"`;
   - smart quotes pasted from a chat app → `„Birutė“` vs `"Birutė"`;
   - Lithuanian letters in an identifier → `pomėgiai` vs `pomegiai`;
   - missing comma in a list → `["futbolas" "šunys"]`.
6. **Misijos logistika** — class code on the board, pairing table projected,
   a timer, the "keičiamės" call every 5 minutes.
7. **Saugumo aptarimas (scripted)** — the closing five minutes:

   > *"Ar kas nors gavo flagą nepakalbėjęs su tuo žmogumi?"*
   >
   > Whoever did gets credit. Then: the page has to check flags, so the page
   > has to be able to make flags — the algorithm is in `misija.py`, which
   > every pupil downloaded. Nothing sent to a browser is secret. This is why
   > real systems check passwords on a server, and why "hidden" client-side
   > code is not protection.
8. **Kortelių skaitymas** — prompts for the closing round.

- [ ] **Step 2: Write `README.md`**

Cover: what the lesson is; the live URL; `pip install -r requirements-dev.txt`;
`python -m pytest`; `python build.py`; `python build.py --tik-nb`;
`python poros.py klase.txt --kodas <KODAS>`; the file map (engines, content,
teacher tooling, generated artefacts); and the rule that `klase.txt` and
`poros_*.html` are gitignored and must never be committed.

- [ ] **Step 3: Verify every documented command actually runs**

```bash
python -m pytest -q
python build.py --tik-nb
python poros.py /tmp/klase_test.txt --kodas ZEBRAI2026 --html /tmp/poros_check.html
```

Expected: all three succeed. Fix the docs if any command differs from what is
written.

- [ ] **Step 4: Commit**

```bash
git add mokytojui.md README.md
git commit -m "docs: teacher guide and README"
```
