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
    assert "vard" in capsys.readouterr().out.lower()


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
# TypeError later, inside misijos_bukle's "_tikslas - len(_draugai)" — which
# runs automatically from irasyk_flaga's success path. Must print, not raise,
# and must leave the mission unregistered.
@pytest.mark.parametrize("blogas_tikslas", ["3", 0, -1])
def test_pradek_misija_su_netinkamu_tikslu_nemeta_klaidos_ir_neregistruoja(capsys, blogas_tikslas):
    misija.pradek_misija("Birutė", "ZEBRAI2026", tikslas=blogas_tikslas)
    assert "tikslas" in capsys.readouterr().out.lower()
    assert misija._mano_norm is None
