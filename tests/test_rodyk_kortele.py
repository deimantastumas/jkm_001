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
    # 46 vidaus stulpeliai + po vieną rėmelio simbolį iš abiejų pusių.
    # Lygybė tarp dviejų eilučių viena pati praeitų ir tada, jei plotis
    # nuplauktų abiejose vienodai.
    assert kortele._plotis(trumpa) == 48
    assert kortele._plotis(ilga) == 48


def test_apkarpyk_nuline_plocis_grazina_tuscia():
    assert kortele._apkarpyk("Birutė", 0) == ""


def test_apkarpyk_vieno_plocio_grazina_elipsi():
    assert kortele._apkarpyk("abc", 1) == "…"


@pytest.fixture(autouse=True)
def svari_kortele():
    kortele._atstatyk()
    yield
    kortele._atstatyk()


def _eilutes(capsys):
    return [e for e in capsys.readouterr().out.split("\n") if e]


def test_kortele_visos_eilutes_vienodo_plocio(capsys):
    kortele.rodyk_kortele("Birutė", 16, "robotas", "turiu du šunis")
    plociai = {kortele._plotis(e) for e in _eilutes(capsys)}
    assert len(plociai) == 1


def test_kortele_su_visais_laukais_lieka_lygi(capsys):
    kortele.rodyk_kortele(
        "Birutė", 16, "robotas", "turiu du šunis",
        pomegiai=["futbolas", "programavimas"],
        slapyvardis="BIR-32",
        bendri_interesai=[("Tomas", "krepšinis")],
    )
    plociai = {kortele._plotis(e) for e in _eilutes(capsys)}
    assert len(plociai) == 1


def test_kortele_labai_ilga_reiksme_nesulauzo_remelio(capsys):
    kortele.rodyk_kortele("Birutė", 16, "robotas", "x" * 500)
    plociai = {kortele._plotis(e) for e in _eilutes(capsys)}
    assert len(plociai) == 1


@pytest.mark.parametrize("tema", ["klasika", "matrix", "neonas"])
def test_visos_temos_atvaizduojamos(tema, capsys):
    kortele.rodyk_kortele("Birutė", 16, "robotas", "faktas",
                          pomegiai=["futbolas", "šunys"], tema=tema)
    isvestis = "\n".join(_eilutes(capsys))
    assert isvestis
    for simbolis in kortele._TEMOS[tema].values():
        assert simbolis in isvestis, f"{tema}: trūksta rėmelio simbolio {simbolis!r}"
    svetimi = {s for kita, zenklai in kortele._TEMOS.items() if kita != tema
               for s in zenklai.values()} - set(kortele._TEMOS[tema].values())
    assert not (svetimi & set(isvestis)), f"{tema} atvaizdavo svetimos temos rėmelį"


def test_nezinoma_tema_duoda_zinute(capsys):
    kortele.rodyk_kortele("Birutė", 16, "robotas", "faktas", tema="vienaragis")
    isvestis = capsys.readouterr().out
    assert "tema" in isvestis.lower()
    assert "klasika" in isvestis


# Review Focus 5: the most common beginner mistakes.
def test_amzius_kaip_tekstas_duoda_zinute_o_ne_klaida(capsys):
    kortele.rodyk_kortele("Birutė", "16", "robotas", "faktas")
    assert "amzius" in capsys.readouterr().out


def test_tuscias_vardas_duoda_zinute(capsys):
    kortele.rodyk_kortele("", 16, "robotas", "faktas")
    assert "vardas" in capsys.readouterr().out


def test_pomegiai_ne_sarasas_duoda_zinute(capsys):
    kortele.rodyk_kortele("Birutė", 16, "robotas", "faktas", pomegiai="futbolas")
    assert "pomegiai" in capsys.readouterr().out


# bendri_interesai is not taught, but level 4 sends pupils hunting through
# kortele.py's source for undocumented keyword arguments — it sits right
# next to tema= in the signature, so a malformed value here must also
# print a hint rather than raise.
def test_bendri_interesai_tekstas_duoda_zinute(capsys):
    kortele.rodyk_kortele("Birutė", 16, "robotas", "faktas", bendri_interesai="krepšinis")
    assert "bendri_interesai" in capsys.readouterr().out
    assert kortele._paskutine_kortele is None


def test_bendri_interesai_sarasas_tekstu_duoda_zinute(capsys):
    kortele.rodyk_kortele("Birutė", 16, "robotas", "faktas",
                          bendri_interesai=["Tomas", "krepšinis"])
    assert "bendri_interesai" in capsys.readouterr().out
    assert kortele._paskutine_kortele is None


