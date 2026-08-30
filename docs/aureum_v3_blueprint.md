# Aureum AI Platform V3 Blueprint

**Dokumentstatus:** Working blueprint checkpoint  
**Checkpointdato:** 29. august 2026  
**Production branch:** `main`  
**Production baseline:** `cf656f4e4c22d3dd8a04981b3177b86731e19e12`  
**V3-kode implementeret:** Nej  
**Production ændret af V3-arbejdet:** Nej

---

## 1. Formål

Dette dokument fastholder den verificerede V3-baseline, de beslutninger der allerede er låst, samt de forslag der endnu afventer godkendelse. Det skal gøre det muligt at genoptage arbejdet uden at rekonstruere beslutninger fra chat-historik.

Statusord:

- **LOCKED** — formelt accepteret V3-beslutning.
- **PROPOSED** — udarbejdet forslag, endnu ikke formelt godkendt.
- **PENDING** — endnu ikke færdigdesignet.
- **VERIFIED** — observeret direkte i production-baselinen.

---

## 2. Verificeret production-baseline

| Punkt | Status |
|---|---|
| Git branch | `main` |
| Git HEAD | `cf656f4e4c22d3dd8a04981b3177b86731e19e12` |
| Remote | `origin/main` på samme commit |
| Working tree | Ren |
| Aureum service | Aktiv |
| Main PID ved checkpoint | `538331` |
| Seneste commit | `Add disabled critical SMS alert delivery` |
| Critical SMS | Implementeret, men deaktiveret |
| Twilio credentials | Ikke installeret i production |
| V3 implementation | Ikke startet |

PID er kun et øjebliksbillede, ikke en permanent kontrakt.

---

## 3. V3-mission

Aureum V3 skal udvikle platformen fra et omfattende dashboard med mange intelligente komponenter til et sammenhængende AI-beslutningssystem.

> **Aureum V3 opdager interessante aktier, analyserer dem i dybden, forklarer potentiale og risiko, vurderer relevansen for portfolioen og følger efterfølgende, om investeringscasen udvikler sig som forventet.**

V3 skal hurtigt kunne besvare:

1. Hvad kræver opmærksomhed nu?
2. Er der opstået en ny interessant aktiemulighed?
3. Hvorfor kan aktien have potentiale?
4. Hvad kan få investeringscasen til at mislykkes?
5. Hvad betyder muligheden for portfolioen?
6. Hvor sikker er vurderingen?
7. Hvor gode og aktuelle er dataene?
8. Hvad har ændret sig siden sidste analyse?
9. Har Aureums tidligere vurderinger faktisk været gode?

Aureum må ikke love, at en aktie vil stige. Systemet skal finde situationer, hvor det målbare potentiale ser attraktivt ud i forhold til risikoen.

---

## 4. Ikke-forhandlingsbare V3-principper

- **Beslutningsværdi frem for informationsmængde.**
- **Genbrug fungerende V2-motorer; intet big-bang rewrite.**
- **Konklusioner foran AI-maskinrummet i Command Center.**
- **Ingen OpenAI- eller provider-kald ved almindelig sidevisning.**
- **Manglende data er aldrig lig nul.**
- **AI må ikke opfinde finansielle tal eller fakta.**
- **Budgetpres må reducere analysemængden, men aldrig kvalitetskravene.**
- **Portfolio Fit holdes adskilt fra aktiens objektive Opportunity Score.**
- **Telegram fortsætter som væsentlig alert-kanal. Critical SMS/Twilio forbliver disabled/out of scope.**

---

## 5. Verificeret V2-baseline

### 5.1 Aktieunivers

Production-universet indeholder:

- 1.000 aktier
- 17 lande
- 18 markeder/børser
- 13 sektorkategorier
- 500 amerikanske aktier (50 %)
- 36 danske aktier
- kun 5 aktier med ukendt sektor

### 5.2 Combined Ranking

`combined_ranking` indeholder 1.000 poster og 11 felter:

- `stock`
- `ticker`
- `currency`
- `price`
- `original_price`
- `weekly_change`
- `technical_score`
- `news_score`
- `combined_score`
- `rating`
- `ai_analysis`

`ai_analysis` findes kun for 16/1000 aktier. Ranking-laget er derfor velegnet som et billigt første filter, men er ikke en fuld fundamental Opportunity Engine.

