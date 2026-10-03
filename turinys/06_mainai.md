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
for vardas, (flagas, interesas) in draugai.items():
    irasyk_flaga(vardas, flagas, interesas)
```