def test_bendri_interesai_netinkamo_ilgio_poros_duoda_zinute(capsys):
    kortele.rodyk_kortele("Birutė", 16, "robotas", "faktas",
                          bendri_interesai=[("Tomas", "krepšinis", "papildomai")])
    assert "bendri_interesai" in capsys.readouterr().out
    assert kortele._paskutine_kortele is None


def test_bloga_ivestis_nepalieka_paskutines_korteles(capsys):
    kortele.rodyk_kortele("Birutė", "16", "robotas", "faktas")
    assert kortele._paskutine_kortele is None


def test_paskutine_kortele_irasoma(capsys):
    kortele.rodyk_kortele("Birutė", 16, "robotas", "faktas", pomegiai=["a", "b"])
    assert kortele._paskutine_kortele["vardas"] == "Birutė"
    assert kortele._paskutine_kortele["pomegiai"] == ["a", "b"]
    assert kortele._paskutine_kortele["slapyvardis"] is None


def test_bendri_interesai_paimami_is_misijos_kai_nenurodyti(capsys):
    import misija
    misija._atstatyk()
    try:
        misija.pradek_misija("Birutė", "ZEBRAI2026")
        misija.irasyk_flaga("Tomas", misija.generuok_flaga("Tomas", "ZEBRAI2026"), "krepšinis")
        capsys.readouterr()
        kortele.rodyk_kortele("Birutė", 16, "robotas", "faktas")
        assert "krepšinis" in capsys.readouterr().out
    finally:
        misija._atstatyk()


def test_slapyvardis_ne_tekstas_duoda_zinute(capsys):
    kortele.rodyk_kortele("Birutė", 16, "robotas", "faktas", slapyvardis=42)
    assert "slapyvardis" in capsys.readouterr().out
    assert kortele._paskutine_kortele is None


# Minor fix: kortelė rodė „su Tomas – krepšinis“; taisyklinga lietuvių kalba
# reikalautų įnagininko („su Tomu“), o linksniavimas yra už pamokos ribų.
def test_bendri_interesai_rodomi_be_prielinksnio(capsys):
    kortele.rodyk_kortele("Birutė", 16, "robotas", "faktas",
                          bendri_interesai=[("Tomas", "krepšinis")])
    isvestis = capsys.readouterr().out
    assert "Tomas – krepšinis" in isvestis
    assert "su Tomas" not in isvestis



# --- Ilgų atsakymų laužymas ------------------------------------------------
#
# `svajoniu_projektas` ir `faktas` yra laisvo teksto laukai — mokinys parašo
# sakinį. Kortelės vidus yra 46 stulpeliai, tad ilgą atsakymą reikia perkelti
# į kitą eilutę, o ne nukirsti: būtent šį lauką mokinys skaito garsiai.

def test_lauzyk_trumpas_tekstas_lieka_vienoje_eiluteje():
    assert kortele._lauzyk("trumpas", 20) == ["trumpas"]


def test_lauzyk_lauzo_ties_zodziu_riba():
    eilutes = kortele._lauzyk("žaidimas kuriame katinai valdo kosminius laivus", 20)
    assert len(eilutes) > 1
    assert all(kortele._plotis(e) <= 20 for e in eilutes)
    assert " ".join(eilutes) == "žaidimas kuriame katinai valdo kosminius laivus"


def test_lauzyk_nepertraukia_zodziu_vidurio():
    eilutes = kortele._lauzyk("vienas du trys keturi penki", 12)
    for eilute in eilutes:
        assert not eilute.startswith(" ") and not eilute.endswith(" ")
        for zodis in eilute.split():
            assert zodis in "vienas du trys keturi penki".split()


def test_lauzyk_nenutraukiamas_zodis_apkarpomas():
    eilutes = kortele._lauzyk("a" * 60, 20)
    assert all(kortele._plotis(e) <= 20 for e in eilutes)


def test_lauzyk_lietuviskos_raides_skaiciuojamos_po_viena():
    eilutes = kortele._lauzyk("ąčęėįšųūž ąčęėįšųūž", 9)
    assert eilutes == ["ąčęėįšųūž", "ąčęėįšųūž"]


def test_ilgas_svajoniu_projektas_nesulauzo_remelio(capsys):
    kortele.rodyk_kortele(
        "Birutė", 17,
        "žaidimas, kuriame katinai valdo kosminius laivus ir kovoja su šunimis",
        "turiu du šunis",
    )
    plociai = {kortele._plotis(e) for e in _eilutes(capsys)}
    assert plociai == {48}


def test_ilgas_faktas_taip_pat_lauzomas(capsys):
    kortele.rodyk_kortele(
        "Birutė", 17, "Nuotykių programėlė",
        "kartą per vasarą perplaukiau ežerą pirmyn ir atgal be sustojimo",
    )
    isvestis = capsys.readouterr().out
    assert "be sustojimo" in isvestis
    assert "…" not in isvestis