### 5.3 Stock Screener

Stock Screener har 1.000 poster med:

- `stock`
- `ticker`
- `currency`
- `price`
- `original_price`
- `weekly_change`
- `score`

### 5.4 Instrument Master

`stock_universe.csv` har 1.000 poster med fuld dækning af:

- symbol
- navn
- ticker
- land
- marked
- valuta
- sektor
- news query
- active
- deep_ai

Filen fortsætter som canonical instrument-register.

### 5.5 Deep AI-univers

Det effektive Deep AI-univers består af 16 aktier:

- 15 faste core-aktier
- 1 personligt tilvalg: `DSV_CO`

Deep AI er overvågning af allerede valgte aktier, ikke en discovery-motor. Opportunity Radar skal derfor være et separat dynamisk lag og må ikke automatisk ændre brugerens Deep AI-valg.

### 5.6 Fundamental datadækning

Yahoo-probe på ét instrument fra hver af de 18 markeder gav:

- 18/18 markeder succesfulde
- 391/432 mulige felter
- 90,5 % samlet dækning

Testede felter omfattede bl.a.:

- market cap
- trailing/forward P/E
- price/book
- EV/EBITDA
- profit-, operating- og gross margin
- revenue/earnings growth
- ROE/ROA
- debt/equity
- current/quick ratio
- free/operating cash flow
- cash/debt
- enterprise value
- analyst target/recommendation/coverage

De hyppigste mangler var analytikerfelter på mindre europæiske markeder samt enkelte klassiske industrimetrics på finansielle selskaber. Det understøtter Yahoo som primær fundamental datakilde i V3.0, men kræver sector-aware scoring og Data Confidence.

### 5.7 Nuværende OpenAI-forbrug

Usage-loggen dækkede 15.–29. august 2026.

Seneste syv dage:

- 611 kald
- 210.070 inputtokens
- 137.025 outputtokens
- 347.095 samlede tokens
- 0 registrerede API cached-input-tokens
- 0 kald med manglende usage-data

Hele logperioden:

- 1.316 kald
- 452.363 inputtokens
- 300.158 outputtokens
- 752.521 samlede tokens

Stock News-jobbet kører hver sjette time og har application-level exact-result cache.

### 5.8 AI-budget

Foreløbig planlægningsramme:

> **Hard cap cirka 100 DKK pr. måned til Aureums samlede OpenAI-forbrug.**

Den tekniske budget-controller og modelrouting behandles i V3-D005.

---

## 6. Foreslået V3-produktstruktur

Working proposal:

| Område | Formål |
|---|---|
| Command Center | Dagens vigtigste handlinger, ændringer, risici og muligheder |
| Opportunities | Opportunity Radar, kandidater, Deep Research og High Conviction |
| Portfolio | Beholdninger, portfolio health, anbefalinger, rebalancering og Portfolio Lab |
| Research | Aktieprofiler, Stock Library, marked, nyheder og regnskaber |
| AI Intelligence | Decision quality, learning, calibration, maturity og performance |
| System | Datakvalitet, AI-forbrug, jobs, sikkerhed, backup og administration |

Command Center skal primært vise:

1. Dagens vigtigste handling
2. Bedste nye Opportunity
3. Vigtigste portfolio-handling
4. Største risiko eller kommende begivenhed
5. Markeds-, data- og AI-confidence

---

# V3-D001 — LOCKED

## 7. To separate Opportunity-spor

| Spor | Tidshorisont | Rolle |
|---|---:|---|
| **Compounder Opportunity** | 3–5 år | Primært/default spor |
| **Catalyst Opportunity** | 3–18 måneder | Sekundært spor |

### Compounder

Fokus på:

- holdbar omsætnings- og indtjeningsvækst
- stærke eller forbedrede marginer
- sund balance
- stabilt cash flow
- kapitalafkast
- konkurrencemæssige fordele
- rimelig valuation relativt til kvalitet og vækst
- en case der kan holde gennem flere markedsperioder

Kortvarigt svagt momentum må ikke automatisk diskvalificere en stærk Compounder.

### Catalyst

Fokus på konkrete ændringer, der kan flytte markedets forventninger inden for 3–18 måneder:

- estimatrevisioner
- regnskabs-/guidanceændringer
- produktlanceringer
- regulatoriske beslutninger
- turnaround
- marginforbedring
- sektorændringer
- re-rating
- momentum/volumenbekræftelse

