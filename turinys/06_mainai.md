## Apsikeitimas

Po kiekvieno pokalbio pakeiskite duomenis ir paleiskite šį langelį iš naujo.

> 💡 Jei flagas nepriimamas — patikrinkite, ar gerai nurašėte vardą.
> Lietuviškos raidės ir didžiosios/mažosios nesvarbu.

**Greitiesiems:** tą patį galima padaryti su **žodynu** (`dict`) ir ciklu:

```python
draugai = {
    "Tomas": ("TOMA-4417", "krepšinis"),
    "Eglė":  ("EGLE-9930", "šunys"),
}
for draugo_vardas, (draugo_flagas, bendras) in draugai.items():
    irasyk_flaga(draugo_vardas, draugo_flagas, bendras)
```

> ⚠ Atkreipkite dėmesį: ciklo kintamasis pavadintas `draugo_vardas`, o ne
> `vardas`. Jei pavadintume `vardas`, ciklas perrašytų jūsų pačių `vardas`
> reikšmę iš 1 lygio, ir kortelė gale rodytų paskutinio draugo vardą.
