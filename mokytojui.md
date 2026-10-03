# Mokytojui — „Prisistatymo kortelė“ + „Flagų misija“

70 minučių pamoka, du iššūkiai. Šis dokumentas skirtas skaityti vakare prieš
pamoką ir dar kartą — stovint prieš klasę.

## DĖMESIO — pirmiausia: gauk tikrą nuorodą

Šiame faile visur, kur reikėtų nuorodos mokiniams, parašyta `<PAGES-URL>`.
**Tai ne tikra nuoroda — ją reikia susikurti vieną kartą:**

1. Sukurk GitHub repozitoriją ir į ją `push` šio projekto `main` šaką.
2. Repozitorijos `Settings → Pages → Build and deployment → Source` nustatyk
   **„GitHub Actions“** (ne „Deploy from a branch“).
3. Palauk, kol repo `Actions` skiltyje `deploy` workflow baigs veikti (žalia
   varnelė).
4. Atsidaręs `Settings → Pages` pamatysi gyvą adresą — jis atrodys panašiai
   į `https://<vartotojas>.github.io/<repo>/`.
5. Pakeisk **visus** šio failo `<PAGES-URL>` įrašus į šį adresą.

Kol to nepadarei, šis vadovas naudoti pamokoje netinka — mokiniai neturės kur
eiti.

## 1. Nuoroda mokiniams

Pagrindinė nuoroda (atverti JupyterLite notebooką):

```
<PAGES-URL>
```

**Atsarginis variantas be interneto** (jei mokyklos wifi neveikia arba
filtras blokuoja):

1. Nukopijuok `dist/` aplanką į USB raktą arba tiesiai į mokytojo
   kompiuterį. `dist/` nėra įkeltas į git (jis sugeneruojamas iš naujo
   kiekvieną kartą) — jį pasiruoši §2 „Prieš pamoką“ sąraše žemiau, pirmame
   punkte, prieš pamoką.
2. Iš `001/` aplanko paleisk:
   ```
   ./.venv/bin/python -m http.server 8000 --directory dist
   ```
3. Pasakyk mokiniams atsiverti `http://<tavo-kompiuterio-ip>:8000` (IP
   gauni `ipconfig getifaddr en0` arba iš tinklo nustatymų).

**Svarbu:** daugelis mokyklų tinklų naudoja **client isolation** (įrenginiai
laidiniame/wifi tinkle nemato vienas kito) — tokiu atveju šis būdas
neveiks. **Išbandyk jį iš anksto**, ne pamokos metu.

## 2. Prieš pamoką (checklist)

Visa tai daryk **iš mokyklos tinklo**, ne iš namų — namie viskas atrodo
veikiantis, bet mokyklos wifi ir filtrai gali elgtis kitaip.

- [ ] Pasiruošk atsarginį variantą be interneto: paleisk
      `./.venv/bin/python build.py`, patikrink, ar `dist/` aplankas
      atsirado/atsinaujino, ir nukopijuok jį į USB raktą arba mokytojo
      kompiuterį (žr. §1). Tai daryk **net jei** planuoji naudoti tik
      `<PAGES-URL>` — tai tavo saugiklis, jei wifi ar filtras pamokos metu
      pakiš koją.
- [ ] Atsiversk `<PAGES-URL>` telefonu per mokyklos wifi. Palauk, kol
      Pyodide pilnai įsikels (pirmas kartas gali užtrukti 20-40 s), ir
      paleisk bent vieną langelį — jis turi grąžinti rezultatą be klaidų.
- [ ] Patikrink, ar mokyklos turinio filtras neblokuoja `github.io`.
- [ ] Paruošk klasės sąrašą `klase.txt` (po vieną vardą eilutėje, lygiai
      taip, kaip nori, kad mokiniai juos rašytų) ir paleisk:
      ```
      ./.venv/bin/python poros.py klase.txt --kodas <KODAS>
      ```
      Jei scenarijus praneša apie vardų koliziją (du mokiniai su tuo pačiu
      vardu gautų tą patį flagą), pataisyk `klase.txt` (pvz. „Lukas B.“
      vietoj „Lukas“) ir paleisk iš naujo — be to jis lentelės neišves.