Et Catalyst-signal må ikke fremstilles som en langsigtet kvalitetsinvestering uden separat Compounder-evidens.

### Adskillelse

De to spor får separate:

- scoremodeller
- confidence-vurderinger
- High-Conviction-grænser
- Deep Research-rapporter
- alerts
- outcome-perioder

Samme aktie kan kvalificere sig i begge spor.

Outcome tracking:

- Catalyst: 1, 3, 6, 12, 18 måneder
- Compounder: 6, 12, 24, 36, 60 måneder

---

# V3-D002 — LOCKED

## 8. Scoring, Confidence og High-Conviction-gates

### 8.1 Tre separate vurderinger

| Værdi | Besvarer |
|---|---|
| Compounder/Catalyst Score | Hvor attraktiv ser aktien objektivt ud? |
| AI Confidence | Hvor robust og sammenhængende er investeringscasen? |
| Data Confidence | Hvor komplette, aktuelle og konsistente er dataene? |

AI Confidence må aldrig kompensere for dårlig Data Confidence.

### 8.2 Compounder Score

| Komponent | Vægt |
|---|---:|
| Kvalitet og indtjeningsevne | 25 |
| Holdbar vækst | 20 |
| Valuation | 20 |
| Finansiel robusthed | 15 |
| Cash flow og kapitaludnyttelse | 10 |
| Markedsbekræftelse | 5 |
| Katalysatorer og forventningsstøtte | 5 |
| **I alt** | **100** |

### 8.3 Catalyst Score

| Komponent | Vægt |
|---|---:|
| Katalysatorens styrke og tydelighed | 25 |
| Fundamental forbedring/vendepunkt | 20 |
| Forventnings- og estimatændringer | 15 |
| Momentum og markedsbekræftelse | 15 |
| Valuation/re-rating | 10 |
| Risk/reward-asymmetri | 10 |
| Nyheder og sentiment | 5 |
| **I alt** | **100** |

### 8.4 Sector-aware profiler

V3.0 får mindst:

1. General Companies
2. Financial Services
3. Real Estate
4. Utilities/Energy

Financial Services må fx ikke straffes automatisk for manglende FCF/current ratio/quick ratio/EV-EBITDA, når disse metrics ikke er relevante.

Tidlig biotech/pre-revenue må gerne findes af Radar, men får ikke automatisk High Conviction i V3.0 uden senere specialmodel.

### 8.5 Manglende data

Aureum skal:

1. markere metric `N/A`
2. angive årsagen
3. renormalisere relevante vægte
4. reducere Data Confidence
5. blokere High Conviction ved kritiske datamangler

En score kan normalt beregnes, når mindst cirka 70 % af relevant vægt er dækket.

### 8.6 Data Confidence

| Faktor | Vægt |
|---|---:|
| Datadækning | 40 |
| Aktualitet | 30 |
| Konsistens | 20 |
| Anomali/outlier-kontrol | 10 |

Fortolkning:

- <60: utilstrækkelige data
- 60–74: kun overvågning
- 75–84: kandidat kan vurderes
- 85–100: gate-egnet til Compounder High Conviction
- Catalyst kan være gate-egnet fra 80

### 8.7 Kandidatniveauer

Compounder:

- <60: lav prioritet
- 60–69: Monitor
- 70–79: Candidate
- 80–84: Strong Candidate
- 85–100: High-Conviction-eligible

Catalyst:

- <60: lav prioritet
- 60–69: Monitor
- 70–79: Candidate
- 80–87: Strong Candidate
- 88–100: High-Conviction-eligible

### 8.8 Compounder High-Conviction-gate

Som minimum:

- Compounder Score ≥85
- AI Confidence ≥80
- Data Confidence ≥85
- Quality ≥75
- Financial Strength ≥65
- Valuation ≥55
- ingen kritiske balance-/data-/governance-red flags
- Deep Research gennemført
- uafhængig AI second opinion uden væsentlig modsigelse
- score/tese bekræftet i mindst to kørsler med cirka 72 timers afstand
- casen må ikke afhænge af ét enkelt nøgletal

### 8.9 Catalyst High-Conviction-gate

Som minimum:

