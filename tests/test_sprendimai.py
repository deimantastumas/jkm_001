import pytest

import kortele
import sprendimai


@pytest.mark.parametrize("lygis", [1, 2, 3, 4])
def test_pavyzdinis_sprendimas_atvaizduoja_kortele(lygis, capsys):
    """Mokytojas šiuos rodo klasei — jie privalo nulūžti niekada."""
    erdve = getattr(sprendimai, f"sprendimas_{lygis}")()
    isvestis = capsys.readouterr().out
    assert erdve["vardas"] in isvestis.upper() or erdve["vardas"].upper() in isvestis
    assert "Traceback" not in isvestis


@pytest.mark.parametrize("lygis", [1, 2, 3, 4])
def test_pavyzdinis_sprendimas_nenaudoja_placeholderiu(lygis, capsys):
    erdve = getattr(sprendimai, f"sprendimas_{lygis}")()
    for raktas, placeholderis in kortele.PLACEHOLDERS.items():
        assert erdve.get(raktas) != placeholderis