- [ ] Atsispausdink arba atsiversk projektavimui `poros_lentele.html` (jį
      sugeneravo tas pats paleidimas).
- [ ] Prieš pamoką užrašyk klasės kodą (`<KODAS>`) ant lentos — tą patį,
      kurį naudojai `poros.py` komandoje.

## 3. Eiga

| Min. | Veikla |
| --- | --- |
| 3 | Pristatai, ką šiandien darysime |
| 5 | Visi atsiveria nuorodą, paleidžia pirmą (parengiamąjį) langelį |
| 8 | 1 lygis |
| 7 | 2 lygis |
| 7 | 3 lygis |
| ~8 | 4 lygis (greitesniems; kiti dar baigia ankstesnius) |
| 2 | Misijos pristatymas, projektuojama porų lentelė, kodas ant lentos |
| 2 | Visi paleidžia `pradek_misija(...)`, pamato savo flagą |
| 15 | 3 raundai × 5 min, komanda „keičiamės!“ pagal laikmatį |
| 4 | Galutinės kortelės atvaizdavimas |
| 5 | Saugumo aptarimas |

**5 minučių raundo ilgis yra tai, ką verta koreguoti pačią dieną** —
priklausomai nuo klasės dydžio ir tempo. Jei matai, kad niekas nespėja,
duok 6-7 min; jei visi greitai susitvarko, trumpink iki 4.

## 4. Pavyzdiniai sprendimai

Visi keturi lygiai yra `sprendimai.py` — `sprendimas_1()` .. `sprendimas_4()`.

**Svarbu:** jie sujungti grandine — `sprendimas_2()` pirmiausia iškviečia
`sprendimas_1()` ir prideda prie jo rezultato, `sprendimas_3()` iškviečia
`sprendimas_2()` ir t. t. Tai reiškia:
- konkrečios reikšmės (vardas, amžius, miestas, faktas) užrašytos **tik
  `sprendimas_1()` viduje** — kituose levelio sprendimuose jų nebeieškok;
- failą skaityk nuo viršaus į apačią kaip vieną tekstą, o ne kaip keturias
  nepriklausomas funkcijas.

Trumpai, kas kiekviename:

- **1 lygis** — `vardas`, `amzius`, `miestas`, `faktas` kintamieji,
  perduoti `rodyk_kortele(...)`.
- **2 lygis** — prideda `pomegiai` sąrašą (bent 2 elementai), perduoda
  `pomegiai=pomegiai`.
- **3 lygis** — sugalvoja `slapyvardis` iš vardo ir amžiaus
  (`f"{vardas[:3].upper()}-{amzius * 2}"`), perduoda `slapyvardis=slapyvardis`.
- **4 lygis (laisvas)** — demonstruoja a) funkciją `slapyvardis_is(vardas,
  amzius)`, b) `random.choice(...)` tarp kelių faktų, c) slaptą temą
  (`tema="matrix"`). Čia teisingo atsakymo nėra — `patikrink(4)` visada
  tik aprašo, ką rado.

**Kai mokinys įstrigo — ką paleisti pirmiausia:**

- `patikrink(1)` / `patikrink(2)` / `patikrink(3)` — pasako, kurio kintamojo
  trūksta arba kuris dar neperduotas kortelei.
- `misijos_bukle()` — parodo, ar mokinys apskritai užsiregistravo
  (`pradek_misija`), kiek flagų jau surinkta ir su kuo. Jei ji sako
  „Pirmiausia paleisk langelį su pradek_misija(...)“ — visa misijos dalis jam
  dar neveikia, ir tai svarbiausia pataisyti.
- Tavo paties flagų sąrašas iš `poros.py` — greičiausias būdas patikrinti, ar
  mokinys tikrai užsiregistravo ta vardo rašyba, kuri yra lentelėje: palygink
  jo ekrane rodomą flagą su sąraše esančiu.