- Catalyst Score ≥88
- AI Confidence ≥82
- Data Confidence ≥80
- konkret, tidsafgrænset, kildeunderstøttet katalysator
- mindst to uafhængige evidenstyper
- positiv markedsbekræftelse eller dokumenteret ændring i forventninger
- udløbsdato
- thesis-invalidation-kriterier
- Deep Research
- uafhængig second opinion

En pludselig begivenhed kan få status `Provisional Catalyst Opportunity`, men ikke High Conviction uden ny uafhængig bekræftelse.

### 8.10 AI'ens rolle

AI må ikke frit ændre den objektive score. AI bruges til:

- sammenhæng og forklaring
- modargumenter
- nyheder og katalysatorer
- bull/base/bear case
- thesis-invalidation
- AI Confidence
- second opinion

### 8.11 Portfolio Fit

Portfolio Fit vurderes separat efter aktiekvaliteten, fx:

- ny potentiel position
- allerede ejet
- mulig forøgelse
- sektor-/enkeltaktiekoncentration
- overlap
- valuta-/markedsrisiko

Portfolio Fit ændrer ikke Compounder/Catalyst Score.

---

# V3-D003 — LOCKED

## 9. Opportunity-livscyklus

```text
SCREENED
   ↓
MONITOR
   ↓
CANDIDATE
   ↓
STRONG_CANDIDATE
   ↓
DEEP_RESEARCH
   ↓
HIGH_CONVICTION
```

Supplerende tilstande:

- `DATA_HOLD`
- `REJECTED`
- `EXPIRED`
- `THESIS_BROKEN`

### SCREENED

Grundlæggende krav er bestået; ingen OpenAI.

### MONITOR

Interessante tegn, men utilstrækkelig evidens. Følges i baggrunden uden alert.

### CANDIDATE

Typisk score 70–79, Data Confidence ≥70, ingen kritiske red flags og mindst to positive komponenter.

### STRONG_CANDIDATE

- Compounder 80–84 eller Catalyst 80–87
- Data Confidence ≥75
- tydelig case
- ingen alvorlig konflikt mellem fundamentals, momentum og risiko

Prioriteres til Deep Research.

### DEEP_RESEARCH

Arbejdsstatus, ikke kvalitetsstempel. Startes kun når budget, freshness og input-hash tillader det.

Kan ende i High Conviction, Strong Candidate, Monitor, Rejected eller Data Hold.

### HIGH_CONVICTION

Kræver alle D002-gates. High Conviction er den eneste normale opportunity-status, der udløser en ny opportunity-alert via Telegram.

### DATA_HOLD

Ved manglende, modstridende, forældede data, post-earnings refresh eller providerfejl. Ikke en negativ vurdering.

### REJECTED

Ved fx uacceptabel valuation, svag balance, lav indtjeningskvalitet, ikke-understøttet katalysator eller dårlig risk/reward.

### EXPIRED

Primært Catalyst: event/katalysator er passeret eller ikke længere relevant.

### THESIS_BROKEN

Ved fx guidance cut, fundamental forværring, mislykket katalysator, gælds-/likviditetsproblem eller brud på invalidationskriterier. Kan udløse Telegram, især for portfolio-aktier.

### Stabilitet/støj

- <3 point: støj
- 3–7 point: registreres normalt uden ny AI-analyse
- ≥8 point: kan udløse revurdering
- væsentlig ny begivenhed kan tilsidesætte pointgrænsen
- High Conviction kræver normalt to separate bekræftelser
- jobs må aldrig skabe dublerede alerts

### Nyt AI-kald er kun berettiget ved

- væsentligt ændret input-hash
- nye finansielle resultater
- væsentlig nyhed/katalysator
- markant scoreændring
- udløbet rapport
- thesis-invalidation
- manuel Deep Research

### Alert-hierarki

| Begivenhed | Opportunities | Command Center | Telegram |
|---|---:|---:|---:|
| Monitor | Nej | Nej | Nej |
| Candidate | Ja | Normalt nej | Nej |
| Strong Candidate | Ja | Bedste kandidater | Nej |
| Deep Research færdig | Ja | Ved høj relevans | Normalt nej |
| High Conviction | Ja | Ja | Ja |
| Thesis styrket væsentligt | Ja | Ja | Eventuelt |
| Thesis Broken | Ja | Ja | Ja |
| Data Hold | Ja | Kun ved høj relevans | Kun ved kritisk portfolio-relevans |

---

