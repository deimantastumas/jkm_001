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