## 5. Dažniausios klaidos

| Klaida | Neteisingai | Teisingai | Vienas sakinys mokiniui |
| --- | --- | --- | --- |
| Tekstas be kabučių | `vardas = Birutė` | `vardas = "Birutė"` | Tekstą visada rašome tarp kabučių — be jų Python ieško kintamojo, vardu „Birutė“. |
| „Protingos“ kabutės iš pokalbių programos | `vardas = „Birutė“` | `vardas = "Birutė"` | Nekopijuok teksto iš Messenger/WhatsApp — jos įterpia riestas kabutes, kurių Python nesupranta; rašyk tiesiai Jupyter langelyje. |
| Lietuviškos raidės kintamojo varde | `pomėgiai = [...]` | `pomegiai = [...]` | Kintamųjų varduose nenaudojame lietuviškų raidžių (ą, č, ė...) — tik `pomegiai`, be „ė“. |
| Trūksta kablelio sąraše | `["futbolas" "šunys"]` | `["futbolas", "šunys"]` | Tarp sąrašo elementų visada reikia kablelio, kitaip Python juos sulipdo į vieną žodį. |
| `NameError: name 'pomegiai' is not defined` | Paleistas 3 lygio langelis praleidus 2 lygį | Pirma paleisti 1 ir 2 lygio langelius | Paleidai langelį praleidęs ankstesnį — grįžk ir paleisk 1 ir 2 lygio langelius iš eilės. |
| `NameError` po puslapio perkrovimo, nors langeliai atrodo paleisti | JupyterLite perkrovus puslapį paleidžia naują branduolį, bet senieji rezultatai lieka matomi — atrodo, lyg viskas būtų įvykdyta | Paleisti langelius iš naujo nuo 1 lygio | Perkrovei puslapį — Python pradėjo iš naujo, nors senieji atsakymai dar matomi. Paleisk langelius iš eilės nuo 1 lygio. |

## 6. Misijos logistika

- **Klasės kodas** parašytas ant lentos **prieš** pamoką pradedant misiją —
  tas pats, kurį naudojai `poros.py --kodas` komandoje.
- **Porų lentelė** (`poros_lentele.html`) projektuojama ekrane viso misijos
  etapo metu — mokiniai patys žiūri, pas ką eiti kiekviename raunde.
- **Laikmatis** matomas visiems (telefonas, kompiuteris, net garsiai
  skaičiuojamas) — 5 min raundui.
- Kas 5 minutes garsiai sakai **„Keičiamės!“** — tai signalas eiti pas
  kitą porą iš lentelės.
- Jei kas nors baigė 1 iššūkį vėliau ir praleido raundą — `irasyk_flaga`
  priima bet kurį klasės draugą, ne tik lentelėje nurodytą, tad jis tiesiog
  prisijungia prie laisvo žmogaus.
- **Toje pačioje `pradek_misija(...)` eilutėje reikia pakeisti ir klasės
  kodą** — langelis atkeliauja su `"KLASES-KODAS"` vietoj tikro kodo. Kol jis
  nepakeistas, langelis atsako `✋ Čia dar pavyzdiniai duomenys` ir misijos
  nepradeda. Pasakyk tai garsiai, kai rodai misijos langelį: keičiami **du**
  dalykai vienoje eilutėje — vardas ir kodas.
- **Svarbu:** kiekvienas mokinys turi registruotis `pradek_misija(...)`
  **lygiai tokia pačia savo vardo rašyba, kokia parašyta projektuojamoje
  porų lentelėje** — flagas skaičiuojamas iš vardo, tad kitokia forma duos
  kitokį flagą ir draugai jo nepripažins. Diakritikai ir didžiosios/mažosios
  raidės nesvarbu (`Birutė`, `birute` ir `BIRUTE` duoda tą patį flagą), bet
  kitokia vardo forma
  (pvz. trumpinys ar pravardė vietoj pilno vardo) — jau ne. `poros.py`
  lentelę sudaro tiesiai iš `klase.txt` įrašų, tad jei mokiniai renkasi tuos
  pačius vardus, viskas sutaps automatiškai.