# V3-D004 — PROPOSED / PENDING APPROVAL

## 10. Datakontrakt, caching og opdateringsfrekvens

D004 er udarbejdet, men endnu ikke formelt godkendt.

### 10.1 Seks datalag

| Lag | Indhold |
|---|---|
| Instrument Master | Symbol, ticker, navn, land, børs, valuta, sektor |
| Market Data | Pris, historik, afkast, volumen, momentum |
| Fundamental Data | Vækst, marginer, valuation, balance, cash flow |
| Events & News | Nyheder, regnskaber, katalysatorer |
| Opportunity Intelligence | Scores, status, red flags, datakvalitet |
| AI Research | Candidate Review, Deep Research, second opinion |

Lagene opdateres uafhængigt.

### 10.2 Fælles snapshot-kontrakt

Mindst:

- `schema_version`
- `symbol`
- `provider`
- `provider_symbol`
- `observed_at`
- `retrieved_at`
- `valid_until`
- `freshness_status`
- `data_status`
- `input_hash`
- `fields`
- `missing_fields`
- `warnings`

Freshness: `FRESH`, `AGING`, `STALE`.

Data status: `COMPLETE`, `PARTIAL`, `ERROR`.

Manglende-data-årsager:

- `NOT_PROVIDED`
- `NOT_APPLICABLE`
- `PROVIDER_ERROR`
- `STALE`
- `INVALID_VALUE`

### 10.3 Foreslåede frekvenser

Instrument Master:

- daglig validering
- enrichment primært ved mangler

Market Data:

- hele universet efter relevant markedslukning
- portfolio/Deep AI/High Conviction hyppigere i åbningstiden
- 1/3/6/12 måneders momentum dagligt
- relativ styrke mod sektor/marked dagligt

Fundamentals, prioritet:

1. Portfolio og High Conviction
2. Strong Candidates
3. Deep AI
4. Candidates
5. Resten round-robin

Foreslået rytme:

- portfolio/High Conviction: hver 1–3 dag
- Strong Candidates: cirka hver 3. dag
- Deep AI: ugentligt
- hele universet: ugentligt round-robin
- tvungen refresh efter regnskab

Nyheder:

- portfolio/High Conviction: cirka hver 2. time
- Catalyst Candidates: cirka hver 2.–3. time
- Deep AI: eksisterende 6-timers rytme
- Compounder Candidates: cirka hver 6.–12. time
- ingen individuel OpenAI-analyse af alle 1.000

Opportunity:

- Compounder Universe Scan: dagligt
- Catalyst Mini Scan: hver 6. time
- fuldt Catalyst Scan: dagligt
- Candidate Review: højst dagligt ved ændrede input
- Deep Research: eventdrevet
- second opinion: kun tæt på High-Conviction-gate

Frekvenser skal valideres i shadow mode.

### 10.4 AI-rapporters gyldighed

Compounder Deep Research:

- normal maksimal TTL: 14 dage
- tidligere invalidation ved regnskab, væsentlig dataændring, større nyhed, scoreændring eller thesis-brud

Catalyst Deep Research:

- normal maksimal TTL: 72 timer
- tidligere invalidation ved ændret katalysator/guidance/estimat, markant kurs-/volumenbevægelse eller eventets indtræden

Samme input-hash + prompt-kontrakt + modelversion skal normalt give cache-hit.

### 10.5 Freshness-gates

High Conviction kræver bl.a.:

- fundamentals opdateret efter seneste offentliggjorte regnskab
- ingen ventende post-earnings refresh
- kritiske datakilder `FRESH`
- relevante events/news kontrolleret
- Data Confidence over D002-grænsen

Weekender og helligdage må ikke fejlagtigt gøre sidste handelsdags data stale.

### 10.6 Provider-strategi

V3.0 starter med:

- Yahoo som primær fundamental-kilde
- eksisterende provider-lag til pris/historik/metadata
- EODHD kun som dokumenteret fallback for eksisterende kontrakter

Ved Yahoo-fejl:

1. behold sidste valide snapshot
2. markér `AGING`/`STALE`
3. reducer Data Confidence
4. retry med backoff
5. blokér High-Conviction-promovering ved kritisk stale data
6. lad resten af batchen fortsætte

### 10.7 Raw og normaliserede data

```text
Raw provider snapshot
        ↓
Validation
        ↓
Normalized snapshot
        ↓
Sector-aware features
        ↓
Opportunity Score
```

