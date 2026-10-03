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
    _atvaizduok(erdve)
    praejo, eilutes = kortele._ivertink(2, erdve)
    assert praejo is False
    assert any("sąrašas" in e for e in eilutes)


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


# Not from the brief: slapyvardis_is is exactly the kind of thing confident
# pupils write themselves at level 4, and a function that raises is a
# realistic input, not a hypothetical. Pins that the try/except in
# _ivertink_4 actually survives it.
def test_lygis4_funkcija_kuri_meta_klaida_nelunka():
    def blogas_slapyvardis(vardas, amzius):
        raise ValueError("kažkas negerai")

    erdve = {"slapyvardis_is": blogas_slapyvardis}
    praejo, eilutes = kortele._ivertink(4, erdve)
    assert praejo is True
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


# Not from the brief: the brief's own tests always pass erdve= explicitly,
# so the sys._getframe(1).f_globals default path (what a pupil's bare
# `patikrink(2)` in a notebook cell actually relies on) was never exercised.
# exec() with a single globals dict mimics a notebook cell's top-level
# namespace, where locals are globals.
def test_patikrink_be_erdve_naudoja_skambintojo_globalius(capsys):
    vykdymo_erdve = {"kortele": kortele}
    vykdymo_erdve.update(_erdve_1())
    exec(
        "kortele.rodyk_kortele(vardas, amzius, miestas, faktas)\n"
        "kortele.patikrink(1)\n",
        vykdymo_erdve,
    )
    israsyta = capsys.readouterr().out
    assert "✅" in israsyta