## 7. Saugumo aptarimas (scenarijus)

Paskutinės penkios minutės. Gali skaityti beveik pažodžiui arba kalbėti
savais žodžiais — svarbu, kad pasiektum tą pačią išvadą.

> **"Ar kas nors gavo flagą, nepakalbėjęs su tuo žmogumi?"**

Palauk atsakymo. Jei kas nors prisipažins (pvz. atspėjo flagą, pažiūrėjo į
kito ekraną, ar susigalvojo savo sprendimą) — **viešai pagirk** tą mokinį,
nesvarbu, kad tai „apgaulė“: jis ką tik įrodė esmę, kurią ir norime
parodyti.

**Jei neprisipažįsta niekas** — parodyk pats. Atsiversk notebooką savo
ekrane, naujame langelyje paleisk (`Tomas` pakeisk tikru klasės mokinio
vardu iš porų lentelės):

```python
import misija
misija.generuok_flaga("Tomas", misija._klases_kodas)
```

ir pasakyk: **„štai Tomo flagas, ir aš su juo nekalbėjau“**. `_klases_kodas`
yra tas pats kodas, kurį įrašei savo `pradek_misija(...)` langelyje, tad
rezultatas sutaps su tuo, kas rodoma Tomo ekrane — patikrink garsiai, paklausęs
Tomo. Tai ta pati demonstracija, tik be savanorio.

Tada paaiškink (arba leisk tam mokiniui paaiškinti, jei jis jau susigaudė):

> Puslapis, kuriame žaidėme, turėjo **patikrinti** jūsų flagą — ar jis
> teisingas. O jei puslapis gali *patikrinti* flagą, vadinasi, jis turi
> žinoti, **kaip jį paskaičiuoti**. O jei jis žino, kaip paskaičiuoti —
> jis gali tą patį paskaičiavimą padaryti **jums**, be jūsų draugo pagalbos.
>
> Algoritmas, kuris tai daro, yra faile `misija.py` — tame pačiame, kurį
> kiekvienas iš jūsų atsisiuntė į savo naršyklę pamokos pradžioje. Jis nėra
> paslėptas — jis tiesiog yra jūsų kompiuteryje.
>
> Štai kodėl **niekas, kas siunčiama į naršyklę, nėra paslaptis.** Viskas,
> ką naršyklė gauna — HTML, JavaScript, Python kodas — bet kuris pakankamai
> atkaklus žmogus gali perskaityti ir atkartoti.
>
> Būtent dėl to tikros sistemos (banko programėlė, el. paštas, žaidimų
> paskyra) **niekada netikrina slaptažodžio naršyklėje** — jos jį siunčia
> į serverį, ir *serveris*, kurio jūs nematote ir negalite perskaityti,
> atlieka patikrinimą. „Paslėptas“ kodas naršyklės pusėje — ne apsauga,
> o tik iliuzija.

Jei lieka laiko, gali paklausti: *„Tai ką reikėtų pakeisti, kad flagų
sistema taptų tikrai saugi?“* — teisingas atsakymas yra serveris, bet čia
jau tik papildoma mintis, ne privaloma dalis.

## 8. Kortelių skaitymas

Baigiamasis ratas — kiekvienas mokinys garsiai perskaito savo kortelę.
Klausimai/nurodymai, kuriuos gali duoti:

- „Perskaityk savo kortelę garsiai — vardą, amžių, miestą ir faktą apie
  save.“
- „Jei turi slapyvardį (3 lygis) — pasakyk ir jį, ir iš ko jis sudarytas.“
- „Ką radai savo kortelės skyriuje Bendri interesai? Su kuo ir ką bendro
  radote?“
- Jei kas nors rado slaptą temą (4 lygis) — paprašyk parodyti ir
  paklausk, kaip ją rado.
- Jei liko laiko: „Kieno kortelė šiandien labiausiai nustebino?“