Forslag:

- rå snapshots komprimeret 30–90 dage
- normaliserede snapshots langsigtet
- Deep Research-inputpakke gemmes sammen med rapporten

### 10.8 Historik

Immutable snapshots skal understøtte:

- vækstacceleration
- marginudvikling
- gældsreduktion
- valuationændring
- scoreændring
- signalstabilitet
- thesis-forbedring/-forværring

### 10.9 Valuta

Monetære felter bør bevare:

- native value
- native currency
- normalized value
- base currency
- FX observed at

### 10.10 Concurrency/integritet

V3 skal bruge:

- SQLite-transaktioner
- idempotente writes
- relevante locks
- unikke snapshot-/input-hash-nøgler
- atomic file writes ved JSON-caches
- temp-fil, flush, `fsync`, rename
- sikker genstart efter afbrudte jobs

### 10.11 Foreslåede acceptance criteria

- samme input/kontrakt giver samme lokale score
- `N/A` bliver aldrig nul
- sektor-irrelevante felter giver ikke straf
- centrale værdier har kilde/timestamp
- providerfejl bevarer sidste valide snapshot
- én fejlende aktie stopper ikke batchen
- concurrent jobs overskriver ikke hinanden
- sidevisning giver nul eksterne data-/AI-kald
- nyt regnskab invaliderer relevant cache
- uændrede AI-input giver cache-hit
- High Conviction blokeres ved kritisk stale data
- 1.000 aktier kan opdateres uden ukontrollerede burst-kald
- Deep Research kan reproduceres fra gemt inputpakke

---

## 11. Opportunity Radar — working architecture

| Trin | Omfang | OpenAI |
|---|---:|---:|
| Universe Scan | ~1.000 | Ingen |
| Eligibility Filter | ~150–250 | Ingen |
| Fundamental Intelligence | ~50–100 | Ingen |
| Opportunity Scoring | ~20–30 | Ingen |
| AI Candidate Review | ~10–15 | Billigt/struktureret |
| Deep Stock Research | ~3–5 | Stærkere model |
| Independent Second Opinion | ~0–3 | Premium/selektivt |
| Alert & Tracking | Kun godkendte cases | Begrænset |

Tallene kalibreres i shadow mode.

Deep Research skal mindst indeholde:

- hvorfor aktien blev opdaget
- hvad markedet muligvis undervurderer
- finansielle styrker/svagheder
- valuation
- vækst/marginer
- cash flow/balance
- katalysatorer
- risici
- bull/base/bear case
- thesis-invalidation
- Compounder Score
- Catalyst Score
- AI Confidence
- Data Confidence
- tidshorisont
- dataenes dato
- næste relevante event

---

## 12. Foreløbig V2-reuse-map

| Eksisterende område | V3-retning |
|---|---|
| Stock Universe | REUSE |
| Stock Screener | REUSE som tidligt filter |
| Combined Score | REUSE, ikke endelig Opportunity Score |
| Yahoo-provider | EXTEND med provider-neutral fundamental kontrakt |
| Stock News cache | REUSE og senere strukturere output |
| Deep AI core/personlige valg | REUSE |
| Portfolio Manager | REUSE |
| Portfolio Lab | REUSE |
| Portfolio Intelligence | REUSE og konsolider i UI |
| Decision Learning | BACKGROUND + AI Intelligence |
| Adaptive Intelligence | BACKGROUND + AI Intelligence |
| AI Maturity | BACKGROUND + AI Intelligence |
| Dashboard cache | GRADVIS REFACTOR |
| Alerts/Telegram | REUSE |
| Accounts/authorization/MFA | REUSE uændret |
| Backup/audit | REUSE uændret |
| Critical SMS | DISABLED / OUT OF SCOPE |
| Historiske/dublerede routes | LEGACY indtil feature-paritet |

---

## 13. Foreslået ny kodeorganisation

V3 bør undgå unødig yderligere fragmentering.

Foreløbige moduler:

- `opportunity_data_service.py`
- `opportunity_engine.py`
- `opportunity_research_service.py`
- `opportunity_store.py`
- `opportunity_routes.py`
- `ai_budget_policy_service.py`

Foreløbige UI-filer:

- `templates/opportunities.html`
- `templates/opportunity_detail.html`
- `static/css/opportunities.css`

