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
    isvestis = capsys.readouterr().out
    assert "per mažai raidžių" in isvestis
    assert misija._mano_norm is None


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
    assert "Savo paties flago įrašyti negalima" in capsys.readouterr().out


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
    assert "Flagas netinka" in capsys.readouterr().out


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
    assert "Surinkta flagų: 1" in isvestis
    assert "Tomas" in isvestis


# Moved here per task-2 ruling: these call irasyk_flaga/surinkti, which do not
# exist until this step, so they cannot run as part of the Step 1 block.
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


# Fix round 1, Important finding: tikslas was never validated, so a bad
# value (e.g. a quoted string) stored into module state would raise a raw
# TypeError later, inside misijos_bukle's "_tikslas - len(_draugai)". Must
# print, not raise, and must leave the mission unregistered.

@pytest.mark.parametrize("kodas", ["KLASES-KODAS", "klases-kodas", " KLASES-KODAS "])
def test_pradek_misija_su_vietazenkliu_kodu_neregistruoja(capsys, kodas):
    misija.pradek_misija("Jonas", kodas)
    isvestis = capsys.readouterr().out
    assert isvestis.startswith("✋")
    assert "Misija pradėta" not in isvestis
    assert misija._mano_norm is None


def test_nepataisytas_starteris_nepradeda_misijos(capsys):
    """Tiksliai tai, ką mokinys paleidžia, nieko nepakeitęs."""
    import kortele
    misija.pradek_misija(kortele.PLACEHOLDERS["vardas"], misija.PLACEHOLDER_KODAS)
    isvestis = capsys.readouterr().out
    assert "Misija pradėta" not in isvestis
    assert misija._mano_norm is None


def test_vardo_vietazenklis_tik_perspeja_bet_registruoja(capsys):
    """Tikras Jonas privalo galėti dalyvauti.

    Vardas, skirtingai nei klasės kodas, dviprasmis: „Jonas“ yra vienas
    dažniausių tikrų vardų. Blokavimas jį išmestų iš visos antros pamokos
    dalies, tad čia tik priminimas.
    """
    import kortele
    misija.pradek_misija(kortele.PLACEHOLDERS["vardas"], "ZEBRAI2026")
    isvestis = capsys.readouterr().out
    assert "✋" in isvestis
    assert "Misija pradėta" in isvestis
    assert misija._mano_norm == "deimantas"


def test_placeholder_kodas_atitinka_starterio_langeli():
    from pathlib import Path
    import build
    starteris = build.pakeisk(Path("turinys/05_misija.py").read_text(encoding="utf-8"))
    assert f'"{misija.PLACEHOLDER_KODAS}"' in starteris


def test_neteisingas_flagas_nurodo_ir_savo_pradek_misija_eilute(capsys):
    _pradek()
    misija.irasyk_flaga("Tomas", "TOMA-0001", "krepšinis")
    isvestis = capsys.readouterr().out
    assert "pradek_misija" in isvestis
    assert "klasės kodą" in isvestis


# ---- I2: vardo pataisymas ištrina flagus — bet nebe tyliai ----

def test_vardo_pakeitimas_pranesa_apie_prarastus_flagus(capsys):
    misija.pradek_misija("Birutė", "ZEBRAI2026")
    misija.irasyk_flaga("Tomas", misija.generuok_flaga("Tomas", "ZEBRAI2026"), "krepšinis")
    capsys.readouterr()
    misija.pradek_misija("Birutė Jonaitytė", "ZEBRAI2026")
    isvestis = capsys.readouterr().out
    assert "⚠" in isvestis
    assert "nebegalioja" in isvestis
    assert misija.surinkti() == []


def test_vardo_pakeitimas_be_surinktu_flagu_netyli_be_reikalo(capsys):
    misija.pradek_misija("Birutė", "ZEBRAI2026")
    capsys.readouterr()
    misija.pradek_misija("Eglė", "ZEBRAI2026")
    assert "⚠" not in capsys.readouterr().out


# ---- I4: misijos_bukle kviečiama starterio langelio, ne irasyk_flaga ----

def test_irasyk_flaga_nedubliuoja_bukles(capsys):
    _pradek()
    misija.irasyk_flaga("Tomas", misija.generuok_flaga("Tomas", "ZEBRAI2026"), "krepšinis")
    isvestis = capsys.readouterr().out
    assert "✅ Tomas — krepšinis" in isvestis
    assert "Misijos būklė" not in isvestis


def test_starterio_langelis_kviecia_misijos_bukle():
    from pathlib import Path
    assert "misijos_bukle()" in Path("turinys/06_mainai.py").read_text(encoding="utf-8")


# ---- I3: likusios mokiniui rodomos šakos ----

@pytest.mark.parametrize("blogas_vardas", [None, 17, "", "   "])
def test_pradek_misija_be_vardo_nemeta_klaidos(capsys, blogas_vardas):
    misija.pradek_misija(blogas_vardas, "ZEBRAI2026")
    assert "Įrašyk savo vardą kabutėse" in capsys.readouterr().out
    assert misija._mano_norm is None


@pytest.mark.parametrize("blogas_kodas", [None, 2026, "", "   "])
def test_pradek_misija_be_klases_kodo_nemeta_klaidos(capsys, blogas_kodas):
    misija.pradek_misija("Birutė", blogas_kodas)
    assert "Klasės kodas užrašytas ant lentos" in capsys.readouterr().out
    assert misija._mano_norm is None


@pytest.mark.parametrize("vardas, flagas", [
    (None, "TOMA-0001"), ("Tomas", None), (17, 42), (["Tomas"], "TOMA-0001"),
])
def test_irasyk_flaga_ne_tekstiniai_argumentai_nemeta_klaidos(capsys, vardas, flagas):
    _pradek()
    misija.irasyk_flaga(vardas, flagas, "krepšinis")
    assert "rašomi kabutėse" in capsys.readouterr().out
    assert misija.surinkti() == []


def test_irasyk_flaga_neflaguojamas_draugo_vardas(capsys):
    _pradek()
    misija.irasyk_flaga("Ą", "AA-0001", "krepšinis")
    isvestis = capsys.readouterr().out
    assert "flago sudaryti nepavyko" in isvestis
    assert "Patikrink rašybą" in isvestis
    assert misija.surinkti() == []


def test_misijos_bukle_pries_pradek_misija_yra_zinute(capsys):
    misija.misijos_bukle()
    assert "pradek_misija" in capsys.readouterr().out




def test_saltinyje_nera_variacijos_selektoriu():
    from pathlib import Path
    assert "\ufe0f" not in Path("misija.py").read_text(encoding="utf-8")
    assert "\ufe0f" not in Path("kortele.py").read_text(encoding="utf-8")