Opportunity Store bør bruge separat SQLite med transaktioner og concurrency-sikre writes.

Centrale records:

- scan runs
- candidates
- score components
- snapshots
- research reports
- thesis versions
- alerts
- status changes
- subsequent price performance
- outcomes

---

## 14. Foreslået migrationsplan

### Fase 1 — Blueprint og kontrakter

- lås V3-scope
- færdiggør D004
- definér modelrouting/budget-controller
- ingen productionændring

### Fase 2 — Fundamental Data Foundation

- provider-neutral fundamental kontrakt
- raw/normalized snapshots
- batch refresh
- Data Confidence
- sector profiles

### Fase 3 — Opportunity Engine i shadow mode

- ingen alerts
- ingen automatisk High Conviction
- gem scores/historik
- mål datamangler/stabilitet
- sammenlign med eksisterende ranking

### Fase 4 — Deep Research beta

- manuel Deep Research
- budget-controller
- strukturerede rapporter
- second opinion
- ingen automatisk alert i starten

### Fase 5 — Opportunities-side

- kandidatoversigt
- scoreforklaring
- Deep Research
- thesis-status
- historik/outcomes

### Fase 6 — Alerts

- High-Conviction-gates
- Telegram
- cooldown/dedup
- Thesis Broken-alerts

### Fase 7 — Command Center V3

- nyt executive cockpit
- konsolider V2-cards
- behold V2-sider under overgang

### Fase 8 — Kontrolleret oprydning

Legacy pensioneres først efter dokumenteret feature-paritet og rollback-test.

---

## 15. Foreløbige production-acceptance criteria

V3 er først production-klar når:

- V2 fungerer uændret under udviklingen
- V3 er bag feature flag eller separat route
- sidevisninger starter ingen eksterne kald
- 100 DKK hard cap håndhæves teknisk
- sector-aware scoring fungerer
- manglende data vises ærligt
- opportunities viser risiko/thesis-invalidation
- alerts er idempotente/deduplikerede
- AI-vurderinger har input-hash/kontraktversion
- Deep Research kan reproduceres
- outcome tracking fungerer
- concurrency-tests er bestået
- shadow mode har kørt længe nok til kalibrering
- rollback kan gennemføres uden tab af V2-data

---

## 16. Åbne beslutninger

### V3-D004

**Status:** PROPOSED / PENDING APPROVAL

Datakontrakt, caching, freshness, provider-adfærd og opdateringsfrekvens skal godkendes eller justeres.

### V3-D005

**Status:** PENDING

Skal definere:

- modelrouting
- research-kontrakter/outputformater
- budget-controller
- prisestimering før kald
- prioritering ved budgetpres
- soft target/warning/critical/hard cap
- model-/promptversionsstyring

Aktuelle modelnavne og priser verificeres mod officiel OpenAI-dokumentation på implementeringstidspunktet.

### V3-D006

**Status:** PENDING

Opportunity Store/databasekontrakt:

- tabeller
- idempotency keys
- constraints
- retention
- migrations
- concurrency
- backup/restore

### V3-D007

**Status:** PENDING

Opportunities UX:

- oversigt
- filtre
- detailrapport
- scoreforklaring
- confidence
- timeline
- portfolio fit
- alert-historik

### V3-D008

**Status:** PENDING

Shadow mode/kalibrering:

- varighed
- benchmark
- false positives
- scorestabilitet
- outcome-måling
- kriterier for aktivering af alerts

### V3-D009

**Status:** PENDING

Command Center V3 og samlet informationsarkitektur.

---

## 17. Genoptagelsespunkt

Ved næste arbejdssession:

1. Kontrollér Git HEAD og ren worktree.
2. Gennemgå V3-D004.
3. Godkend eller justér D004.
4. Fortsæt med V3-D005 om AI-modelrouting og budget-controller.
5. Implementér ingen V3-kode, før de nødvendige kontrakter er låst.

---

## 18. Checkpointkonklusion

Ved dette checkpoint er:

- V3-D001 låst
- V3-D002 låst
- V3-D003 låst
- V3-D004 udarbejdet, men ikke låst
- 100 DKK/måned aftalt som planlægningsmæssigt maksimum
- Opportunity Radar defineret som V3’s vigtigste nye funktion
- ingen V3-kode implementeret
- production ikke ændret
