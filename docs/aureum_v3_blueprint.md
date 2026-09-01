# Aureum AI Platform V3 Blueprint

**Dokumentstatus:** Working blueprint checkpoint  
**Checkpointdato:** 1. september 2026  
**Production branch:** `main`  
**Production baseline:** `d75816f4ab438ef47dcf3b1db9aa22055f98176b`  
**V3-kode implementeret:** Nej  
**Production runtime ændret af V3-arbejdet:** Nej

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
| Production-baseline Git HEAD | `d75816f4ab438ef47dcf3b1db9aa22055f98176b` |
| Remote ved production-baseline-checkpoint | `origin/main` på `d75816f4ab438ef47dcf3b1db9aa22055f98176b` |
| Working tree ved production-baseline-checkpoint | Ren |
| Aureum service | Senest verificeret aktiv 29. august; ikke genstartet/deployeret af V3-blueprintarbejdet |
| Main PID ved 29. august-checkpoint | `538331` |
| Seneste production-baseline commit | `Lock V3-D006 persistence and database contracts` |
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

# V3-D004 — LOCKED

## 10. Datakontrakt, caching og opdateringsfrekvens

D004 er formelt godkendt og låst. Ændringer kræver en ny V3-beslutning og må ikke indføres stiltiende under implementeringen.

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

### 10.2 Snapshot-, provenance- og freshness-kontrakt

Snapshots, inputpakker og afledte vurderinger er immutable. En rettelse,
renormalisering eller re-evaluering opretter en ny record og overskriver
aldrig den oprindelige.

Fælles snapshot-envelope:

- `schema_version`
- `snapshot_id`
- `snapshot_kind`: `PROVIDER` eller `NORMALIZED`
- `instrument_id`
- `data_layer`
- `data_subtype`
- `symbol`
- `observed_at`
- `created_at`
- `data_status`
- `content_hash`
- `fields`
- `missing_fields`
- `warnings`

`instrument_id` er Aureums stabile interne identitet. Symbol, ticker og
provider-symboler er tidsafgrænsede aliases i Instrument Master og må
ikke bruges som eneste identitet. Et snapshots `symbol` er den alias,
der var gældende ved `observed_at`; historiske aliases overskrives ikke.

`data_subtype` er den mindste freshness-homogene enhed. Felter med
væsentligt forskellige observationstidspunkter eller freshness-regler
skal opdeles i separate snapshots. For et normaliseret snapshot er
`observed_at` det fælles effektive observationstidspunkt for den
pågældende subtype; kildespecifikke tidspunkter bevares i
`field_provenance`.

Provider-snapshots indeholder desuden mindst:

- `retrieval_attempt_id`
- `provider`
- `provider_symbol`
- `retrieved_at`
- `raw_payload_ref`
- `raw_payload_hash`

Normaliserede snapshots indeholder desuden mindst:

- `normalization_version`
- `normalized_at`
- `source_snapshot_ids`
- `source_set_hash`
- `field_provenance`

For hvert felt, der indgår i score, gate eller AI-input, skal
`field_provenance` mindst vise kilde-snapshot, kildefelt, kildens
`observed_at` og anvendt `transformation_id`. Afledte felter refererer
til alle væsentlige inputfelter.

Score-, gate- og research-input samles i immutable inputpakker med mindst:

- `input_package_id`
- `purpose`
- `contract_version`
- `created_at`
- `snapshot_ids`
- `freshness_assessment_ids`
- `policy_versions`
- `input_hash`

Uændrede input genbruger den eksisterende inputpakke via et scoped
`input_hash` frem for at skabe semantiske dubletter.

Freshness-kontekst gemmes som en immutable record med mindst:

- `freshness_context_id`
- `as_of`
- `calendar_snapshot_ids`
- `event_snapshot_ids`
- `context_hash`

En immutable freshness-vurdering indeholder mindst:

- `freshness_assessment_id`
- `snapshot_id`
- `evaluated_at`
- `valid_until`
- `stale_after`
- `freshness_status`
- `freshness_policy_version`
- `freshness_context_id`
- `reason_codes`

En re-evaluering opretter en ny freshness-vurdering og ændrer aldrig
snapshotet. Den aktuelle status er den seneste gyldige vurdering for
snapshotet og den aktive policy.

Freshness:

- `FRESH`: `evaluated_at` er senest `valid_until`, og ingen kendt
  invaliderende begivenhed er indtruffet
- `AGING`: `valid_until` er passeret, men `evaluated_at` er senest
  `stale_after`, og ingen kendt invaliderende begivenhed er indtruffet
- `STALE`: `stale_after` er passeret, en kendt invaliderende begivenhed
  er indtruffet, eller kildedata udtrykkeligt er markeret som forældede

`valid_until` og `stale_after` beregnes deterministisk ud fra
`observed_at`, datalag/datasubtype, relevante kalender- og
event-snapshots samt den versionerede freshness-policy. `retrieved_at`
må aldrig gøre en gammel observation frisk.

Samme snapshot, freshness-policyversion, `evaluated_at` og immutable
freshness-kontekst skal give samme freshness-status.

Data status: `COMPLETE`, `PARTIAL`, `ERROR`.

`PARTIAL` beskriver snapshotets samlede fuldstændighed, men afgør ikke
alene en High-Conviction-gate. Kritikalitet afgøres på normaliseret
felt-/datasubtype-niveau af den aktive gate-policy.

Manglende-data-årsager:

- `NOT_PROVIDED`
- `NOT_APPLICABLE`
- `PROVIDER_ERROR`
- `STALE`
- `INVALID_VALUE`

### 10.3 Konfigurerbare startfrekvenser

Frekvenserne nedenfor er godkendte startværdier og -intervaller til
shadow mode. For hvert job vælger den aktive, versionerede
`schedule_policy` én entydig kørselsrytme eller trigger inden for den
angivne ramme.

En `schedule_policy` indeholder mindst:

- `schedule_policy_version`
- `job_type`
- `effective_from`
- `timezone`
- `market_calendar_id`, når relevant
- `active_window`
- `cadence_or_trigger`
- `jitter`
- `catch_up_policy`

`Dagligt`, `markedslukning` og handelsvinduer fortolkes efter den
relevante børs-/markedskalender og tidszone. Tidsbaserede intervaller
skal angive, om de gælder som wall-clock-tid eller kun inden for et
aktivt handels-/overvågningsvindue.

Hver jobkørsel gemmer mindst `schedule_policy_version`, `planned_for`,
`trigger_type`, `started_at` og `finished_at`. Frekvenser og
triggerregler må ikke hardcodes i services eller routes.

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

Startfrekvenser:

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

Startfrekvenserne skal valideres i shadow mode. En justering inden
for en låst ramme kræver en ny `schedule_policy_version` og en
auditerbar begrundelse. En ændring uden for rammen eller en ændring,
der svækker freshness- eller High-Conviction-gates, kræver en ny
V3-beslutning.

Eventdrevne og manuelle kørsler skal følge samme idempotency-,
concurrency- og auditkrav og må ikke skabe dubleret arbejde.

### 10.4 AI-rapporters identitet, caching og gyldighed

AI-rapporter og generationsforsøg er immutable. En færdig AI-rapport
indeholder mindst:

- `research_report_id`
- `instrument_id`
- `opportunity_id`, når relevant
- `report_type`: `CANDIDATE_REVIEW`, `DEEP_RESEARCH` eller
  `SECOND_OPINION`
- `research_role`: `PRIMARY` eller `INDEPENDENT_SECOND_OPINION`
- `input_package_id`
- `prompt_contract_version`
- `model_provider`
- `requested_model_id`
- `resolved_model_id`
- `model_resolution_status`: `EXACT`, `ALIAS_ONLY` eller
  `NOT_PROVIDED`
- `model_route_decision_id`
- `model_route_policy_version`
- `effective_route_hash`
- `generation_contract_hash`
- `response_contract_version`
- `report_validity_policy_version`
- `generated_at`
- `normal_valid_until`
- `output_hash`
- `generation_attempt_id`
- `provider_response_id`, når tilgængelig
- `evidence_input_hash`, kun ved second opinion
- `independence_policy_version`, kun ved second opinion

`resolved_model_id` skal være den mest præcise modelidentitet, som
provideren returnerer. Feltet er post-generation auditmetadata og må
ikke kræves kendt ved et pre-call cache-opslag.

Når provideren kun returnerer en bevægelig alias eller ingen særskilt
modelversion, registreres dette ærligt i `model_resolution_status`.
Aureum må da kun love reproduktion af input, kontrakter og routingvalg,
ikke et bit-identisk nyt modelsvar.

`model_route_policy_version` identificerer reglerne, mens
`model_route_decision_id` identificerer den konkrete immutable
routing- og budgetbeslutning.

`effective_route_hash` dækker den outputpåvirkende pre-call-rute,
herunder provider, endpoint, requested model og relevante
modelkapabiliteter. En ny routingpolicy skaber kun et nyt cache-scope,
når den effektive rute eller en anden outputpåvirkende kontrakt faktisk
ændres.

`generation_contract_hash` dækker alle øvrige outputpåvirkende
indstillinger, herunder promptskabeloner, tool-kontrakter, outputschema
og relevante genereringsparametre.

Et pre-call AI-cache-scope identificeres mindst af:

- `report_type`
- `research_role`
- inputpakkens `input_hash`
- `prompt_contract_version`
- `effective_route_hash`
- `generation_contract_hash`
- `response_contract_version`
- `independence_policy_version`, når det er en second opinion

`model_route_policy_version` og den konkrete route-decision gemmes til
audit, men en rent administrativ policyændring må ikke alene skabe et
dyrt cache-miss.

Den faktisk returnerede `resolved_model_id` gemmes på rapporten efter
kaldet og bruges til audit, kalibrering og post-generation analyse, men
er ikke en nødvendig pre-call cache-nøgle.

En `INDEPENDENT_SECOND_OPINION` kræver mindst:

- et særskilt `generation_attempt_id` og `research_report_id`
- isoleret modelkontekst og en særskilt second-opinion-promptkontrakt
- samme væsentlige evidensgrundlag som den primære rapport
- et `evidence_input_hash`, der dokumenterer evidensgrundlaget
- ingen primær konklusion, anbefaling, AI Confidence eller færdig rapport
  i modelinputtet før second opinion er genereret
- den model-/provider-uafhængighed, som den aktive D005-policy kræver

Sammenligning sker først efter, at begge immutable rapporter eksisterer,
og gemmes i en separat immutable reconciliation-record med mindst:

- `research_reconciliation_id`
- `primary_report_id`
- `second_opinion_report_id`
- `evaluated_at`
- `reconciliation_policy_version`
- `alignment_status`: `ALIGNED`, `MATERIAL_CONTRADICTION` eller
  `INCONCLUSIVE`
- `contradiction_codes`
- `comparison_output_hash`

Reconciliation må ikke ændre nogen af rapporterne. D002-kravet om en
second opinion uden væsentlig modsigelse er kun opfyldt ved en aktuel,
gyldig reconciliation med `alignment_status = ALIGNED`.
`MATERIAL_CONTRADICTION` og `INCONCLUSIVE` blokerer High Conviction.

Kun komplette, schema-valide rapporter må fungere som positive
cache-resultater. Fejlede eller ufuldstændige generationsforsøg må ikke
genbruges som en gyldig rapport.

Et cache-hit genbruger den eksisterende rapport og må ikke:

- nulstille `generated_at` eller `normal_valid_until`
- tælle som en ny separat kørsel
- tælle som en ny uafhængig second opinion
- tælle som D002's nye bekræftelse efter cirka 72 timer
- skabe en ny lifecycle-overgang eller alert

Et cache-hit på en fortsat gyldig, tidligere uafhængigt genereret
second opinion kan bruges i en ny reconciliation med en aktuel
primærrapport, når evidensgrundlag og independence-policy fortsat
matcher. Det må aldrig fremstilles som en ny uafhængig generation eller
en ny tidsmæssig bekræftelse.

Rapportgyldighed vurderes separat i immutable records med mindst:

- `report_validity_assessment_id`
- `research_report_id`
- `evaluated_at`
- `report_validity_policy_version`
- `freshness_context_id`
- `evaluated_against_input_package_id`
- `validity_status`: `VALID`, `EXPIRED` eller `INVALIDATED`
- `reason_codes`

En ny vurdering overskriver aldrig rapporten eller tidligere
gyldighedsvurderinger.

Compounder Deep Research:

- normal maksimal TTL: 14 dage
- tidligere invalidation ved nyt regnskab, væsentlig dataændring, større
  nyhed, relevant scoreændring eller thesis-brud

Catalyst Deep Research:

- normal maksimal TTL: 72 timer
- tidligere invalidation ved ændret katalysator, guidance eller estimat,
  markant kurs-/volumenbevægelse eller eventets indtræden

En second opinions `normal_valid_until` må ikke ligge senere end den
relevante profils Deep-Research-TTL eller gyldigheden af dens kritiske
input.

En reconciliation er kun gate-gyldig, mens både primærrapporten, second
opinion, evidensgrundlaget og den anvendte independence-policy er
gyldige.

`EXPIRED` bruges, når `normal_valid_until` er passeret uden en
tidligere materiel invalidation. `INVALIDATED` bruges ved en konkret
data-, event-, thesis- eller policyændring, der gør rapporten uegnet til
den aktuelle gate.

En rapport invalideres desuden, når:

- en nyere kritisk inputpakke ændrer investeringscasen væsentligt
- et kritisk input bliver `AGING`, `STALE`, ugyldigt eller utilgængeligt
- den aktive kontrakt- eller gate-policy kræver en ny vurdering
- et eksplicit thesis-invalidation-kriterium bliver opfyldt

En udløbet eller invalideret rapport bevares som historik, men må ikke
bruges til at passere en aktuel High-Conviction-gate. Udløb eller
invalidation udløser ikke automatisk et nyt OpenAI-kald; D003's
kalderegler og D005's budget-controller skal begge tillade kørslen.

### 10.5 Opportunity-semantik, freshness- og High-Conviction-gates

Datakontrakten skelner mellem:

- `opportunity_profile`: `COMPOUNDER` eller `CATALYST`
- `lifecycle_status`: præcis én af tilstandene låst i D003
- `qualification_labels`: nul eller flere supplerende labels

D002-betegnelsen `Provisional Catalyst Opportunity` normaliseres som
label-koden `PROVISIONAL_CATALYST_OPPORTUNITY`. Det er ikke en ekstra
lifecycle-status.

Labelen må ikke alene:

- udløse Telegram
- tælle som High Conviction
- omgå Deep Research
- omgå uafhængig second opinion
- omgå øvrige D002- eller D003-gates

High Conviction evalueres med en versioneret `gate_policy` separat for
Compounder og Catalyst. Gate-policyen indeholder mindst:

- `gate_policy_version`
- `effective_from`
- `opportunity_profile`
- `target_status`
- `decision_contract_refs` for de låste D002- og D003-kontrakter
- `allowed_source_statuses`
- `critical_input_rules`
- `freshness_and_coverage_rules`
- `report_and_reconciliation_rules`
- `confirmation_policy`
- `gate_validity_rule`
- `reason_code_contract_version`

Kritikalitet defineres på normaliseret felt-/datasubtype-niveau og må
ikke bindes til navnet på én bestemt provider, når samme godkendte
normaliserede kontrakt kan opfyldes fra en anden kilde.

Hver gate-evaluering er immutable og side-effect-fri og indeholder
mindst:

- `gate_evaluation_id`
- `opportunity_id`
- `instrument_id`
- `opportunity_profile`
- `lifecycle_status_before`
- `target_status`
- `execution_mode`: `SHADOW` eller `LIVE`
- `evaluated_at`
- `gate_valid_until`
- `freshness_context_id`
- `gate_policy_version`
- `decision_contract_refs`
- `input_package_id`
- `score_assessment_ids`
- `report_validity_assessment_ids`
- `research_reconciliation_id`, når krævet
- `confirmation_evidence_ids`
- `gate_basis_hash`
- `data_confidence`
- `checks`
- `result`: `PASS`, `FAIL` eller `BLOCKED_DATA`
- `reason_codes`

Hvert element i `checks` skal mindst indeholde check-kode, resultat og
referencer til den immutable evidens, der blev anvendt.

`gate_basis_hash` dækker inputpakken, scores, rapportgyldighed,
reconciliation, bekræftelser, freshness-kontekst og samtlige anvendte
beslutnings-, kontrakt- og policyversioner.

`gate_valid_until` må ikke ligge senere end den tidligste
gyldighedsgrænse for kritiske freshness-vurderinger, rapporter,
reconciliation, bekræftelser eller en Catalyst-katalysators udløbsdato.
En relevant invalidation eller policyændring kan gøre gaten ugyldig
tidligere.

`execution_mode` må ikke ændre checks, resultat, `gate_basis_hash` eller
`gate_valid_until`. Det styrer kun, om en efterfølgende statusovergang
overhovedet er tilladt.

Resultaterne betyder:

- `PASS`: alle gates er opfyldt; casen er berettiget til en separat
  transaktionel statusovergang
- `FAIL`: én eller flere investerings-, rapport-, bekræftelses- eller
  lifecycle-gates er ikke opfyldt
- `BLOCKED_DATA`: en gyldig vurdering kan ikke gennemføres på grund af
  manglende, modstridende, ugyldige eller forældede kritiske data

`FAIL` må ikke automatisk betyde `REJECTED` eller `THESIS_BROKEN`.
`BLOCKED_DATA` er et gate-resultat, ikke en lifecycle-status. Det kan
berettige en separat D003-overgang til `DATA_HOLD`, men ændrer aldrig
lifecycle-status i sig selv.

High Conviction kræver alle relevante D002-gates, herunder:

- profilens objektive score- og delscorekrav
- profilens AI Confidence-krav
- Data Confidence ≥85 for Compounder eller ≥80 for Catalyst
- ingen kritiske balance-, data-, governance- eller thesis-red flags
- gyldig Deep Research
- gyldig uafhængig second opinion
- aktuel reconciliation med `alignment_status = ALIGNED`
- dokumenterede separate bekræftelser efter D002, D003 og den aktive `confirmation_policy`
- ingen afhængighed af ét enkelt nøgletal eller én enkelt evidenstype

Hver bekræftelse skal referere til en særskilt immutable
evalueringsrecord med eget evalueringstidspunkt og en aktuel
freshness-kontekst. Et retry eller replay med samme idempotency key, et
cache-hit eller genlæsning af den samme rapport tæller ikke som en ny
bekræftelse.

For Compounder skal `confirmation_policy` operationalisere D002's krav
om mindst to kvalificerende kørsler med cirka 72 timers afstand i en
eksplicit tidsregel. For Catalyst skal policyen håndhæve D002's krav om
en ny uafhængig bekræftelse efter et
`PROVISIONAL_CATALYST_OPPORTUNITY`-label. Den samme rapport,
reconciliation eller evidensrecord må ikke dobbeltælle som flere
uafhængige krav.

Portfolio Fit vurderes fortsat separat efter D002. Det må ikke ændre den
objektive Opportunity Score, AI Confidence eller Data Confidence og må
hverken opfylde eller underkende en High-Conviction-gate. Portfolio Fit
kan efterfølgende påvirke anbefalet portfoliohandling, prioritering og
visning.

Derudover kræver High Conviction:

- fundamentals opdateret efter seneste offentliggjorte regnskab
- ingen ventende post-earnings refresh
- alle kritiske normaliserede inputfelter tilgængelige og valide
- alle tilhørende kritiske freshness-vurderinger `FRESH`
- relevante events og nyheder kontrolleret efter aktiv policy
- alle nødvendige rapportgyldighedsvurderinger `VALID`
- ingen nyere inputpakke, event eller policyændring, som invaliderer
  gate-evidensen

Fælles kritiske input omfatter mindst:

- entydig instrumentidentitet, børs, valuta og sector-aware profil
- seneste forventede markedsdata for den relevante handelsdag
- status for seneste kendte offentliggjorte regnskab
- de konkrete normaliserede felter, som score og gate bygger på
- den freshness-kontekst og de policyversioner, gaten anvender

Yderligere kritiske Compounder-input omfatter mindst:

- relevante fundamentals
- balance- og cash-flow-felter
- relevante valuationfelter
- tilstrækkelig vægtdækning efter D002
- gennemført events-/news-kontrol efter Compounder-policyen

Yderligere kritiske Catalyst-input omfatter mindst:

- aktuelt event-/news-snapshot
- konkret og kildeunderstøttet katalysator
- katalysatorens udløbsdato
- thesis-invalidation-kriterier
- mindst to uafhængige evidenstyper
- de fundamentals, estimatændringer eller markedsdata, der understøtter
  vendepunktet og markedsbekræftelsen

Et snapshot eller datalag med `PARTIAL` kan kun passere, når:

- alle felter, som er kritiske for den konkrete gate, er tilgængelige
- alle kritiske felter er valide
- alle kritiske freshness-vurderinger er `FRESH`
- D002's krav til relevant vægtdækning er opfyldt
- den relevante Data Confidence-grænse er opfyldt

Et manglende, ugyldigt, `AGING`, `STALE` eller `ERROR` kritisk input
blokerer promovering og giver gate-resultatet `BLOCKED_DATA`, når dataproblemet forhindrer
en gyldig vurdering.

`NOT_APPLICABLE`-felter udelades efter den relevante sector-aware profil
og må ikke i sig selv blokere gaten eller reducere vægtdækningen.

Weekender og helligdage må ikke fejlagtigt gøre sidste handelsdags data
stale. Den relevante børs-/markedskalender skal indgå i
freshness-vurderingen.

En gate-evaluering ændrer aldrig selv lifecycle-status og sender aldrig
selv en alert. Den samme gate-evidens og de samme kontrakt- og
policyversioner skal give samme gate-resultat i `SHADOW` og `LIVE`.

En efterfølgende statusovergang til `HIGH_CONVICTION` må kun gennemføres,
når:

- gate-resultatet er `PASS`
- `gate_valid_until` ikke er passeret
- opportunity-status, inputpakke og relevante policyversioner stadig
  matcher gate-evalueringen
- ingen nyere invalidation eller kritisk dataændring er registreret
- `execution_mode` og aktiv feature policy tillader overgangen

I `SHADOW`-mode gemmes gate-evalueringen, men der oprettes ingen
automatisk `HIGH_CONVICTION`-overgang eller opportunity-alert.

I `LIVE`-mode gennemføres statusovergangen idempotent og transaktionelt.
Kun en committed overgang til `HIGH_CONVICTION` må oprette D003's
normale opportunity-alert. Genkørsel af samme gate eller overgang må
ikke oprette en dubleret alert.

### 10.6 Providerstrategi, kildevalg og fejladfærd

V3.0 starter med:

- Yahoo som primær fundamental-kilde
- eksisterende provider-lag til pris, historik og metadata
- EODHD kun som dokumenteret fallback for allerede understøttede
  kontrakter

Ingen provider må tilføjes, prioriteres eller anvendes som fallback
stiltiende.

Hver provider-/kapabilitetskombination registreres i en versioneret
`provider_policy` med mindst:

- `provider_policy_version`
- `provider_id`
- `data_layer`
- `data_subtype`
- understøttede markeder og instrumenttyper
- rolle: `PRIMARY` eller `FALLBACK`
- prioritet og tilladte fallback-betingelser
- `source_contract_version`
- timeout-, retry-, backoff- og circuit-breaker-regler
- rate- og kvotegrænser
- licens-, anvendelses-, opbevarings- og
  redistributionsbegrænsninger
- `effective_from` og eventuelt `effective_until`

Credentials eller andre secrets må ikke gemmes i policy-, snapshot-,
attempt- eller auditrecords.

En versioneret source-kontrakt definerer mindst:

- krævede og valgfrie kildefelter
- kildefelternes timestamp-semantik
- enheder og valuta
- null- og manglende-data-semantik
- valideringsregler
- mapping til den normaliserede kontrakt
- kendte providerbegrænsninger

`observed_at` skal afledes af kildens faktiske observation eller
rapporteringsperiode. `retrieved_at` må aldrig bruges som erstatning
for et ukendt `observed_at`.

Hver planlagt hentning registreres i en immutable `retrieval_plan` med
mindst:

- `retrieval_plan_id`
- `job_run_id`
- instrument eller eksplicit scope
- `data_layer` og `data_subtype`
- `requested_as_of`
- `provider_policy_version`
- godkendt provider-rækkefølge
- relevante source- og normaliseringskontraktversioner

Hvert providerforsøg registreres som en immutable `retrieval_attempt`
med mindst:

- `retrieval_attempt_id`
- `retrieval_plan_id`
- `provider_id`
- `provider_symbol`
- `attempt_number`
- `started_at` og `finished_at`
- `outcome`
- providerens status-/fejlkode, når tilgængelig
- normaliseret fejlklasse
- retry- og rate-limit-metadata
- payloadreference og hash, når en payload blev modtaget

Mindst følgende outcomes understøttes:

- `SUCCESS`
- `PARTIAL`
- `NOT_SUPPORTED`
- `TRANSIENT_ERROR`
- `RATE_LIMITED`
- `AUTH_ERROR`
- `CONTRACT_ERROR`
- `PERMANENT_ERROR`

Et mislykket forsøg uden brugbar payload opretter ingen fabrikeret
dataobservation; fejlen findes i `retrieval_attempt`.

En modtaget payload, der kan bevares, men ikke opfylder hele
source-kontrakten, kan oprette et provider-snapshot med `PARTIAL` eller
`ERROR`, præcise manglende-data-årsager og warnings. Kun validerede
felter må føres videre til normalisering.

Fallback må kun anvendes, når den aktive `provider_policy` tillader det.
Fallback-data må kun opfylde et kritisk input, når:

- samme relevante normaliserede kontrakt kan opfyldes
- observationstidspunkt og freshness kan dokumenteres
- de samme obligatoriske valideringsregler er bestået
- field-level provenance viser den faktiske kilde
- providerens licens-, anvendelses-, opbevarings-, rate- og
  kvotegrænser overholdes

Flere providers må kun kombineres gennem en versioneret
normaliserings- og konfliktpolicy med field-level provenance. En
uafklaret konflikt om et kritisk felt må ikke løses stiltiende og skal
føre til reduceret Data Confidence eller et eksplicit
`CRITICAL_DATA_BLOCKED`-signal til gate-laget, afhængigt af
gatekritikaliteten. Gate-laget kan derefter evaluere dette til
`BLOCKED_DATA`; en eventuel D003-overgang til `DATA_HOLD` sker separat.

Ved providerfejl skal Aureum:

1. registrere det immutable providerforsøg
2. bevare sidste valide snapshot uændret
3. aldrig mutere snapshotet til `AGING` eller `STALE`
4. oprette en ny freshness-vurdering, når aktiv policy eller det
   aktuelle evalueringstidspunkt kræver det
5. anvende begrænset retry med backoff, jitter og circuit breaker
6. forsøge godkendt fallback, når policy, licens, rate og kvote
   tillader det
7. aldrig klassificere et snapshot som `AGING` eller `STALE` alene,
   fordi det aktuelle providerforsøg fejlede; klassifikationen følger
   fortsat snapshotets observationstid, den aktive freshness-policy,
   immutable freshness-kontekst og reelle invaliderende begivenheder
8. reducere Data Confidence kun når dækning, aktualitet, konsistens
   eller validerbarhed faktisk påvirkes
9. markere `CRITICAL_DATA_BLOCKED`, når kritiske input ikke kan
   valideres fra en frisk, godkendt kilde; gate-laget skal da blokere
   High-Conviction-promovering med gate-resultatet `BLOCKED_DATA`
10. isolere fejlen, så resten af instrumenterne og batchen fortsætter

En providerfejl er ikke i sig selv et negativt investeringssignal.
Vedvarende auth-, kontrakt- eller circuit-breaker-fejl må udløse en
deduplikeret system-/driftsalarm, men ikke en opportunity-alert.

Når en provider igen leverer valide data, oprettes nye snapshots og
freshness-vurderinger. Historiske snapshots, attempts og vurderinger
overskrives ikke.

### 10.7 Raw data, normalisering, reproduktion og retention

```text
Raw provider payload
        ↓
Retrieval attempt + provider snapshot
        ↓
Source-contract validation
        ↓
Normalized snapshot + field-level provenance
        ↓
Immutable input package
        ↓
Sector-aware features
        ↓
Opportunity Score / Gate / AI Research
```

Rå payload, provider-snapshot og normaliseret snapshot er forskellige records og må ikke behandles som samme objekt.

Normalisering må aldrig ændre rådata. Ændringer i mapping, validering, konfliktløsning eller beregningslogik kræver en ny `normalization_version` og et nyt normaliseret snapshot. Field-level provenance og oprindelige observationstidspunkter skal bevares.

Retention-policy:

- providerens licens- og opbevaringsregler har altid forrang
- rå provider-payloads opbevares normalt mindst 30 og højst 90 dage; kortere retention kræver provider-/licenskrav, og længere retention kræver en gyldig retention-pin samt provider-policyens tilladelse
- fra dag 31 må rå payloads komprimeres tabsfrit
- efter dag 90 slettes rå payloads, medmindre en gyldig retention-pin kræver fortsat opbevaring
- retention-pins må kun oprettes for aktiv Deep Research/second opinion, en High-Conviction-gate eller committed overgang, en Thesis-Broken-undersøgelse eller en eksplicit audit-, anomali- eller kalibreringssag
- rutinescans, uændrede scorer og almindelige outcomes må ikke automatisk pinne rådata
- hver pin skal mindst have `retention_pin_id`, `record_id`, `pin_reason`, `owner_record_id`, `created_at`, `review_after` og `retention_policy_version`
- `review_after` må højst ligge 365 dage fremme; fornyelse skal være eksplicit, versioneret og auditerbar
- permanente rådata-pins er ikke tilladt i V3.0
- normaliserede snapshots må kun slettes eller kompakteres, når reproducerbarhed bevares
- Deep Research-inputpakken bevares mindst lige så længe som rapporten og dens relevante outcome
- manifests, hashes, provenance og nødvendige policyversioner bevares, når de kræves for reproduktion
- hvis providerregler kræver sletning af nødvendige rådata, skal Aureum respektere kravet, bevare de metadata der lovligt må bevares og markere reproduktionspakken `reproducibility_level = PARTIAL`
- `reproducibility_level = FULL` må kun bruges, når alle nødvendige input, kontrakter, policyversioner og lovligt bevarede rådata kan verificeres
- retention-job skal være idempotente, auditerbare og må ikke efterlade dangling references

### 10.8 Historik og temporal integritet

Historik bygges af immutable records. Historiske observationer, vurderinger og beslutninger må aldrig overskrives for at få fortiden til at ligne den seneste viden.

Enhver historisk beregning eller evaluering skal have et eksplicit `as_of`-tidspunkt og må kun bruge data, som Aureum faktisk havde adgang til på dette tidspunkt.

Som minimum:

- et provider-snapshot må ikke anvendes før både dets `retrieved_at` og `created_at` er nået
- et normaliseret snapshot må ikke anvendes før alle nødvendige source-snapshots var tilgængelige og `normalized_at` var nået
- en AI-rapport må ikke anvendes før `generated_at`
- en gate-, score- eller freshness-vurdering må ikke anvendes før dens `evaluated_at`
- senere restatements, rettelser eller renormalisering må aldrig lække bagud i en historisk `as_of`-evaluering

Periodiske fundamentals skal, når relevant, bevare regnskabsperiode, periodetype og offentliggørelsestidspunkt. Et restatement eller en senere korrektion opretter et nyt snapshot med lineage til den tidligere version; den gamle version bevares.

En renormalisering af historiske data opretter ligeledes nye normaliserede snapshots med ny `normalization_version` og må ikke overskrive de snapshots, som tidligere scores eller beslutninger byggede på.

Historiske sammenligninger må kun behandles som direkte sammenlignelige, når metric-kontrakt, enhed, periodegrundlag og relevant normaliserings-/valutakontekst er kompatible. Ellers markeres sammenligningen som ikke direkte sammenlignelig.

Historikken skal mindst understøtte:

- vækstacceleration
- marginudvikling
- gældsreduktion
- valuationændring
- scoreændring
- signalstabilitet
- thesis-forbedring/-forværring
- lifecycle-overgange
- efterfølgende kursudvikling og outcomes
- reproducerbar shadow-mode- og kalibreringsanalyse uden look-ahead bias

### 10.9 Valuta og FX-provenance

Monetære felter skal bevare både den oprindelige værdi og enhver normaliseret værdi.

Mindst:

- `native_value`
- `native_currency`
- `normalized_value`, når konvertering anvendes
- `base_currency`, når konvertering anvendes
- `fx_rate`
- `fx_pair`
- `fx_snapshot_id`
- `fx_observed_at`
- `fx_policy_version`

Base currency, FX-kilde og konverteringsregel fastlægges i en versioneret `fx_policy` og må ikke hardcodes i scorelogikken.

FX-konvertering skal bruge en kurs, som var tilgængelig på det relevante `as_of`-tidspunkt. En senere FX-kurs må ikke lække bagud i historiske beregninger.

Native value og native currency overskrives aldrig ved konvertering. Genberegning med en ny FX-kurs eller `fx_policy_version` opretter en ny normaliseret værdi eller snapshot med provenance til den anvendte FX-record.

Dimensionsløse metrics og allerede sammenlignelige ratioer må ikke valutakonverteres uden en eksplicit metric-kontrakt.

Hvis en FX-konvertering indgår i et kritisk score- eller gateinput, skal den anvendte FX-record have dokumenteret provenance og tilstrækkelig freshness efter den aktive policy.

### 10.10 Concurrency, idempotency og integritet

Opportunity Store er canonical source of truth for V3-state. JSON-caches er afledte views og må aldrig være eneste autoritative kopi af en beslutning, gate, rapport eller statusovergang.

V3 skal bruge:

- SQLite-transaktioner og aktiverede foreign-key constraints
- versionerede, transaktionelle schema-migrations
- idempotente writes med record-type-specifikke scoped keys
- relevante korte locks eller leases omkring jobs, der ikke må overlappe
- atomic file writes ved afledte JSON-caches
- temp-fil, flush, `fsync` og atomic rename
- sikker retry og genstart efter afbrudte jobs
- transaktionel outbox til alerts og andre irreversible side effects

`input_hash` eller `content_hash` må ikke have én global uniqueness-constraint på tværs af record-typer eller instrumentscopes.

Mindstekrav til scoped idempotency keys:

- provider-snapshot: `(provider_id, instrument_id, data_subtype, observed_at, content_hash)`
- normaliseret snapshot: `(instrument_id, data_subtype, observed_at, normalization_version, source_set_hash)`
- freshness-vurdering: `(snapshot_id, evaluated_at, freshness_policy_version, freshness_context_id)`
- inputpakke: `(purpose, contract_version, input_hash)`
- AI-cache: det pre-call cache-scope defineret i §10.4
- gate-evaluering: `(opportunity_id, target_status, gate_basis_hash, gate_policy_version)`
- statusovergang: `(opportunity_id, gate_evaluation_id, from_status, to_status)`
- alert-outbox: `(status_transition_id, alert_type, channel)`

Et retry med samme idempotency key skal enten returnere den eksisterende semantisk identiske record eller gennemføre præcis én gyldig write. Det må ikke skabe parallelle dubletter.

Gate-evaluering, lifecycle-overgang og alert-delivery er separate records. En committed lifecycle-overgang og dens outbox-record skal oprettes i samme SQLite-transaktion, så en crash eller retry hverken mister eller dublerer alerten.

Ekstern levering, herunder Telegram, sker først efter commit. Delivery-forsøg har egne immutable attempt-records og må genkøres sikkert uden at oprette en ny logical alert.

Concurrent jobs må ikke overskrive immutable records. Ved konflikt om mutable coordination-state skal Aureum bruge compare-and-set, versionsfelt eller tilsvarende transaktionel kontrol frem for last-write-wins.

Et job-run skal have stabilt `job_run_id`. Jobs, der kræver eksklusivitet, skal bruge en tidsbegrænset lease med ejer og udløbstid, så et crash ikke efterlader en permanent lås.

Database- og cache-opdateringer skal kunne genstartes efter afbrudt kørsel uden korruption, tab af committed data eller gentagelse af irreversible side effects.

### 10.11 Acceptance criteria

D004 er implementeringsklar, når mindst følgende kan dokumenteres i tests:

- samme immutable inputpakke og samme kontrakt-/policyversioner giver samme lokale score
- samme snapshot, `freshness_policy_version`, `evaluated_at` og immutable freshness-kontekst giver samme freshness-status
- `instrument_id` forbliver stabil ved ændring af ticker eller provider-symbol
- hvert kritisk score-, gate- og AI-input har field-level provenance
- `N/A` bliver aldrig nul, og sector-irrelevante felter giver ikke straf
- historiske `as_of`-beregninger bruger ingen data, rapporter eller vurderinger fra fremtiden
- restatements og renormalisering overskriver ikke tidligere anvendte snapshots
- FX-konverteringer kan rekonstrueres fra native value, FX-snapshot og policyversion
- providerfejl bevarer sidste valide snapshot uændret
- en providerfejl gør ikke alene et ellers gyldigt snapshot stale
- fallback kan kun opfylde kritiske input efter aktiv provider- og source-kontrakt
- én fejlende aktie stopper ikke resten af batchen
- sidevisning giver nul eksterne data- eller AI-kald
- nyt regnskab eller anden materiel invalidation gør relevant cache og rapportgyldighed uaktuel
- uændrede, fortsat gyldige AI-input giver cache-hit
- et cache-hit tæller ikke som ny AI-generation, second opinion eller tidsmæssig bekræftelse
- second opinion genereres isoleret fra den primære konklusion og sammenlignes først bagefter
- High Conviction kræver en aktuel reconciliation med `alignment_status = ALIGNED`
- `PROVISIONAL_CATALYST_OPPORTUNITY` er kun et label og udløser ikke alene High Conviction eller Telegram
- `PARTIAL` kan kun passere en gate, når alle konkrete kritiske input er valide og `FRESH`
- manglende, ugyldige, `AGING`, `STALE` eller `ERROR` kritiske input blokerer promovering
- dataproblemer giver gate-resultatet `BLOCKED_DATA`; en separat D003-overgang kan sætte lifecycle-status `DATA_HOLD`, men må ikke automatisk give `REJECTED` eller `THESIS_BROKEN`
- samme gate-evidens giver samme gate-resultat i `SHADOW` og `LIVE`
- en gate-evaluering har ingen side effects
- præcis én committed overgang til `HIGH_CONVICTION` giver højst én logical opportunity-alert pr. kanal
- retries og concurrent jobs skaber ikke semantiske dubletter eller overskriver immutable records
- afbrudte jobs kan genstartes uden korruption, tab af committed data eller gentagelse af irreversible side effects
- retention efterlader ingen dangling references og respekterer providerens licens-/opbevaringskrav
- reproduktionspakker mærkes ærligt `FULL` eller `PARTIAL`
- 1.000 aktier kan opdateres uden ukontrollerede burst-kald
- Deep Research kan reproduceres fra den bevarede inputpakke inden for det dokumenterede `reproducibility_level`

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

**Status:** LOCKED

Datakontrakt, snapshotidentitet, provenance, freshness, AI-cache og rapportgyldighed, High-Conviction-gates, provider-adfærd, retention, temporal integritet, FX-provenance samt concurrency/idempotency er godkendt og låst som beskrevet i V3-D004.

### V3-D005

**Status:** LOCKED

D005 fastlægger Aureums globale AI-budget, modelrouting,
research-kontrakter og versionsstyring. Budgetpres må reducere
analysemængden, men aldrig kvalitetskravene til en analyse, der faktisk
gennemføres.

#### D005.1 Global AI-budgetkontrakt

Budgettet gælder samlet for alle betalingsudløsende OpenAI API-kald fra
både V2 og V3. Ingen service, route, cronjob eller manuel funktion må
have et separat ubudgetteret OpenAI-forbrug.

Den aktive, versionerede `budget_policy` bruger kalender­måned i
`Europe/Copenhagen` og følgende DKK-grænser:

- soft target: 70,00 DKK
- warning: 80,00 DKK
- critical: 90,00 DKK
- hard cap: 100,00 DKK

Når D005 er implementeret, er 100,00 DKK et teknisk loft i controllerens
konservative DKK-ækvivalent og ikke blot et rapporteringsmål.

Budgeteksponering beregnes som mindst:

`settled_spend + active_reservations + unresolved_exposure`

Ethvert betalingsudløsende OpenAI-kald kræver en succesfuld,
transaktionel reservation før provider-kaldet starter.

En reservation skal konservativt dække den maksimale tilladte pris for
kaldet ud fra mindst:

- versioneret priskatalog
- valgt provider/modelrute
- estimerede inputtokens
- eksplicit maksimalt outputbudget
- reasoning-/tool-omkostninger, når relevante
- versioneret budget-FX-regel
- konfigureret sikkerhedsmargin

Cached-input-rabat må kun reducere reservationen, når rabatten kan
forudsiges deterministisk. Ellers reserveres som ikke-cachet input.

Et nyt kald må kun accepteres, når den samlede eksponering inklusive
den nye reservation fortsat er højst hard cap.

Hvis prisdata, FX-data, reservationslager eller anden nødvendig
budgetinformation mangler eller er upålidelig, skal controlleren
`fail closed`: det betalingsudløsende kald må ikke starte.

Efter et gennemført kald afregnes reservationen mod faktisk usage og
den faktiske modelidentitet/priskontrakt. Ubrugt reservation frigives.

Hvis faktisk usage mangler eller kaldets betalingsstatus er uklar,
bevares reservationen som `unresolved_exposure`, indtil den kan
reconciles. Usikkerhed må aldrig frigive budget tidligt.

Budgetzonerne betyder:

- under 70 DKK: normal admission efter prioritet og øvrige gates
- 70 til under 80 DKK: lavværdi-/enrichment-kald kan udskydes
- 80 til under 90 DKK: lavprioritets-AI reduceres aggressivt og cache/fallback foretrækkes
- 90 til under 100 DKK: kun beslutningskritiske kald kan optages, når hele reservationen kan rummes
- ved 100 DKK eller utilstrækkeligt resterende budget: alle nye betalingsudløsende kald afvises

Budgetpres må aldrig:

- sænke High-Conviction-gates
- erstatte krævet Deep Research med en utilstrækkelig billig analyse
- gøre en krævet second opinion mindre uafhængig
- genbruge et cache-hit som en ny analyse eller bekræftelse

Hvis den krævede kvalitetsklasse ikke kan rummes i budgettet, skal
analysen udskydes frem for at kvalitetsnedgraderes.

Der er ét globalt budgetledger. V2 og V3 får ikke permanente,
uigennemtrængelige delbudgetter; admission og shedding styres af den
versionerede prioritetspolitik, som defineres i D005.

Aktuelle modelnavne og priser er ikke en del af den låste blueprint-
kontrakt. De ligger i versioneret model- og priskonfiguration og skal
verificeres mod officiel provider-dokumentation ved implementering og
ved senere pris-/modelændringer.

#### D005.2 Budgetledger, perioder og reservationsidentitet

Budgetledgeren er canonical source of truth for budget-admission. Den eksisterende usage-JSONL er audit/telemetri og må ikke alene håndhæve hard cap.

Ledgeren skal ligge i et transaktionelt, concurrency-sikkert store. Den præcise databasestruktur låses senere i D006.

Hver budgetperiode identificeres eksplicit med `budget_period_id` og følger kalendermåned i `Europe/Copenhagen`.

En reservation bindes til den budgetperiode, hvor provider-kaldet bliver optaget. Hvis et allerede startet kald krydser månedsskiftet, afregnes det fortsat i den oprindelige periode.

En reservation, som endnu ikke er startet ved månedsskiftet, må ikke automatisk flyttes til næste måned. Den skal frigives eller udløbe og kræver ny admission i den nye periode.

Hver reservation indeholder mindst:

- `reservation_id`
- `reservation_key`
- `budget_period_id`
- `request_id`
- service og operation
- instrument/scope, når relevant
- `budget_policy_version`
- `priority_policy_version`
- `priority_class`
- `quality_class`
- `budget_zone_at_admission`
- `model_route_decision_id`
- `price_catalog_version`
- `budget_fx_policy_version`
- `budget_fx_snapshot_id`
- estimerede inputtokens
- maksimalt outputbudget
- `reserved_dkk`
- state
- admission-/reason codes
- `created_at`, `expires_at` og relevante transition-timestamps

`request_id` er stabilt for hele samme logical AI-request og grupperer
primary-, retry- og fallback-attempts.

`reservation_key` er den egentlige reservations-idempotency-nøgle og
skal være stabil for samme tilsigtede budgetreservation. Et retry af
samme reservationsoperation skal derfor returnere den eksisterende
reservation frem for at reservere igen.

Et ekstra betalt generation-attempt må kun få en ny `reservation_key`,
når den aktive `generation_policy` tillader forsøget, og enten en
eksisterende samlet reservation allerede dækker det fuldt ud eller en
ny atomisk budget-admission gennemføres efter D005.2/D005.4.

`request_id` må ikke alene bruges som uniqueness-key for reservationer,
fordi ét logical request legitimt kan have flere særskilt budgetterede
providerforsøg.

Admission skal i én atomisk transaktion:

1. læse periodens settled spend, aktive reservationer og unresolved exposure
2. beregne den nye konservative reservation
3. kontrollere hard cap og zone-/prioritetsregler
4. oprette præcis én reservation eller returnere en entydig afvisning

Read-check og reservation må aldrig ske i separate ubeskyttede trin.

Der findes ingen normal runtime-override af hard cap. En ændring af 100 DKK-loftet kræver en ny eksplicit V3-beslutning og versioneret budget-policy.

Reservations-state machine:

- `RESERVED`: optaget, men provider-kaldet er ikke startet
- `STARTED`: provider-kaldet kan have påført omkostning
- `SETTLED`: faktisk usage/pris er afregnet
- `RELEASED`: kaldet startede aldrig, og reservationen er frigivet
- `EXPIRED`: en ikke-startet reservation udløb og er frigivet
- `UNRESOLVED`: kaldet kan have kostet penge, men korrekt afregning kan endnu ikke bevises

Kun `RESERVED` må udløbe automatisk. `STARTED` må aldrig frigives alene på timeout eller procescrash.

Tilladte normale state transitions er:

- `RESERVED` → `STARTED`, `RELEASED` eller `EXPIRED`
- `STARTED` → `SETTLED` eller `UNRESOLVED`
- `UNRESOLVED` → `SETTLED`, når auditerbar reconciliation foreligger

Terminale states må ikke genåbnes eller omskrives; korrektioner sker som nye immutable reconciliation-/auditrecords.

Overgangen fra `RESERVED` til `STARTED` skal committes før provider-kaldet starter. Ved denne overgang bindes et stabilt `generation_attempt_id` til reservationen. Det samme ID skal forbinde reservation, providerforsøg, usage-event og efterfølgende settlement.

Budgeteksponering tæller:

- `RESERVED` og `STARTED`: hele `reserved_dkk`
- `UNRESOLVED`: mindst hele den senest konservativt kendte eksponering
- `SETTLED`: faktisk afregnet DKK-beløb
- `RELEASED` og `EXPIRED`: 0 DKK

Settlement skal være idempotent. Samme provider-/usage-resultat må ikke afregnes to gange.

Hvis faktisk usage eller pris bliver højere end reservationen, må settlement aldrig klippes ned til `reserved_dkk`. Den faktiske eksponering registreres fuldt ud, nye betalingsudløsende kald blokeres, og hændelsen markeres som budget-integritetsafvigelse til reconciliation.

Reconciliation skal kunne behandle mindst:

- manglende usage-data
- provider-timeout efter muligt gennemført kald
- procescrash efter provider-kald men før settlement
- ukendt eller ændret response-model
- pris-/FX-kontrakt, som ikke længere kan verificeres
- dublerede eller forsinkede usage-events

En `UNRESOLVED` reservation må først reduceres eller lukkes, når der findes auditerbar evidens for korrekt betalingsstatus og afregning.

Ledger, reservation, settlement og reconciliation må ikke afhænge af application-memory og skal overleve service-restart.

#### D005.3 Prioritering og budget-shedding

Alle betalingsudløsende AI-requests får en versioneret `priority_class`.
Prioritet bestemmes af beslutningsværdi og aktualitet, ikke af hvilken
route, cron eller brugerhandling der udløste requestet.

Klasser:

- `P1_DECISION_CRITICAL`: AI, der er nødvendig for næste bindende
  beslutningsgate, efter at casen allerede har bestået de relevante
  lokale score-, data-, freshness- og lifecycle-pre-gates; fx krævet
  Deep Research eller uafhængig second opinion tæt på High Conviction
- `P2_MATERIAL_REVIEW`: væsentlig ny information eller stærk kandidat,
  hvor AI-review kan ændre næste beslutningstrin
- `P3_MONITORING_ENRICHMENT`: nyttig løbende AI-fortolkning af
  portfolio-, kandidat- eller nyhedsdata, men uden aktuel gate-afhængighed
- `P4_NARRATIVE_OPTIONAL`: præsentations-/dashboardnarrativ og anden
  tekst, hvor lokale data, cache eller fallback er tilstrækkeligt

Standardmapping for eksisterende V2-operationer:

- `ai_analyst/market_briefing` → `P4_NARRATIVE_OPTIONAL`
- `news_sentiment/market_news_sentiment` → `P3_MONITORING_ENRICHMENT`
- `stock_news/news_sentiment` → `P3_MONITORING_ENRICHMENT`, med mulighed
  for `P2_MATERIAL_REVIEW` ved dokumenteret portfolio-/Opportunity-
  relevans og materielt ændrede input
- `ai_news_check/novo_news_risk` → `P2_MATERIAL_REVIEW`, når nye input
  faktisk kræver AI-vurdering; cache-hit bruger intet nyt budget

En manuel Deep Research-request får ikke automatisk `P1`. Den skal
opfylde samme versionerede prioriteringsregler og lokale pre-gates som
automatiske requests. At en researchtype er krævet af D002 er ikke alene
nok til at gøre et request `P1`.

Priority class må aldrig:

- omgå hard cap
- omgå freshness-, input- eller D003-kalderegler
- omgå cache
- sænke den krævede model-/research-kvalitetsklasse
- gøre et ikke-kritisk request beslutningskritisk alene pga. caller

Den konkrete mapping og eventuelle promotion-regler ligger i en
versioneret `priority_policy` og gemmes på reservationen.

Budgetzonernes admission-regler:

- `NORMAL`, under 70 DKK: `P1`–`P4` kan optages efter cache-, input-,
  freshness- og øvrige kalderegler
- `SOFT`, 70 til under 80 DKK: `P4` defereres som udgangspunkt; `P1`–`P3`
  kan fortsat optages
- `WARNING`, 80 til under 90 DKK: `P4` får som udgangspunkt
  `DEFERRED_BUDGET`; `P3` defereres som udgangspunkt; `P1` og `P2` kan
  optages
- `CRITICAL`, 90 til under 100 DKK: kun `P1_DECISION_CRITICAL` kan
  optages, og kun når hele den konservative reservation kan rummes
- `HARD_CAP`, ved 100 DKK eller utilstrækkeligt resterende budget:
  ingen nye betalingsudløsende OpenAI-kald må starte

Et `P3`-request må kun fortsætte i `WARNING`, hvis det gennem den aktive
`priority_policy` først kvalificerer til `P2`; caller må ikke selv
opgradere prioriteten.

Et budget-admission-resultat skal mindst være én af:

- `ADMITTED`
- `DEFERRED_BUDGET`
- `REJECTED_HARD_CAP`
- `REJECTED_POLICY`

Ved `DEFERRED_BUDGET` må caller anvende en fortsat gyldig cache eller
dokumenteret lokal fallback, men må ikke foregive, at en ny AI-analyse
er gennemført.

Deferred requests må ikke ligge som en ubetinget betalingskø til næste
måned. Før et deferred request senere kan optages, skal Aureum igen
kontrollere:

- D003-kalderegler
- aktuelt input-hash
- freshness og rapportgyldighed
- eksisterende cache
- opportunity-status og materialitet
- den aktuelle budget- og priority-policy

Et request, der ikke længere er relevant, skal udløbe uden API-kald.

Aging af et deferred request må ikke alene hæve dets `priority_class`.
Inden for samme klasse skal rækkefølgen være deterministisk og mindst
kunne tage højde for beslutningsdeadline, materialitet,
portfolio-relevans, request-tidspunkt og stabil tie-breaker.

Budget-controlleren må ikke reservere en fast permanent V2- eller
V3-pulje. Den kan anvende versionerede rate-/concurrency-grænser for at
forhindre én operation i at dominere admission, men sådanne grænser må
aldrig skabe en vej rundt om hard cap.

#### D005.4 Modelrouting og kvalitetsklasser

`priority_class` og `quality_class` er separate begreber. Prioritet afgør,
om et request må bruge budget nu; kvalitetsklasse afgør, hvilke
modelruter der overhovedet er fagligt acceptable.

Mindst følgende kvalitetsklasser bruges:

- `Q1_STRUCTURED_LIGHT`: Candidate Review, V2-enrichment, sentiment og
  korte strukturerede narrativer
- `Q2_DEEP_RESEARCH`: beslutningsrelevant Deep Research med stærkere
  analyse-, sammenhængs- og modargumentationskrav
- `Q3_INDEPENDENT_OPINION`: second opinion med mindst Q2-analytisk
  kapabilitet plus D005s særskilte independence-krav

En versioneret `model_route_policy` definerer for hver research-/operationstype:

- krævet `quality_class`
- krævede modelkapabiliteter
- tilladte provider-/modelruter
- foretrukken rækkefølge
- maksimalt input- og outputbudget
- reasoning-/tool-konfiguration, når relevant
- struktureret response-kontrakt
- tilladte fallback-ruter
- `effective_from` og eventuelt `effective_until`

En konkret route-decision gemmes som immutable `model_route_decision`
og indeholder mindst:

- `model_route_decision_id`
- `model_route_policy_version`
- service, operation og researchtype
- `priority_class`
- `quality_class`
- valgt provider og requested model
- `effective_route_hash`
- anvendte capability-checks
- valgt fallback-niveau, hvis relevant
- beslutningstidspunkt og reason codes

Budget-controlleren må vælge den billigste godkendte rute, der opfylder
hele den krævede kvalitets- og capability-kontrakt.

En billigere rute, som ikke opfylder kvalitetsklassen, er ikke en
fallback; requestet skal i stedet defereres eller afvises.

Aktuelle modelnavne må ikke hardcodes i research-services. De bindes via
den versionerede route-policy og det versionerede priskatalog.

Fallback-regler:

- fallback må kun ske til en rute, som er eksplicit godkendt til samme
  `quality_class`
- fallback må ikke ske alene, fordi budgettet er presset, hvis den
  billigere rute har lavere faglig kapabilitet
- providerfejl, rate-limit eller midlertidig utilgængelighed må kun
  udløse fallback efter aktiv `model_route_policy`
- hver fallback skal gemme reason code og den oprindeligt foretrukne rute
- flere modelkald for samme logical request kræver hver sin
  budgetreservation eller en samlet konservativ reservation, som
  eksplicit dækker alle mulige providerforsøg

For `Q3_INDEPENDENT_OPINION` gælder desuden:

- second opinion skal genereres i et separat provider-/modelkald
- den må ikke modtage den primære rapports konklusion, anbefaling,
  AI Confidence eller færdige argumentation som input
- den skal bruge samme væsentlige evidensgrundlag gennem den immutable
  evidence-input-kontrakt fra D004
- `independence_policy` skal definere minimumskrav til model-/provider-
  uafhængighed og versioneres
- den konkrete second-opinion-rute skal opfylde mindst Q2-kapabilitet
- den må ikke bruge samme response eller cache-entry som den primære
  rapport
- den må gerne bruge en tidligere selvstændigt genereret og fortsat
  gyldig second opinion, når D004s evidence-, cache- og
  reconciliation-regler tillader det
- en billigere second-opinion-rute er kun tilladt, hvis den stadig
  opfylder hele `Q3_INDEPENDENT_OPINION`-kontrakten

Hvis ingen godkendt Q3-rute kan reserveres inden for hard cap, skal
High-Conviction-processen vente. Aureum må ikke erstatte second opinion
med en lavere kvalitetsklasse.

Modelrouting skal ske før budgetreservationen, så reservationen kan
beregnes på den konkrete rute. Hvis fallback efterfølgende bliver
nødvendig, skal controlleren sikre, at den eksisterende reservation
fortsat dækker fallback-rutens maksimale pris; ellers kræves ny atomisk
budget-admission før fallback-kaldet starter.

#### D005.5 Research-kontrakter og strukturerede outputs

Alle V3-researchoutputs skal følge en versioneret
`response_contract_version` og schema-valideres før de kan gemmes som en
gyldig researchrapport.

Et AI-svar må ikke blive gate-evidens alene, fordi det er syntaktisk
læsbart. Manglende obligatoriske felter, ugyldige enums, uventede typer
eller brud på response-kontrakten gør generationen ugyldig.

AI må ikke opfinde finansielle tal, datoer, events eller kilder.
Kvantitative fakta og andre materielle evidenspåstande i rapporten skal
kunne spores til den immutable inputpakke gennem strukturerede
`evidence_refs` eller markeres som AI-fortolkning frem for fakta.

En `evidence_ref` skal mindst kunne identificere relevant snapshot,
inputfelt eller anden immutable inputrecord. En reference til en kilde,
som ikke findes i inputpakken, må ikke fabrikeres.

##### Candidate Review

Candidate Review bruger mindst `Q1_STRUCTURED_LIGHT` og skal mindst
returnere:

- `candidate_review_contract_version`
- `instrument_id`
- `opportunity_profile`
- `case_summary`
- `positive_evidence`
- `negative_evidence`
- `material_changes`
- `evidence_refs`
- `key_risks`
- `candidate_counterarguments`
- `missing_or_uncertain_evidence`
- `thesis_invalidation_candidates`
- `ai_confidence`
- `recommended_next_step`
- `reason_codes`

`recommended_next_step` er en begrænset enum og må mindst understøtte:

- `KEEP_MONITORING`
- `PROMOTE_FOR_DEEP_RESEARCH`
- `NO_FURTHER_AI_NOW`
- `DATA_HOLD_RECOMMENDED`

Candidate Review må ikke selv ændre lifecycle-status, objektiv score,
Data Confidence eller sende alert.

##### Deep Research

Deep Research bruger mindst `Q2_DEEP_RESEARCH` og skal mindst returnere:

- `deep_research_contract_version`
- `instrument_id`
- `opportunity_profile`
- `investment_thesis`
- `why_now`
- `what_market_may_underestimate`
- `financial_strengths`
- `financial_weaknesses`
- `growth_and_margin_analysis`
- `cash_flow_and_balance_analysis`
- `valuation_analysis`
- `evidence_refs`
- `catalysts`
- `key_risks`
- `counterarguments`
- `bull_case`
- `base_case`
- `bear_case`
- `thesis_invalidation`
- `evidence_gaps`
- `ai_confidence`
- `time_horizon`
- `next_relevant_event`
- `conclusion`
- `reason_codes`

Deep Research skal tydeligt adskille:

- observerede inputfakta
- deterministisk beregnede værdier
- AI-fortolkning
- usikkerhed/manglende evidens

AI Confidence skal begrundes ud fra evidensens sammenhæng og styrke og
må aldrig kompensere for lav Data Confidence.

Deep Research må ikke frit ændre Compounder Score eller Catalyst Score.
Hvis AI finder en mulig data-, beregnings- eller kontraktfejl, markeres
den som en særskilt anomali til efterfølgende deterministisk kontrol.

##### Independent Second Opinion

Second opinion bruger `Q3_INDEPENDENT_OPINION` og skal mindst returnere:

- `second_opinion_contract_version`
- `instrument_id`
- `opportunity_profile`
- `evidence_input_hash`
- `independent_thesis`
- `supporting_evidence`
- `contrary_evidence`
- `evidence_refs`
- `counterarguments`
- `key_risks`
- `thesis_invalidation`
- `missing_or_uncertain_evidence`
- `independent_ai_confidence`
- `independent_conclusion`
- `reason_codes`

Second-opinion-outputtet må ikke indeholde et felt, som antager kendskab
til den primære rapports konklusion. Sammenligning med primærrapporten
sker først i D004s separate reconciliation-trin.

Reconciliation skal bruge immutable referencer til begge rapporter og må
ikke omskrive deres outputs. D004s `alignment_status` er den bindende
gate-fortolkning; second opinion må ikke selv erklære
`ALIGNED` eller `MATERIAL_CONTRADICTION`.

##### Schemafejl, retry og outputvalidering

En generation er kun succesfuld, når:

- provider-kaldet er gennemført
- usage/budgetstatus er håndteret efter D005.2
- output kan parses
- response-schemaet validerer
- alle obligatoriske enums og typer er gyldige
- outputtet ikke bryder den relevante research-kontrakt

Et ugyldigt AI-output må aldrig gemmes som en gyldig Candidate Review,
Deep Research eller second opinion.

Et repair-, retry- eller fallback-kald er et nyt potentielt
betalingsudløsende providerforsøg og kræver budgetdækning efter D005.2
og D005.4.

En versioneret `generation_policy` skal mindst definere:

- `generation_policy_version`
- maksimalt antal betalte attempts pr. logical request
- hvilke fejlklasser der må retries
- hvilke fejlklasser der må bruge fallback
- retry/backoff-regler
- output-/schema-valideringskontrakt

I V3.0 må et logical research-request som standard højst bruge to
betalingsudløsende generation-attempts. Et højere loft kræver en ny
versioneret policy og skal fortsat kunne rummes konservativt under hard
cap.

Retry må aldrig ske automatisk ved:

- budgetafvisning
- manglende freshness
- ugyldige kritiske input
- uopfyldte lokale pre-gates
- uændret cache-hit
- permanent policy-/kontraktbrud

Hvis alle tilladte attempts fejler, afsluttes det logical request med
`research_request_status = FAILED_GENERATION`. Dette er en
research-request-status og ikke en D003 lifecycle-status.

Aureum må derefter bruge gyldig cache eller lokal fallback, hvor
kontrakten tillader det, men må ikke fremstille dette som en ny
gennemført AI-researchrapport.

#### D005.6 Pre-call token-, pris- og FX-estimering

Ingen betalingsudløsende modelrute må optages, før dens maksimale
konservative DKK-eksponering kan beregnes.

En versioneret `price_catalog` indeholder mindst:

- `price_catalog_version`
- provider
- model-/route-identitet
- `effective_from` og eventuelt `effective_until`
- inputpris
- cached-input-pris, når relevant
- outputpris
- reasoning-/tool-/modality-priser, når relevante
- `price_currency`
- prismåleenhed
- kilde-/verifikationsmetadata
- `verified_at`

Priskataloget må ikke baseres på modelnavnet alene, når providerens pris
afhænger af endpoint, modality, reasoning, tools eller anden
route-konfiguration.

En versioneret `budget_fx_policy` skal mindst definere:

- `budget_fx_policy_version`
- DKK som budgetvaluta
- tilladte FX-kilder
- konservativ sikkerhedsmargin
- maksimal tilladt FX-alder
- validerings- og fail-closed-regler

Den konkrete kurs gemmes separat som et immutable `budget_fx_snapshot`
med mindst:

- `budget_fx_snapshot_id`
- kildevaluta
- DKK som budgetvaluta
- `fx_rate_dkk_per_source_unit`, entydigt defineret som antal DKK pr. 1 enhed kildevaluta
- FX-kilde
- `fx_observed_at`
- `fx_retrieved_at`
- `budget_fx_policy_version`
- snapshot-hash

En reservation refererer til præcis det `budget_fx_snapshot_id`, som
blev brugt ved admission. Senere FX-opdateringer må ikke omskrive
reservationens historiske DKK-beregning.

Budget-FX bruges kun til budgetkontrol og må ikke forveksles med D004s
investeringsdata-FX.

Pre-call inputestimatet skal dække hele det betalingsrelevante request,
herunder mindst:

- system- og user-input
- developer-/policytekst, når den sendes til provideren
- strukturerede schemas og response-format
- tool-definitioner og øvrig request-overhead
- immutable research-input
- eventuel conversation/context, som faktisk sendes

Når providerens officielle tokenizer eller anden deterministisk
tokenberegning er tilgængelig for den valgte rute, skal den anvendes.

Når inputtokens ikke kan bestemmes eksakt før kaldet, skal Aureum bruge
en dokumenteret konservativ estimator og sikkerhedsmargin. Et
optimistisk gennemsnit må ikke bruges til hard-cap-admission.

Hvert betalingsudløsende request skal have et eksplicit
`max_output_tokens` eller tilsvarende provider-håndhævet outputloft.
Det outputloft, som bruges i reservationen, skal være det samme eller
højere end det loft, der faktisk sendes til provideren.

En modelrute uden et håndhæveligt eller konservativt begrænseligt
maksimalt output-/omkostningsloft må ikke bruges under V3-hard-cap,
medmindre en anden dokumenteret provider-mekanisme giver samme
konservative omkostningsgaranti.

Reservationens konservative prisberegning skal mindst svare til:

`max_input_cost + max_output_cost + max_reasoning_tool_cost + other_route_costs`

konverteret til DKK med reservationens immutable
`budget_fx_snapshot_id` under den aktive `budget_fx_policy` og derefter
justeret med den aktive sikkerhedsmargin.

Reservationen må aldrig bruge forventet gennemsnitsoutput som loft.
Den skal bruge det faktisk håndhævede maksimale outputbudget for requestet.

Hvis flere betalte providerforsøg kan ske under samme logical request,
skal admission enten:

- reservere konservativt for alle tilladte forsøg på forhånd, eller
- kræve ny atomisk budget-admission før hvert ekstra betalt forsøg

Priskataloget skal være immutable pr. version. En prisændring opretter en
ny `price_catalog_version`; historiske reservations- og settlementrecords
bevarer reference til den version, de faktisk brugte.

En eksisterende `RESERVED` reservation må ikke stiltiende genberegnes
efter en ny pris- eller FX-version. Hvis den valgte route ændres før
kaldstart, skal controlleren kontrollere den nye maksimale eksponering
atomisk og enten justere reservationen sikkert eller kræve ny admission.

Et `STARTED` kald afregnes efter den verificerbare pris-/routekontrakt,
der faktisk gjaldt for providerforsøget. Historisk settlement må ikke
omskrives, fordi prislisten senere ændres.

`price_catalog` skal have versionerede validitetsregler.
`budget_fx_snapshot` skal vurderes mod den aktive
`budget_fx_policy` og dens maksimale tilladte FX-alder.

Fail-closed gælder mindst når:

- den valgte route ikke findes entydigt i priskataloget
- priskatalogets gyldighed er udløbet
- budget-FX er ældre end policyens maksimale alder
- pricing units eller route-specifikke tillæg er uklare
- den maksimale output-/reasoning-/tool-eksponering ikke kan begrænses
- den konservative DKK-reservation ikke kan beregnes reproducerbart

En pris-/FX-opdatering må foretages uden AI-kald og skal auditeres med
kilde, tidspunkt og version.

Ved implementation skal aktuelle modelnavne, endpointregler og priser
verificeres mod officiel provider-dokumentation. D005 låser mekanismen,
ikke dagens konkrete prisniveau.

#### D005.7 Model-, prompt-, tool- og response-versionsstyring

Enhver betalingsudløsende AI-generation skal kunne rekonstruere præcis,
hvilken kontrakt Aureum sendte til provideren, og hvilken kontrakt der
blev brugt til at validere svaret.

En versioneret generationskontrakt skal mindst referere til:

- `prompt_contract_version`
- `response_contract_version`
- `generation_policy_version`
- `model_route_policy_version`
- `model_route_decision_id`
- `effective_route_hash`
- relevante `tool_contract_versions`
- `independence_policy_version`, når relevant
- `price_catalog_version`
- `budget_fx_policy_version`
- relevante research-/operation-contract versions

Hver kontraktversion skal være immutable og mindst have:

- stabil version-ID
- `effective_from` og eventuelt `effective_until`
- content-hash
- schema-/formatversion
- ændringsårsag
- auditmetadata

Prompten må bygges af dynamiske inputdata, men selve promptstrukturen,
instruktionerne og outputkravene skal komme fra versionerede
promptkontrakter. Research-services må ikke indeholde skjulte,
uversionerede promptregler, som ændrer modeladfærden.

Tool-definitioner, tool-inputschemas og tool-outputschemas, som kan
påvirke modelsvaret, skal have egne versionerede kontrakter og indgå i
`generation_contract_hash`.

Response-schemaet skal være versionsbundet til den researchkontrakt, som
outputtet skal opfylde. Et response-schema må ikke ændres stiltiende
under samme `response_contract_version`.

En immutable `generation_attempt` skal mindst gemme:

- `generation_attempt_id`
- `request_id`
- `reservation_id`
- reservationens `price_catalog_version`
- reservationens `budget_fx_policy_version`
- reservationens `budget_fx_snapshot_id`
- `input_package_id`
- `prompt_contract_version`
- `response_contract_version`
- `generation_policy_version`
- `model_route_decision_id`
- `effective_route_hash`
- `generation_contract_hash`
- relevante tool-/research-contract versions
- requested model
- resolved response-model, når tilgængelig
- provider response-ID, når tilgængelig
- start-/sluttidspunkt
- attempt-resultat og reason codes
- usage-reference
- output-hash, når output blev modtaget

Cache- og kompatibilitetsregler:

- en ændring i `prompt_contract_version`, `response_contract_version`,
  `generation_contract_hash`, `effective_route_hash` eller anden
  outputpåvirkende kontrakt skaber som udgangspunkt et nyt cache-scope
- en administrativ metadataændring uden outputpåvirkning må ikke alene
  skabe et dyrt cache-miss
- kompatibilitet mellem kontraktversioner må kun erklæres gennem en
  eksplicit versioneret compatibility-policy
- research-services må aldrig antage kompatibilitet alene ud fra ens
  feltnavne eller samme requested model
- et tidligere cache-resultat må kun genbruges, når D004s
  rapportgyldighed og den aktive compatibility-policy begge tillader det

Modelaliaser behandles som routingkonfiguration, ikke som stabile
reproduktionsidentiteter.

Når provideren returnerer en mere præcis response-model end den
requested alias, gemmes begge. Når en præcis response-model ikke
returneres, skal Aureum registrere dette ærligt og må kun love
reproduktion af input, kontrakter og routingvalg — ikke et identisk nyt
modelsvar.

En ændring af konkret modelroute kræver mindst:

- ny immutable `model_route_decision`
- ny vurdering af capability-krav
- ny konservativ prisreservation
- korrekt cache-scope efter D004/D005
- audit af årsagen til routeændringen

Ændringer i prompt-, tool-, response-, generation- eller
research-kontrakter må ikke foretages stiltiende i production.
Hver ændring kræver ny version, auditspor og relevante regressionstests.

En kontraktversion, som allerede er refereret af en bevaret rapport,
gate, reservation eller generation-attempt, må ikke omskrives eller
slettes, så historisk audit og reproduktion brydes.

Ved deployment af nye kontrakt-/modelversioner skal Aureum kunne køre
shadow-/canary-validering uden at gøre den nye version til automatisk
default for alle betalte kald.

#### D005.8 Acceptance criteria

D005 er implementeringsklar, når mindst følgende kan dokumenteres i
automatiserede tests og auditdata:

Budget og admission:

- alle betalingsudløsende OpenAI-kald går gennem den globale
  budget-controller; direkte ubudgetterede provider-kald kan ikke
  omgå gatewayen
- to eller flere samtidige reservationsforsøg kan ikke tilsammen
  bringe budgeteksponeringen over 100,00 DKK-hard-cap
- grænserne 70/80/90/100 DKK testes eksplicit ved og omkring hver
  zonegrænse
- budgeteksponering medregner settled spend, aktive reservationer og
  unresolved exposure
- manglende pris-, FX- eller ledgerdata giver fail-closed
- et `STARTED` kald frigives ikke ved timeout, crash eller restart
- settlement og reconciliation er idempotente
- manglende usage ender konservativt som `UNRESOLVED`
- faktisk omkostning over reservation registreres fuldt og blokerer nye
  betalte kald, indtil integritetsafvigelsen er håndteret
- månedsskifte i `Europe/Copenhagen` flytter ikke gamle reservationer
  stiltiende til en ny budgetperiode
- service-restart mister ikke reservationer, settlement eller
  unresolved exposure

Prioritering og shedding:

- caller, route, cron og manuel trigger kan ikke selv hæve priority class
- `CRITICAL`-zonen optager kun gyldige `P1_DECISION_CRITICAL`-requests
- `HARD_CAP` starter ingen nye betalingsudløsende OpenAI-kald
- deferred requests revaliderer cache, input-hash, freshness,
  materialitet, lifecycle-status og budget før senere admission
- irrelevante deferred requests udløber uden AI-kald
- budgetpres reducerer analysemængde, men ændrer ikke krævet
  kvalitetsklasse eller High-Conviction-gates
- eksisterende V2-operationer er underlagt samme globale budget- og
  priority-policy som V3

Modelrouting og kvalitet:

- hver betalt generation har en immutable `model_route_decision`
- valgt route opfylder den krævede `quality_class`
- en billigere utilstrækkelig model kan ikke anvendes som fallback
- hvert ekstra betalt fallback-/retry-attempt har dokumenteret
  budgetdækning
- manglende godkendt Q2/Q3-rute defererer research frem for at
  kvalitetsnedgradere den
- second opinion er et separat provider-/modelkald og opfylder den
  aktive independence-policy
- second opinion modtager ikke primærrapportens konklusion,
  anbefaling eller AI Confidence som modelinput

Research og output:

- Candidate Review, Deep Research og second opinion validerer mod deres
  versionerede response-contracts
- et schema-invalidt eller ufuldstændigt output kan ikke blive en gyldig
  researchrapport eller gate-evidens
- materielle evidenspåstande kan spores gennem `evidence_refs`
- AI kan ikke omskrive objektive Compounder-/Catalyst-scores
- et fejlet logical research-request får eksplicit
  `research_request_status = FAILED_GENERATION`
- et logical research-request overskrider ikke generation-policyens
  maksimale antal betalte attempts
- repair/retry/fallback kan ikke ske automatisk efter budgetafvisning,
  manglende freshness eller permanente kontraktbrud

Pris- og tokenkontrol:

- reservationens inputestimat omfatter hele det betalingsrelevante
  request
- hvert betalt kald har et provider-håndhævet eller tilsvarende
  konservativt output-/omkostningsloft
- reservation bruger maksimal tilladt eksponering og ikke forventet
  gennemsnitsoutput
- cached-input-rabat anvendes kun pre-call, når den kan forudsiges
  deterministisk
- stale eller ukendt priskatalog blokerer kald
- stale eller ugyldigt `budget_fx_snapshot` blokerer kald
- historiske price-/FX-versioner omskrives ikke efter settlement
- reservationens DKK-beregning kan reproduceres fra priskatalog,
  route-decision, tokenestimat, outputloft, FX-snapshot og policyversion

Versionering, cache og audit:

- enhver outputpåvirkende prompt-, tool-, response-, generation- eller
  routeændring får korrekt nyt cache-scope
- rent administrativ metadataændring skaber ikke alene et betalt
  cache-miss
- cache-hit bruger intet nyt AI-budget og tæller ikke som ny generation,
  second opinion eller tidsmæssig bekræftelse
- modelalias alene behandles ikke som reproduktionsidentitet
- bevarede rapporter, gates, reservationer og attempts beholder
  referencer til de immutable kontraktversioner, de faktisk brugte
- `generation_attempt_id` binder reservation, providerforsøg,
  usage-event og settlement sammen
- generation-attemptets pris-/FX-referencer matcher den immutable
  reservation, som blev brugt ved admission; eventuelle senere
  settlement-korrektioner bevares som særskilte immutable auditrecords
- nye kontrakt-/modelversioner kan shadow-/canary-valideres uden
  automatisk at blive production-default

Production-sikkerhed:

- almindelig sidevisning starter fortsat ingen provider- eller AI-kald
- D005-implementering kan feature-flages og rulles tilbage uden tab af
  V2-data
- budget-controlleren må ikke erklæres aktiv, før alle eksisterende
  betalingsudløsende OpenAI-call paths er dækket af admission,
  reservation og settlement
- aktuelle modelnavne og priser verificeres mod officiel
  provider-dokumentation ved implementering; blueprint-kontrakten
  forbliver model- og prisneutral

### V3-D006

**Status:** LOCKED

D006 er formelt godkendt og låst. Ændringer til persistence-/databasekontrakten
kræver en ny eksplicit V3-beslutning og må ikke indføres stiltiende under
implementeringen.

D006 konkretiserer den fysiske persistence-kontrakt for de allerede
låste D004- og D005-records. D006 må ikke ændre scorelogik,
lifecycle-definitioner, High-Conviction-gates, AI-kvalitetskrav eller
budgetgrænser.

#### D006.1 Database boundary, path, SQLite-runtime og backup/restore

V3 Opportunity Store skal være en separat canonical SQLite-database og
må ikke lægges ind i `aureum_accounts.sqlite3`.

`aureum_accounts.sqlite3` forbliver autoritativ for accounts,
authentication, MFA, authorization, Deep-AI-entitlements og personlige
bruger-/aktietilvalg.

V3-databasen er canonical source of truth for mindst:

- objective Opportunity-state og historik
- provider-/normalized snapshots og provenance-records
- immutable inputpakker og freshness-vurderinger
- AI-researchreports, generation-attempts og reconciliation
- gate-evalueringer og lifecycle-overgange
- alert-outbox og delivery-attempts
- D005s globale AI-budgetledger, reservationer, settlement og
  reconciliation
- V3 job-/lease-coordination, hvor D006 senere eksplicit tillader
  mutable coordination-state

Den separate database bruger det låste logical navn
`aureum_v3.sqlite3`.

Standardstien skal komme fra Aureums state-path-kontrakt som
`state_path("aureum_v3.sqlite3")`.

En eksplicit environment override skal understøttes som
`AUREUM_V3_DB_PATH`. Override-stien skal være absolut og må ikke
stiltiende falde tilbage til en anden database ved ugyldig
konfiguration.

V3-databasen, dens WAL-/SHM-sidecars og konsistente backup-snapshots er
runtime state og må ikke versionsstyres i Git.

Der må ikke oprettes SQLite foreign keys på tværs af V3-databasen og
`aureum_accounts.sqlite3`. Hvis et V3-record legitimt skal referere til
en ekstern bruger-/account-identitet, gemmes kun et stabilt eksternt ID
efter den relevante kontrakt.

En workflow, der berører begge databaser, må ikke antage en distribueret
atomisk transaktion. Cross-store-koordinering skal i stedet være
idempotent, retry-sikker og eksplicit håndtere delvis succes.

V3-store-initialisering og migrationsværktøjer skal etablere
`PRAGMA journal_mode = WAL`. Normale runtime-forbindelser skal verificere
den forventede journal mode og må ikke stiltiende skifte til en svagere
eller ikke-understøttet mode. Hvis den forventede canonical write-mode
ikke kan etableres eller verificeres, skal writes fail closed.

Alle normale V3-forbindelser skal mindst anvende:

- `PRAGMA foreign_keys = ON`
- eksplicit `busy_timeout`; V3.0 production-default er 15000 ms
- eksplicit durability-policy; V3.0 bruger `synchronous = FULL` for
  canonical writes
- `sqlite3.Row` eller en tilsvarende entydig row-mapping
- et separat V3 `PRAGMA user_version`, uafhængigt af account-databasens
  schema-version

En proces må ikke skrive til databasen, hvis dens `user_version` er
nyere end den schema-version, som processen understøtter.

Databasefilen samt eksisterende `-wal` og `-shm` skal have private
runtime-permissions; V3.0 kræver mindst mode `0600` på disse filer.

Live backup af V3 må ikke implementeres som uafhængig rå kopiering eller
tar-arkivering af en aktiv `.sqlite3`-, `-wal`- og `-shm`-fil. Disse
filer kan ellers repræsentere forskellige tidspunkter.

En normal V3-backup skal i stedet:

1. åbne den canonical database gennem den understøttede SQLite-stack
2. skabe et konsistent snapshot med SQLite online-backup API
   (`sqlite3.Connection.backup`) eller en dokumenteret mekanisme med
   samme consistency-garanti
3. skrive snapshot til en midlertidig fil
4. validere snapshot ved at kræve `PRAGMA quick_check = ok` og nul
   fejl-rækker fra `PRAGMA foreign_key_check`
5. gemme mindst schema-version, snapshot-tidspunkt, kildeidentitet,
   filstørrelse og SHA-256 i backupmetadata
6. flush/fsync snapshot og nødvendig metadata før publicering
7. publicere snapshot atomisk og fsync den relevante parent directory,
   så rename/publicering også er crash-durable
8. lade platform-/full-backup eksplicit arkivere det validerede snapshot
   og dets metadata frem for de aktive V3 DB/WAL/SHM-filer; dette skal
   ske også når `AUREUM_STATE_DIR` eller `AUREUM_V3_DB_PATH` ligger uden
   for `PROJECT_DIR`

En backup må kun markeres succesfuld, når snapshotvalideringen er
bestået.

Restore skal ske uden aktive V3-writers eller under en dokumenteret
write-quiesce-procedure. Før restored data kan blive canonical skal
Aureum mindst:

- validere snapshot-hash og backupmetadata
- køre `PRAGMA quick_check` og `PRAGMA foreign_key_check`
- kontrollere, at `user_version` er understøttet
- bevare den hidtidige canonical database som rollback-materiale, indtil
  restore er verificeret
- sikre, at en restored hoveddatabase aldrig åbnes sammen med stale
  WAL-/SHM-sidecars fra den tidligere database
- publicere den restored database atomisk og fsync den relevante
  parent directory
- genåbne og gentage integrity-/schema-check før writers frigives

Et ældre, men understøttet V3-backupsnapshot må ikke stiltiende
overskrives under restore. Eventuel efterfølgende schema-migration sker
efter D006s migrationskontrakt og med separat pre-migration-backup.

#### D006.2 Canonical tabel- og relationsmodel

D006 låser en hybrid relationsmodel: identitet, tidslinje, hashes,
states, budgettal og alle referencer, som bruges til foreign keys,
idempotency, gates, audit eller queries, gemmes som eksplicitte
relationelle kolonner. Komplekse immutable provider-, research- og
check-payloads må gemmes som schema-versioneret JSON, når de ikke skal
fungere som relationelle nøgler.

Et felt må ikke gemmes kun inde i opaque JSON, hvis feltet bruges til:

- primary eller foreign key
- uniqueness/idempotency
- lifecycle- eller reservations-state
- gate-resultat eller gate-validitet
- budget-admission eller settlement
- temporal ordering/freshness
- retention/legal hold
- almindelig filtrering, som er nødvendig for korrekt runtime-adfærd

JSON-payloads skal valideres mod deres versionerede schema før commit og
have en reproducerbar canonical serialization/content-hash, når
payloadets identitet eller audit afhænger af indholdet.

Alle semantiske V3-identiteter bruger stabile opaque `TEXT`-IDer.
SQLite `rowid` eller `AUTOINCREMENT` må bruges som intern teknisk
optimering, men må ikke være den eneste eksternt refererede identitet
for en D004/D005-record.

Persistente tidspunkter skal have én canonical UTC-repræsentation, så
lexical og kronologisk ordering ikke kan være uenige. Den relevante
business-timezone, fx `Europe/Copenhagen` for budgetperioden, gemmes
eller følger den versionerede policy og må ikke udledes fra serverens
lokale timezone.

Budgetbeløb må ikke håndhæves med SQLite `REAL`. Canonical DKK-beløb til
hard-cap, reservation og settlement gemmes som heltalsbaserede
`*_dkk_micros`, hvor 1 DKK = 1.000.000 micros. Tokenantal gemmes som
heltal. Pris- og FX-rater, der kræver højere eller anden decimal
præcision, gemmes i en reproducerbar decimal/rational repræsentation
efter den versionerede pris-/FX-kontrakt; binary floating point må ikke
være authoritative for hard-cap-beregningen.

Mindste canonical table families er følgende.

##### Instrument-, provider- og kontraktregister

`instruments`
- `instrument_id` er primary key
- indeholder kun stabil instrumentidentitet og langsomt skiftende
  instrumentmetadata, som har en eksplicit kontrakt
- ticker/symbol må ikke være primary key

`instrument_aliases`
- refererer med foreign key til `instruments`
- gemmer alias-type/provider, symbol, `valid_from` og `valid_until`
- historiske aliases overskrives ikke ved tickerændring

`providers`
- stabil `provider_id` og provideridentitet
- runtime-secrets må ikke gemmes her

`contract_versions`
- immutable registry for de versionerede policy-, prompt-, response-,
  tool-, normalization-, gate-, price- og øvrige kontrakter, som skal
  kunne rekonstrueres
- gemmer mindst contract-kind, version-ID, content-hash,
  effective-period og den lovligt bevarbare kontraktdefinition eller
  reference til den
- en allerede refereret kontraktversion må ikke ændres in place

`price_catalogs`
- én immutable catalog-record pr. `price_catalog_version`
- refererer til den tilsvarende versionerede kontrakt og gemmer
  provider, price-currency, effective-period og verification metadata

`price_catalog_entries`
- child-records til `price_catalogs`
- identificerer den konkrete model-/route-/endpoint-/modality-/
  reasoning-/tool-priskontrakt, som D005 kan reservere imod
- authoritative priser gemmes i reproducerbar decimal/rational form,
  ikke som binary `REAL`
- pre-call budgetcontrolleren må ikke være afhængig af at parse et
  opaque dokument for at finde den bindende pris for en route

##### Retrieval, rådata, snapshots og provenance

`retrieval_plans`
- primary key `retrieval_plan_id`
- refererer til `job_run_id`, scope, data layer/subtype og relevante
  provider-/policyversioner

`retrieval_attempts`
- primary key `retrieval_attempt_id`
- foreign key til `retrieval_plans`
- gemmer faktisk `provider_id`, provider-symbol, attempt-number,
  tidsstempler, resultat og reason codes

`provider_raw_payloads`
- separat record for rå providerpayload eller dens retention-manifest
- gemmer mindst stabil raw-payload-ID, `provider_id`, retrieval-attempt,
  content-hash, storage/payload-state og relevante retentionmetadata
- fysisk payload kan senere purges efter D004/providerregler uden at
  slette det lovligt bevarbare manifest eller omskrive snapshots

`data_snapshots`
- primary key `snapshot_id`
- foreign key til `instruments`
- fælles envelope for både `PROVIDER` og `NORMALIZED`
- gemmer relationelt mindst `snapshot_kind`, `instrument_id`,
  `data_layer`, `data_subtype`, anvendt symbol, `observed_at`,
  `available_at`, schema/versionfelter og relevante hashes
- provider-specifikke idempotencyfelter som `provider_id` og
  `content_hash` samt normalized-specifikke felter som
  `normalization_version` og `source_set_hash` ligger som eksplicitte
  nullable kolonner med CHECK-regler bundet til `snapshot_kind`
- selve schema-validerede snapshot-payloadet må ligge som immutable JSON

`normalized_snapshot_sources`
- many-to-many relation fra et normalized `snapshot_id` til de
  provider-/source-snapshots, som faktisk indgik
- må ikke reduceres til kun `source_set_hash`

`field_provenance`
- refererer til det normalized snapshot
- identificerer target field/path
- refererer til faktisk source `snapshot_id` og source field/path
- gemmer `transformation_id`
- flere source-records pr. derived field er tilladt og skal kunne
  repræsenteres uden tab

`investment_fx_snapshots`
- immutable D004 FX-records til investerings-/normaliseringsdata
- er fysisk og semantisk adskilt fra D005s budget-FX
- bevarer rate, pair/currencies, observed/available time, source,
  policyversion og provenance

##### Freshness og immutable inputpakker

`freshness_contexts`
- primary key `freshness_context_id`
- gemmer `as_of`, `context_hash` og relevant policy/schema-identitet

`freshness_context_snapshots`
- join-table mellem freshness context og calendar-/event-snapshots
- role angiver mindst `CALENDAR` eller `EVENT`
- den samme immutable context kan derfor rekonstrueres uden JSON-only
  snapshotreferencer

`freshness_assessments`
- primary key `freshness_assessment_id`
- foreign keys til `data_snapshots` og `freshness_contexts`
- gemmer relationelt `evaluated_at`, `valid_until`,
  `freshness_status`, `freshness_policy_version` og reason-code payload

`input_packages`
- primary key `input_package_id`
- gemmer `purpose`, `contract_version`, `created_at`, `input_hash`,
  reproducibility metadata og immutable package-manifest

`input_package_snapshots`
- join-table fra inputpakke til alle anvendte `snapshot_id`

`input_package_freshness_assessments`
- join-table fra inputpakke til alle anvendte
  `freshness_assessment_id`

`input_package_contract_refs`
- join-table fra inputpakke til de konkrete immutable kontrakt- og
  policyversioner, som indgår i package-identitet/reproduktion
- ref-role angiver kontraktens funktion i inputpakken

Kritiske policy-/contract-referencer i en inputpakke skal være
relationelt bundet eller, for ikke-relationelle metadata, indgå i et
schema-valideret immutable manifest bundet til inputpakkens hash; de må
ikke kunne ændres efter package-creation.

##### Opportunity, score, labels, gates og lifecycle

`opportunities`
- primary key `opportunity_id`
- foreign key til `instruments`
- gemmer `opportunity_profile`, `current_lifecycle_status`,
  `lifecycle_state_version` og creation/update metadata
- COMPOUNDER og CATALYST kan være separate opportunities for samme
  instrument
- `current_lifecycle_status` er en canonical current-state head, men må
  kun ændres i den samme beskyttede transaktion, som opretter den
  gyldige `lifecycle_transitions`-record
- lifecycle-headen opdateres med compare-and-set/state-version og aldrig
  med ubeskyttet last-write-wins
- transitionhistorikken er immutable audit source og skal kunne
  validere/rebuildere current-state headen

`score_assessments`
- immutable score-records med stabil `score_assessment_id`
- refererer til opportunity/instrument, relevant `input_package_id`,
  score-/policyversioner, score, Data Confidence og schema-valideret
  breakdown/check payload

`qualification_label_events`
- immutable assignment/removal-events for supplerende labels som
  `PROVISIONAL_CATALYST_OPPORTUNITY`
- aktuelle labels udledes fra eventhistorikken eller en rebuildable
  projection; label-events må ikke omskrive lifecycle

`confirmation_evidence`
- immutable records for de særskilte bekræftelser, der kan indgå i
  D002/D003-gates
- identitet og provenance skal gøre det muligt at forhindre, at samme
  evidens dobbeltælles

`gate_evaluations`
- primary key `gate_evaluation_id`
- foreign keys til `opportunities`, `instruments`,
  `freshness_contexts` og `input_packages`
- gemmer relationelt mindst profile, lifecycle-before, target-status,
  execution-mode, result, evaluated/valid-until, gate-policy-version,
  `gate_basis_hash` og Data Confidence

`gate_evaluation_scores`
- join-table til de konkrete `score_assessment_id`-records

`gate_evaluation_report_validity`
- join-table til de konkrete report-validity-assessments

`gate_evaluation_confirmations`
- join-table til de konkrete confirmation-evidence-records

`gate_evaluation_contract_refs`
- join-table til de konkrete D002/D003/gate-/confirmation- og øvrige
  immutable beslutningskontrakter, der indgår i
  `decision_contract_refs` og `gate_basis_hash`

`gate_evaluations` refererer direkte til
`research_reconciliation_id`, når gate-kontrakten kræver reconciliation.
Checks/reason codes må være schema-valideret immutable JSON, men de
relationelle evidensreferencer ovenfor må ikke kun gemmes i JSON.

`lifecycle_transitions`
- primary key `status_transition_id`
- foreign keys til opportunity og den bindende `gate_evaluation_id`
- gemmer `from_status`, `to_status`, commit-tidspunkt og transition-
  contract/policy reference
- transitionhistorikken er immutable canonical audit
- `opportunities.current_lifecycle_status` er den canonical operative
  current-state head og skal altid kunne valideres/rebuildes fra den
  committed transitionhistorik
- lifecycle-transition og CAS-opdatering af current-state head skal ske
  atomisk efter D006s transaktionskontrakt

##### AI-request, routing, generation, rapport og reconciliation

`ai_requests`
- primary key er D005s stabile `request_id`
- er den globale logical-request-identitet for alle AI-operationer, som
  går gennem D005-gatewayen, inklusive eksisterende V2 og nye V3-kald
- gemmer mindst service, operation, scope, creation metadata og den
  relevante request-/priority-policy-identitet
- grupperer alle primary-, retry- og fallback-attempts for samme
  logical request

`research_requests`
- 1:1 extension med `request_id` som både primary key og foreign key til
  `ai_requests`
- bruges kun når requestet er Candidate Review, Deep Research,
  Independent Second Opinion eller anden eksplicit V3-researchtype
- gemmer researchtype, instrument/opportunity/profile og
  research-specifik kontraktmetadata

`research_request_events`
- immutable request-state-events med foreign key til `research_requests`,
  herunder terminal `FAILED_GENERATION`
- en current-state projection må rebuildes fra events

`model_route_decisions`
- primary key `model_route_decision_id`
- refererer til det relevante `ai_requests.request_id`
- immutable konkret routebeslutning med policyversion,
  `quality_class`, `priority_class`, provider/requested model,
  `effective_route_hash`, capability/fallback-resultat og reason codes

`budget_fx_snapshots`
- D005s immutable budget-FX-records med
  `budget_fx_snapshot_id`
- fysisk og semantisk adskilt fra `investment_fx_snapshots`

D005s logical immutable `generation_attempt` realiseres fysisk som to
immutable records under samme stabile `generation_attempt_id`, fordi
IDet skal committes og budgetbindes før provider-kaldet, mens
slutresultat/usage først kendes bagefter.

`generation_attempt_authorizations`
- primary key `generation_attempt_id`
- foreign keys til `ai_requests`, `budget_reservations`,
  `input_packages` og `model_route_decisions`
- gemmer `attempt_number` samt alle input-, route-, pris-/FX-,
  prompt-/response-/generation-/tool-/research-kontrakter og andre
  felter, som skal være låst før provider-kaldet
- gemmer provider, requested model, `started_at` som det committed
  pre-call start-/authorization-tidspunkt og den konservative
  cost-basis-reference
- oprettes immutable i den transaktion, som binder reservationen og
  autoriserer providerforsøget
- kan derfor repræsentere både V2- og V3-providerforsøg under den globale
  D005-budgetcontroller

`generation_attempt_contract_refs`
- child/join-table til `generation_attempt_authorizations`
- indeholder alle variable kontraktreferencer, herunder tool-, research-
  og andre outputpåvirkende kontrakter
- de eksplicitte D005-versionfelter bevares fortsat som relationelle
  kolonner, hvor kontrakten kræver dem

`generation_attempts`
- primary key og foreign key er samme `generation_attempt_id` som den
  tilhørende `generation_attempt_authorizations`-record
- er den immutable completion/outcome-del af D005s logical
  generation-attempt og må højst indsættes én gang
- gemmer mindst `finished_at`, attempt-resultat/reason codes,
  resolved response-model, provider response-ID, usage-reference og
  output-hash, når de er tilgængelige
- manglende completion-record efter crash må aldrig få en STARTED
  reservation til at blive frigivet; den håndteres konservativt gennem
  D005 settlement/reconciliation
- authorization-recorden og completion-recorden udgør tilsammen den
  logical immutable `generation_attempt`, som D005 kræver; ingen af dem
  må opdateres in place efter commit

`ai_usage_events`
- immutable provider-/usage-records med stabil usage-identitet
- refererer til `generation_attempt_id`
- dublerede/delayed provider-events skal kunne deduplikeres uden at
  omskrive et tidligere event

`research_reports`
- primary key `research_report_id`
- foreign keys til instrument, eventuel opportunity,
  `input_package_id`, `model_route_decision_id` og
  `generation_attempt_id`
- report-type/role, validity horizon, output hash og de D004/D005-
  krævede kontraktfelter gemmes relationelt
- selve Candidate Review/Deep Research/Second Opinion-outputtet gemmes
  som immutable schema-valideret JSON

`research_reconciliations`
- primary key `research_reconciliation_id`
- foreign keys til præcis én primary-report og én second-opinion-report
- gemmer reconciliation-policy, evaluated-at, `alignment_status` og
  immutable result/check payload
- rapporterne omskrives aldrig af reconciliation

`report_validity_assessments`
- primary key `report_validity_assessment_id`
- foreign keys til research-report, freshness-context og den
  inputpakke, rapporten vurderes imod
- gemmer policyversion, evaluated-at og validity-status

`ai_cache_entries`
- persistent pre-call lookup-index til allerede eksisterende gyldige
  immutable researchreports
- cache-entry må ikke være den eneste kopi af rapporten
- cache-scope skal kunne håndhæve D004/D005s versionerede
  kompatibilitetsregler og må ikke tælle som ny generation

##### Globalt AI-budgetledger

`budget_periods`
- primary key `budget_period_id`
- gemmer periodegrænser og policy/timezone-reference
- settled spend må kunne rekonstrueres fra canonical settlementrecords;
  eventuelle cached totals er projections, ikke eneste source of truth

`budget_reservations`
- primary key `reservation_id`
- unique logical `reservation_key`
- foreign keys til `budget_periods`, `ai_requests`,
  `model_route_decisions` og `budget_fx_snapshots`
- gemmer alle D005-required admissionfelter, herunder
  `reserved_dkk_micros`, den aktuelle `state`, `state_version`,
  `created_at`, `expires_at` og relevante transition-timestamps
- current state må kun ændres gennem D005s tilladte transitioner med
  compare-and-set/versionkontrol; ubeskyttet last-write-wins er forbudt

`budget_reservation_cost_components`
- immutable pre-call cost-basis-records med foreign key til
  `budget_reservations`
- beskriver hver konservativt reserveret attempt-/route-komponent med
  mindst attempt-slot/scenario, relevant `price_catalog_entry`,
  route/effective-route-identitet, estimerede maksimale inputtokens,
  maksimalt outputbudget, maksimale reasoning/tool/other costs,
  sikkerhedsmargin og `component_reserved_dkk_micros`
- komponenterne skal gøre `reserved_dkk_micros` reproducerbart og
  dokumentere, hvad en samlet reservation faktisk dækker
- hvis reservationen på forhånd dækker flere tilladte betalte attempts,
  skal alle disse være repræsenteret i den immutable cost basis

`budget_reservation_events`
- immutable state-transition/audit-events for
  `RESERVED`, `STARTED`, `SETTLED`, `RELEASED`, `EXPIRED` og
  `UNRESOLVED`
- eventhistorikken skal kunne validere/rebuildere reservationens
  canonical current-state head og dokumentere alle transitioner
- `STARTED`-relaterede events skal kunne referere til det konkrete
  `generation_attempt_id`, som bindes før provider-kaldet

`budget_reservation_attempt_bindings`
- immutable relation mellem reservation og faktisk
  `generation_attempt_id`
- oprettes i den transaktion, der autoriserer det konkrete attempt til
  at starte
- refererer til den cost-basis-komponent/attempt-slot, som forsøget
  forbruger, når en samlet reservation dækker flere attempts
- samme generation-attempt må ikke bindes til flere reservationer, og
  bindings må aldrig kunne få samlet dækket eksponering til at overstige
  reservationens konservative cost basis

`budget_settlements`
- immutable settlementrecords
- refererer til reservation, `generation_attempt_id` og usage-event
- gemmer faktisk settled beløb i `*_dkk_micros` og den verificerede
  pris-/FX-basis

`budget_reconciliations`
- immutable auditrecords for unresolved exposure, corrections og
  integritetsafvigelser
- tidligere settlement/reservation events omskrives ikke

##### Alerts, jobs og coordination

`alert_outbox`
- primary key for logical alert/outbox-record
- foreign key til `status_transition_id`
- gemmer alert-type, channel, committed-at og delivery-state/projection
  efter D006s senere state-kontrakt

D004s logical immutable alert-delivery-attempt realiseres fysisk som
en immutable pre-send authorization og en separat immutable completion,
så et crash omkring et eksternt send ikke kræver in-place mutation.

`alert_delivery_attempt_authorizations`
- primary key `delivery_attempt_id`
- foreign key til `alert_outbox`
- gemmer positivt `attempt_number`, channel/provider,
  delivery-/retry-policyversion, `authorized_at` og eventuel
  provider-idempotency-key, når kanalen understøtter den
- oprettes og committes før det eksterne delivery-kald

`alert_delivery_attempts`
- primary key og foreign key er samme `delivery_attempt_id` som den
  tilhørende authorization
- immutable completion-record, som må indsættes højst én gang
- gemmer `finished_at`, resultat/reason codes og ekstern
  delivery/reference-ID, når tilgængelig

`alert_delivery_reconciliations`
- immutable auditrecords for et autoriseret delivery-attempt, hvor
  processen ikke sikkert ved, om den eksterne side effect skete
- resultatet skal mindst kunne skelne mellem dokumenteret leveret,
  dokumenteret ikke leveret og fortsat ukendt
- reconciliation må ikke omskrive authorization eller completion

`job_runs`
- primary key `job_run_id`
- oprettes før jobbet starter og gemmer jobtype, scope,
  `current_run_state`, `state_version`, `started_at` og eventuel
  `finished_at`
- current-state head må kun ændres gennem eksplicitte tilladte
  compare-and-set/versionerede transitioner
- terminale run-states må ikke genåbnes eller omskrives stiltiende

`job_run_events`
- immutable audit-events for job-run-start, completion, failure,
  cancellation og andre versioneret tilladte run-transitioner
- eventhistorikken skal kunne validere job-run-headens state og
  tidsstempler

`job_leases`
- primary key `lease_key` identificerer den eksklusive ressource/jobtype
- er en persistent mutable head og må ikke slettes/recreates i normal
  runtime, fordi fencing-generationen skal overleve release/reacquire
- gemmer mindst `lease_state`, owner-token, `fencing_token`,
  `state_version`, `acquired_at`, `expires_at` og eventuel `released_at`
- `lease_state` er mindst `ACTIVE` eller `RELEASED`
- release ændrer head til `RELEASED`, men bevarer den senest anvendte
  fencing-generation

`job_lease_events`
- immutable audit-events for `ACQUIRE`, `RENEW`, `RELEASE` og
  `TAKEOVER`
- gemmer lease-key, event-sequence, owner/fencing-generation,
  resulting state/version, timestamp og reason codes
- eventhistorikken skal gøre release/reacquire og takeover auditerbar
  uden at nulstille lease-headens fencing history

`schema_migration_control`
- singleton mutable head for V3-store med stabil control-key
  `aureum_v3`
- gemmer mindst `write_mode`, `state_version`, eventuel aktiv
  migration-ID/checksum, migration-lease-key/fencing-token og relevante
  timestamps
- `write_mode` er mindst `NORMAL`, `QUIESCED` eller `MIGRATING`

`schema_migration_control_events`
- immutable audit-events for barrier-/migration-control-transitioner
- skal kunne validere den mutable migration-control-head

`schema_migrations`, `schema_migration_verifications`,
`migration_backfills` og `migration_backfill_events` er ligeledes
canonical V3-records og konkretiseres i D006.6.

Afledte dashboard-/JSON-caches, current-state projections og cached
aggregates kan oprettes for performance, men de skal kunne rebuildes fra
de canonical records og må ikke være eneste kopi af score, gate,
lifecycle, research, outbox eller budgetstate.

Foreign keys skal bruges for alle relationer inden for V3-databasen,
hvor target-recorden er canonical og begge records skal eksistere
samtidigt. Audit-/historikrecords skal som udgangspunkt ikke slettes via
cascading deletes. D006.3 fastlægger de konkrete UNIQUE-, CHECK-,
foreign-key- og idempotency-constraints.

#### D006.3 PK/FK/UNIQUE/CHECK og idempotency

Databaseconstraints er en del af correctness-kontrakten og ikke kun en
performanceoptimering. Invarianter, som SQLite kan håndhæve med primary
keys, foreign keys, UNIQUE/CHECK constraints eller partial unique
indexes, skal som udgangspunkt håndhæves i databasen.

Cross-row-regler, som ikke sikkert kan udtrykkes med almindelige
constraints, skal håndhæves i en eksplicit beskyttet transaktion og,
hvor det giver væsentlig ekstra integritet, med en snævert scoped
database-trigger. Kritiske gates, budget- og lifecycle-invarianter må
ikke afhænge af en ubeskyttet read-then-write-sekvens i application
code.

Alle canonical foreign keys i V3 bruger `ON DELETE RESTRICT` eller
tilsvarende `NO ACTION` som udgangspunkt. Immutable audit-, gate-,
research-, lifecycle-, budget- og delivery-records må ikke forsvinde
gennem cascading delete. `ON DELETE CASCADE` er kun tilladt for rent
afledte/rebuildable child-records, når retention-kontrakten udtrykkeligt
tillader det.

`contract_versions` skal have en stabil `contract_ref_id` som primary
key samt:

`UNIQUE(contract_kind, contract_version)`

Alle relationelle contract-/policy-referencer skal pege på denne
immutable identitet eller på en specialiseret immutable child-record,
som selv refererer til `contract_versions`.

Alle join-tables skal have composite primary key eller tilsvarende
UNIQUE constraint, så samme relation ikke kan indsættes to gange.

##### Generelle CHECK-regler

Mindst følgende skal håndhæves:

- stabile ID-felter må ikke være tomme strings
- tokenantal, attempt-numre, sequence-numre, state-versioner og
  `*_dkk_micros` må ikke være negative
- tællere/attempt-numre, som starter ved 1, skal være `>= 1`
- `valid_until`, `expires_at` og `finished_at` må ikke ligge før deres
  relevante start-/evaluationstidspunkt
- alias `valid_until` skal være `NULL` eller senere end `valid_from`
- canonical enumfelter bruger CHECK-constraints for de værdier, der er
  låst i D002-D005
- nullable felter med variantsemantik skal have CHECK-regler, så
  ugyldige kombinationer ikke kan gemmes

Timestamp-format og timezone-normalisering valideres før write efter
D006.2s canonical UTC-kontrakt. Databasen må ikke acceptere et
server-lokalt tidspunkt som implicit erstatning for et manglende
canonical timestamp.

Authoritative decimaler for price/FX må ikke gemmes som SQLite `REAL`.
D006-implementeringen skal bruge en lossless scaled-integer eller
rational representation. Hvis scaled integer bruges, gemmes mindst
integer-value og decimal-scale; hvis rational representation bruges,
skal denominator være positiv. Konverteringen til
`*_dkk_micros` skal være deterministisk og versionsbundet.

##### Instrumenter og aliases

`instruments.instrument_id` er primary key.

`instrument_aliases` skal mindst forhindre identiske dubletter gennem
en scoped uniqueness-regel over alias/provider/symbol og validity-start.

Overlappende validity-perioder, som ville gøre samme provider-symbol
tvetydigt for samme instrument eller mappe samme entydige provider-
identitet til flere instruments samtidig, skal afvises i den
transaktion, der skriver aliaset. En tickerændring må ikke løses ved at
overskrive det historiske alias.

##### Retrieval og snapshots

`retrieval_attempts` skal mindst have:

`UNIQUE(retrieval_plan_id, attempt_number)`

En rå payload/manifest-record skal have en stabil scoped idempotency key
bundet til faktisk provider/retrieval-attempt og payload content hash,
så retry af samme providerresultat ikke skaber en ny semantisk payload.

D004s provider-snapshot-key håndhæves med en UNIQUE constraint eller
partial unique index svarende til:

`(provider_id, instrument_id, data_subtype, observed_at, content_hash)`

for `snapshot_kind = PROVIDER`.

D004s normalized-snapshot-key håndhæves tilsvarende som:

`(instrument_id, data_subtype, observed_at, normalization_version, source_set_hash)`

for `snapshot_kind = NORMALIZED`.

`data_snapshots` skal have CHECK-regler, så:

- `snapshot_kind` kun er `PROVIDER` eller `NORMALIZED`
- PROVIDER kræver relevante provider-/content-identitetsfelter
- NORMALIZED kræver `normalization_version` og `source_set_hash`
- variant-specifikke felter ikke kan danne en semantisk ugyldig hybrid
- `available_at` ikke ligger før `observed_at`

`normalized_snapshot_sources` skal mindst have:

`PRIMARY KEY(normalized_snapshot_id, source_snapshot_id)`

og må kun forbinde en normalized parent med gyldige source snapshots.
Denne snapshot-kind-invariant skal valideres transaktionelt eller med en
snævert scoped trigger.

`field_provenance` skal have en scoped uniqueness-regel, som mindst
dækker normalized snapshot, target field/path, source snapshot,
source field/path og transformation-identitet. Flere forskellige
sources til samme derived target field skal fortsat være tilladt.

##### Freshness og inputpakker

D004s freshness-idempotency håndhæves som:

`UNIQUE(snapshot_id, evaluated_at, freshness_policy_version, freshness_context_id)`

D004s input-package-idempotency håndhæves som:

`UNIQUE(purpose, contract_version, input_hash)`

Join-tables for freshness contexts og input packages skal bruge
composite keys, så samme snapshot/assessment/contract-ref ikke kan
refereres to gange fra samme parent.

Et uniqueness-hit på `input_hash` er kun et succesfuldt idempotent retry,
hvis eksisterende package-manifest og relationelle refs er semantisk
identiske. Samme hash med modstridende semantic content er en
integritetsfejl og må aldrig behandles som cache-hit.

##### Opportunity, gates og lifecycle

`opportunity_profile` begrænses til:

- `COMPOUNDER`
- `CATALYST`

`current_lifecycle_status`, `from_status` og `to_status` begrænses til
de D003-lifecycle-states, som er låst i blueprintet.

Et `gate_evaluations`-record skal med composite FK eller tilsvarende
databasevalidering sikre, at `instrument_id` og
`opportunity_profile` matcher den refererede opportunity.

Gate-resultat begrænses til:

- `PASS`
- `FAIL`
- `BLOCKED_DATA`

`execution_mode` begrænses til:

- `SHADOW`
- `LIVE`

D004s gate-idempotency håndhæves som:

`UNIQUE(opportunity_id, target_status, gate_basis_hash, gate_policy_version)`

D004s lifecycle-transition-key håndhæves som:

`UNIQUE(opportunity_id, gate_evaluation_id, from_status, to_status)`

En lifecycle-transition må ikke referere til en gate for en anden
opportunity. Transitionens `from_status` skal matche den canonical
current-state head på commit-tidspunktet. Den invariant håndhæves i den
samme CAS-beskyttede transaktion, som opdaterer
`opportunities.current_lifecycle_status`.

`lifecycle_state_version` skal stige monotonisk præcis én version pr.
committed transition.

Qualification-label-events skal have en stabil scoped idempotency key,
som mindst binder opportunity, label, action og den immutable basis for
ændringen. Label-action begrænses mindst til `ASSIGN` og `REMOVE`.
Labels må ikke ændre lifecycle-head direkte.

Confirmation evidence skal have en scoped semantic idempotency key, så
samme underliggende evidens ikke kan indsættes flere gange og derved
bruges som falsk uafhængig bekræftelse.

##### AI requests, routing, attempts og research

`ai_requests.request_id` er D005s globale logical-request-idempotency.
Retry af samme logical request skal genbruge samme `request_id`.

`research_requests.request_id` er både primary key og foreign key til
`ai_requests.request_id`.

`model_route_decisions` skal have en stabil scoped
`route_decision_key`, som er UNIQUE og gør et retry af samme konkrete
routingbeslutning idempotent, men stadig tillader en ny immutable
decision med en ny key ved legitim fallback/re-routing.

`generation_attempt_authorizations` skal have et positivt
`attempt_number` og mindst:

`UNIQUE(request_id, attempt_number)`

Et nyt paid retry/fallback skal derfor have en ny immutable
authorization med et nyt attemptnummer under samme logical `request_id`.

`generation_attempts.generation_attempt_id` er både primary key og
foreign key til authorization-recorden, så samme autoriserede
providerforsøg højst kan få én canonical completion-record.

Et `generation_attempt_id` må højst bindes til én budgetreservation.
Dette håndhæves gennem UNIQUE constraint på
`budget_reservation_attempt_bindings.generation_attempt_id`, og
bindingens foreign key peger på
`generation_attempt_authorizations.generation_attempt_id`.

Hvis cost-basis-tabellen repræsenterer konkrete attempt-slots, skal den
samme slot højst kunne forbruges én gang gennem en UNIQUE constraint på
den relevante cost-component/slot reference.

`research_reports` skal mindst sikre, at samme generation-attempt ikke
kan producere parallelle canonical rapportdubletter for samme
report-role/type. Et retry/repair, der kan skabe en ny rapport, skal
have et nyt `generation_attempt_id`.

Report-type begrænses mindst til:

- `CANDIDATE_REVIEW`
- `DEEP_RESEARCH`
- `SECOND_OPINION`

Research-role begrænses mindst til:

- `PRIMARY`
- `INDEPENDENT_SECOND_OPINION`

En SECOND_OPINION skal have den D004-krævede independent role og må ikke
referere til samme generation-attempt/reportidentitet som den primære
rapport.

`research_reconciliations` skal have en scoped immutable
reconciliation-key, som binder primary-report, second-opinion-report,
reconciliation-policy og den øvrige immutable reconciliation-basis.
Primary og second-opinion report-ID må ikke være ens.

`alignment_status` begrænses til:

- `ALIGNED`
- `MATERIAL_CONTRADICTION`
- `INCONCLUSIVE`

`report_validity_assessments` skal have scoped idempotency over mindst
research-report, evaluationstidspunkt, validity-policy,
freshness-context og inputpakken, som rapporten vurderes imod.

Validity-status begrænses til:

- `VALID`
- `EXPIRED`
- `INVALIDATED`

`ai_usage_events` skal have en stabil `usage_event_key`.
Når provideren leverer en stabil usage/event-ID, indgår denne i nøglen.
Uden provider-ID dannes nøglen deterministisk fra
generation-attempt/provider og det normaliserede immutable usage-
payload. Forsinket eller dubleret usage må ikke afregnes dobbelt.

AI-cache skal have en deterministisk `cache_scope_key`, der dækker hele
det pre-call cache-scope låst i D004/D005. Nøglen skal være UNIQUE.
Et key-hit må kun genbruges efter exact scope-/compatibility-
verifikation; hash/key-lighed alene må ikke skjule en semantic mismatch.

##### Budgetledger

`budget_periods` skal have præcis én canonical record pr.
kalenderperiode og budget-timezone, fx gennem:

`UNIQUE(period_start, period_end, budget_timezone)`

En ændring af `budget_policy_version` midt i en måned må ikke oprette en
ny parallel budgetperiode eller nulstille månedens allerede forbrugte
eksponering. Den aktive policy ved den konkrete admission gemmes på
reservationen, mens alle reservationer og settlements i samme
kalendermåned fortsat tilhører samme `budget_period_id`.

`budget_reservations.reservation_key` er UNIQUE og er D005s
reservations-idempotency-nøgle.

`budget_reservations.state` begrænses til:

- `RESERVED`
- `STARTED`
- `SETTLED`
- `RELEASED`
- `EXPIRED`
- `UNRESOLVED`

`reserved_dkk_micros` skal være `>= 0`, og `state_version` skal være
`>= 0`.

Hver `budget_reservation_cost_components`-record skal have en stabil
component/slot-key med:

`UNIQUE(reservation_id, component_key)`

Summen af reservationens immutable cost components inklusive den
konservative sikkerhedsmargin skal ved admission deterministisk svare
til reservationens `reserved_dkk_micros`. Da en cross-row sum ikke kan
håndhæves med almindelig CHECK, valideres dette inde i den samme
`BEGIN IMMEDIATE`-transaktion før reservationen committes.

I samme `BEGIN IMMEDIATE`-transaktion skal budgetcontrolleren beregne
periodens canonical D005-eksponering og kontrollere:

`current_period_exposure + new_reserved_dkk_micros <= active_hard_cap_dkk_micros`

Eksponeringen beregnes fra canonical reservations-, settlement- og
reconciliation-records efter D005s state-semantik; cached aggregates må
ikke være eneste grundlag for admission.

`RESERVED` og `STARTED` bidrager mindst med deres fulde konservative
reservation, `UNRESOLVED` med mindst den senest konservativt kendte
eksponering, `SETTLED` med den canonical faktisk afregnede eksponering,
og `RELEASED`/`EXPIRED` med nul. Allerede registreret faktisk
eksponering over reservationen må aldrig skjules af den oprindelige
reservation.

Den atomiske hard-cap-kontrol skal ske før INSERT/commit af den nye
reservation, så to samtidige admissions ikke begge kan bestå på samme
forældede budgettal.

`budget_reservation_events` skal have monotonisk event-sequence og:

`UNIQUE(reservation_id, event_sequence)`

Eventet, som dokumenterer overgang til `STARTED`, skal referere til den
samme `generation_attempt_id`, som oprettes/bindes i starttransaktionen.

`budget_reservation_attempt_bindings` skal mindst håndhæve:

- `UNIQUE(generation_attempt_id)`
- uniqueness af den konkrete cost-component/attempt-slot, når denne kun
  må forbruges én gang

Når én reservation konservativt dækker flere mulige betalte attempts,
forbliver reservationen `STARTED`, mens mindst ét faktisk startet/bundet
attempt endnu ikke er endeligt afregnet, og så længe ingen
D005-betingelse kræver `UNRESOLVED`.

Reservationen må først gå til `SETTLED`, når alle faktisk startede
attempts under reservationen har canonical settlement/reconciliation,
ingen unresolved betalingsusikkerhed er tilbage, og ubrugt reserveret
kapacitet kan frigives som en del af finaliseringen.

Et pre-reserveret attempt-slot, som aldrig blev startet, kræver ikke et
fiktivt settlement. `RELEASED` eller `EXPIRED` må derimod kun anvendes
på en reservation, hvor intet betalingsudløsende providerforsøg
startede.

Hvis betalingsstatus for et startet attempt bliver uklar, følger
reservationen D005s `UNRESOLVED`-semantik. En `UNRESOLVED` reservation
må ikke autorisere et nyt providerforsøg, fordi D005-state machine kun
tillader auditerbar reconciliation videre til `SETTLED`.

`budget_settlements` skal være idempotente. Ét
`generation_attempt_id` må højst have ét canonical initial settlement.
Senere korrektioner må kun ske gennem immutable
`budget_reconciliations`, ikke ved at omskrive settlementet.

Settlementbeløb må ikke klippes til reservationen og skal være
ikke-negative integer DKK micros.

`budget_reconciliations` skal have en stabil reconciliation-key, så
samme provider-/usage-/integritetsbevis ikke kan anvendes flere gange
som separate korrektioner.

##### Alerts og jobs

D004s alert-outbox-idempotency håndhæves som:

`UNIQUE(status_transition_id, alert_type, channel)`

`alert_delivery_attempt_authorizations` skal mindst have:

`UNIQUE(alert_outbox_id, attempt_number)`

`alert_delivery_attempts.delivery_attempt_id` er både primary key og
foreign key til authorization-recorden, så ét autoriseret send højst
kan få én canonical completion.

En ekstern provider-delivery-ID, når den er stabil og tilgængelig, skal
også være scoped UNIQUE for den relevante channel/provider, så samme
providerkvittering ikke kan registreres som flere leveringer.

Et autoriseret delivery-attempt uden completion skal behandles som
delivery-ambiguitet. Aureum må ikke automatisk starte et nyt send, hvis
det kan skabe en dublet, medmindre providerens aktive kontrakt giver en
dokumenteret idempotency-mekanisme, eller auditerbar reconciliation har
fastslået, at det tidligere send ikke blev leveret.

`alert_delivery_reconciliations` skal have en stabil scoped
reconciliation-key, så samme eksterne evidens ikke kan anvendes som
flere uafhængige resolutioner.

`job_runs.job_run_id` er stabilt for ét logical run.

`job_run_events` skal have:

`UNIQUE(job_run_id, event_sequence)`

Job-run state/version skal kun ændres gennem tilladte CAS-beskyttede
transitioner.

`job_leases.lease_key` er primary key for den eksklusive ressource.

`lease_state` begrænses til:

- `ACTIVE`
- `RELEASED`

Efter første acquisition skal `fencing_token` være positivt og må aldrig
gå baglæns eller genbruges for samme `lease_key`.
`state_version` skal være ikke-negativ.

En `ACTIVE` lease skal have ikke-tomt owner-token og en expiry senere
end acquisition/seneste gyldige renewal-basis.

En `RELEASED` lease skal bevare sin seneste fencing-generation og have
`released_at`; release må ikke implementeres som DELETE.

`job_lease_events` skal mindst have:

`UNIQUE(lease_key, event_sequence)`

Event-sequence og resulting state-version skal stige monotonisk.
Event-type begrænses mindst til `ACQUIRE`, `RENEW`, `RELEASE` og
`TAKEOVER`.

Et lease-retry med samme logical owner/acquisition-basis må ikke skabe
et nyt parallelt lease-record eller en ny fencing-generation, hvis den
oprindelige transaction allerede committed.

##### Idempotency conflict semantics

For enhver UNIQUE/idempotency-konflikt gælder:

1. writeren læser den eksisterende canonical record i samme beskyttede
   workflow
2. den sammenligner de semantiske felter, immutable refs og relevante
   hashes med det ønskede write
3. ved semantisk identitet returneres den eksisterende record som
   idempotent succes
4. ved semantic mismatch returneres en eksplicit integrity/conflict
   error
5. mismatch må aldrig løses ved `INSERT OR REPLACE`, silent overwrite
   eller last-write-wins

`INSERT OR REPLACE` er forbudt for canonical V3-records, fordi SQLite
ellers kan implementere operationen som delete+insert og dermed bryde
foreign keys, auditidentitet eller immutable historik.

#### D006.4 Mutable state, state machines og atomiske transaktionsgrænser

V3 er immutable-first. Mutable canonical state er kun tilladt, når
runtime skal kunne afgøre den aktuelle operative tilstand uden at
genspille hele historikken for hvert write.

Mindst følgende canonical heads må være mutable:

- `opportunities.current_lifecycle_status` med
  `lifecycle_state_version`
- `budget_reservations.state` med `state_version`
- `alert_outbox.delivery_state` med `delivery_state_version`
- `job_runs.current_run_state` med `state_version`
- `job_leases` som eksplicit coordination-state
- `schema_migration_control.write_mode` med `state_version`
- `migration_backfills` som eksplicit resumable migration-coordination

Alle øvrige D004/D005 audit-, snapshot-, input-, gate-, research-,
generation-, reconciliation-, settlement-, transition-, event- og
delivery-attempt-records er immutable efter commit, medmindre D006s
retention-/migration-kontrakt senere eksplicit fastlægger en kontrolleret
maintenance-operation.

Et mutable head må aldrig ændres uden:

1. eksplicit forventet current state
2. forventet state-version
3. versioneret transitionregel
4. immutable audit-/transitionrecord i samme transaktion, når en sådan
   recordtype findes
5. row-count/CAS-verifikation af, at præcis den forventede head blev
   ændret

Et CAS-miss er en concurrency-conflict og må ikke løses ved blind retry
af det oprindelige write. Writet skal genlæse canonical state og
genvalidere hele transitionen.

State-version starter ved en dokumenteret initialværdi og øges præcis én
gang pr. committed canonical state-transition. Version må ikke springe,
gå baglæns eller genbruges.

##### Lifecycle-state machine

D003s lifecycle states er den eneste tilladte business-state machine for
Opportunity lifecycle. D006 tilføjer ingen nye lifecycle-statusser.

Gate-evalueringen oprettes som immutable og side-effect-free record før
en eventuel lifecycle-transition.

En lifecycle-transition udføres i én kort `BEGIN IMMEDIATE`-transaktion,
som mindst:

1. læser opportunity-head og `lifecycle_state_version`
2. læser den bindende immutable gate-evaluation
3. verificerer, at gate-evaluation tilhører samme opportunity,
   instrument/profile og forventede `from_status`
4. verificerer, at gate-resultat, execution-mode og target-status
   faktisk tillader transitionen efter D002-D004
5. verificerer, at gaten fortsat er gyldig på commit-tidspunktet
6. genvaliderer relevante invalidation-/policyreferencer, som D004
   kræver ved transition
7. opretter præcis én immutable `lifecycle_transitions`-record
8. opdaterer `opportunities.current_lifecycle_status` og
   `lifecycle_state_version` med CAS
9. opretter eventuel required `alert_outbox`-record i samme transaktion
10. committer alle tre effekter samlet eller ingen af dem

`execution_mode = SHADOW` må aldrig skabe en LIVE lifecycle-transition
eller alert-outbox, selv hvis gate-resultatet ellers er `PASS`.

En transition til `HIGH_CONVICTION` må kun committed, når den bindende
gate opfylder de allerede låste D002/D004-krav. D006 må ikke
rekonstruere eller svække gatekravene.

Hvis en idempotent retry finder den allerede committed semantisk
identiske transition og eventuelle outbox-record, returneres disse som
succes uden ny transition, state-version eller alert.

Hvis opportunity-head har ændret sig siden gate-evalueringen, må en
gammel transition ikke tvinges igennem. Casen skal genvurderes efter
D003/D004.

##### Alert-outbox state machine og ekstern levering

`alert_outbox.delivery_state` er en operativ mutable head og er ikke
selve dokumentationen for, om en ekstern levering fandt sted.
Authorization-, completion- og reconciliation-records er canonical
audit.

Mindst følgende fysiske delivery states anvendes:

- `PENDING`
- `AUTHORIZED`
- `DELIVERED`
- `RETRYABLE`
- `AMBIGUOUS`
- `DEAD_LETTER`

Disse er persistence-/delivery-states og må ikke forveksles med D003
lifecycle-status.

Normale transitioner er mindst:

- `PENDING` -> `AUTHORIZED`
- `RETRYABLE` -> `AUTHORIZED`
- `AUTHORIZED` -> `DELIVERED`
- `AUTHORIZED` -> `RETRYABLE`, kun når det kan dokumenteres, at den
  eksterne side effect ikke blev gennemført
- `AUTHORIZED` -> `AMBIGUOUS`, når leveringsstatus ikke kan bevises
- `RETRYABLE` -> `DEAD_LETTER` efter aktiv retry-policy
- `AMBIGUOUS` -> `DELIVERED`, når reconciliation beviser levering
- `AMBIGUOUS` -> `RETRYABLE`, når reconciliation beviser ikke-levering
- `AMBIGUOUS` -> `DEAD_LETTER`, når policy kræver manuel/terminal
  håndtering frem for risiko for dublet

`DELIVERED` og `DEAD_LETTER` er terminale for den logical outbox-record
og må ikke genåbnes stiltiende.

Et delivery-worker-claim udføres i en kort `BEGIN IMMEDIATE`-
transaktion:

1. vælg en eligible `PENDING`/`RETRYABLE` outbox-record
2. verificér current delivery-state/version
3. verificér at ingen unresolved/ambiguous authorization allerede
   blokerer nyt send
4. beregn næste positive attempt-number
5. opret immutable `alert_delivery_attempt_authorizations`
6. opdater outbox-head til `AUTHORIZED` med CAS
7. commit

Det eksterne Telegram/provider-kald sker altid efter commit og uden en
åben SQLite write-transaction.

Efter providerresultatet åbnes en ny kort transaktion, som:

- indsætter den immutable `alert_delivery_attempts` completion-record,
  når udfaldet er kendt
- eller opretter/markerer reconciliation-behov ved betalings-/delivery-
  ambiguitet
- opdaterer outbox-head med CAS til den dokumenterede operative state
- aldrig opretter en ny logical outbox-record for samme
  `(status_transition_id, alert_type, channel)`

Et crash efter authorization men før sikker completion behandles som
delivery-ambiguitet, medmindre providerens versionerede kontrakt giver
en verificerbar idempotency-/statusmekanisme, som entydigt kan
reconciles.

En recovery-worker må aldrig sende direkte fra en efterladt
`AUTHORIZED` state. Den skal først inspicere authorization-recorden og
eventuel provider-idempotency-/statusmekanisme:

- dokumenteret levering kan reconciles og CAS-transitionere
  `AUTHORIZED` -> `DELIVERED`
- dokumenteret ikke-levering kan reconciles og CAS-transitionere
  `AUTHORIZED` -> `RETRYABLE`
- fortsat ukendt status skal oprette immutable reconciliation-basis og
  CAS-transitionere `AUTHORIZED` -> `AMBIGUOUS`

Den relevante reconciliation-record og outbox-head-transition skal
committes atomisk. Et `AUTHORIZED` eller `AMBIGUOUS` attempt er ikke
eligible til et nyt send, før den ovenstående recovery/reconciliation
har gjort næste handling sikker.

Aureum må ikke vælge availability frem for dedup-sikkerhed ved
ambiguous irreversible side effects. Ved tvivl blokeres nyt send,
indtil reconciliation eller manuel policyafgørelse gør næste handling
sikker.

##### Budget admission

Budget-admission anvender én kort `BEGIN IMMEDIATE`-transaktion.

Før transaktionen må Aureum beregne stabilt `request_id`, candidate
route, den foreslåede immutable route-decision, tokenestimat,
price/FX-basis og cost components lokalt. Routingbeslutningen skal være
logisk afsluttet før budgetreservationen, men request- og
route-decision-records må persistéres i samme atomiske
admission-transaktion som reservationen.

Admission-transaktionen skal mindst:

1. idempotent oprette eller hente relevant `ai_requests`-record
2. idempotent oprette eller hente den semantisk identiske immutable
   `model_route_decision` via den scoped UNIQUE `route_decision_key`
3. verificere, at route-decision tilhører samme request og fortsat
   opfylder den aktive route-/capability-policy
4. fastlægge canonical admission-tidspunkt og finde/oprette præcis én
   `budget_period_id` for den relevante `Europe/Copenhagen`-
   kalendermåned
5. genvalidere price catalog, budget-FX, budget-/priority-policy og
   cost basis
6. beregne periodens canonical exposure
7. kontrollere, at ingen aktiv unresolved budget-integritetsafvigelse
   blokerer nye paid admissions
8. kontrollere zone-, priority- og hard-cap-regler
9. kontrollere at cost components summerer deterministisk til
   `reserved_dkk_micros`
10. oprette præcis én `budget_reservations`-record i `RESERVED`
11. oprette alle immutable `budget_reservation_cost_components`
12. oprette reservationens initiale audit/event-record
13. committe samlet

Hvis `reservation_key` allerede findes, må transaktionen kun returnere
den eksisterende reservation som idempotent succes, når alle relevante
semantic admissionfelter og cost components matcher.

En budgetafvisning opretter ikke en falsk aktiv reservation. Hvis
`ai_requests` eller `model_route_decision` kun blev staged som del af
den afviste admission-transaktion, rulles disse nye writes tilbage
sammen med reservationen. Eventuel audit af rejection skal være en
separat recordtype/log, som ikke tæller som exposure og ikke kan
forveksles med en admitted route/reservation.

##### Authorization og start af et paid provider-attempt

Et provider-kald må først starte efter en separat, committed
authorization-transaktion.

For første attempt på en `RESERVED` reservation skal transaktionen
mindst:

1. genlæse reservation og expected `state_version`
2. kontrollere at reservationen stadig tilhører korrekt budgetperiode,
   request, route og gyldig cost basis
3. kontrollere at den valgte attempt-slot er tilladt og ubrugt
4. oprette immutable `generation_attempt_authorizations` med stabilt
   `generation_attempt_id`
5. oprette relevante `generation_attempt_contract_refs`
6. oprette `budget_reservation_attempt_bindings`
7. oprette audit-eventet for den konkrete attempt-authorization
8. transitionere reservation-head `RESERVED` -> `STARTED` med CAS
9. oprette det immutable reservation-state-event for
   `RESERVED` -> `STARTED`, bundet til samme `generation_attempt_id`
10. committe samlet

Først efter denne commit må provider-kaldet starte.

Hvis en allerede `STARTED` reservation lovligt dækker et ekstra paid
retry/fallback-attempt, udføres samme authorization-flow for en ny
ubrugt cost-component/attempt-slot, men reservationens state forbliver
`STARTED`. Der oprettes derfor ikke en falsk `STARTED -> STARTED`
state-transition.

Et ekstra attempt må aldrig autoriseres fra `UNRESOLVED`, `SETTLED`,
`RELEASED` eller `EXPIRED`.

Et crash efter committed authorization behandles konservativt som et
attempt, der kan have kostet penge, selv hvis processen i virkeligheden
nåede at crashe før netværkskaldet.

##### Provider completion, usage og settlement

Provider-resultat og usage gemmes efter provider-kaldet i en ny kort
transaktion.

Når udfaldet kan dokumenteres, skal transaktionen mindst:

1. verificere den eksisterende attempt-authorization/binding
2. indsætte præcis én immutable `generation_attempts`
   completion/outcome-record
3. indsætte/deduplikere relevante immutable `ai_usage_events`
4. beregne canonical faktisk cost fra verificeret usage,
   price-catalog og budget-FX-basis
5. indsætte det idempotente `budget_settlements`-record for attemptet
6. vurdere om reservationen fortsat skal være `STARTED`, eller om hele
   reservationen nu kan finaliseres til `SETTLED`
7. ved finalisering opdatere reservation-head og indsætte immutable
   state-event i samme transaktion
8. committe samlet

Hvis faktisk cost overstiger reservationens konservative basis, gemmes
den fulde faktiske cost. Hændelsen opretter en immutable
budget-integritetsafvigelse/reconciliation-record med stabil scoped
incident-key.

Så længe en sådan integritetsafvigelse ikke har en auditerbar immutable
resolution, er den en canonical global admission-blocker for nye paid
kald. Eventuelle hurtige blocker-/period-projections skal kunne
rebuildes fra incident-/resolution-records og må ikke være eneste source
of truth.

Resolution oprettes som en ny immutable reconciliation-/auditrecord;
den oprindelige settlement, reservation eller incident omskrives ikke.

Hvis provider kan have udført et betalingsudløsende kald, men usage,
response eller pricing ikke kan fastslås sikkert, må Aureum ikke
fabrikere et `SETTLED` resultat.

Hvis selve provider-completion kan dokumenteres sikkert, må den
immutable `generation_attempts` completion-record gemmes med de faktisk
kendte felter, selv om cost endnu er unresolved. Hvis completion ikke
kan bevises, må Aureum heller ikke fabrikere en completion-record.

I den samme beskyttede workflow skal reservationen CAS-transitionere
`STARTED` -> `UNRESOLVED`, og den immutable reservation-state-event
samt reconciliation-basis skal oprettes atomisk med head-opdateringen.
Hvis blot ét startet attempt under en samlet reservation er unresolved,
er hele reservationen `UNRESOLVED` efter D005 og må ikke autorisere
yderligere paid attempts.

Ved service-restart skal alle authorization-records uden sikker
completion/settlement være en del af budget-recovery-scannet. Ingen af
dem må frigive budget alene på alder eller timeout.

##### Budget reconciliation og finalisering

Reconciliation foregår som en særskilt auditerbar workflow.

En `UNRESOLVED` reservation kan kun transitionere til `SETTLED`, når
immutable reconciliation-evidence dokumenterer den korrekte samlede
eksponering for alle startede attempts.

Reconciliation-transaktionen skal mindst:

1. genlæse reservation og alle attempt-bindings
2. deduplikere ny provider-/usage-evidence
3. oprette immutable `budget_reconciliations`
4. oprette eventuelle manglende canonical settlement/correction-
   records efter D005
5. beregne reservationens endelige faktiske exposure
6. verificere at ingen startet attempt fortsat er unresolved
7. CAS-transitionere `UNRESOLVED` -> `SETTLED`
8. oprette immutable state-event
9. committe samlet

Tidligere settlement-, authorization- eller usage-records må aldrig
omskrives for at få reconciliation til at passe.

En reservation i `RESERVED` må kun gå til `RELEASED` eller `EXPIRED`,
når intet paid provider-attempt blev autoriseret/startet.

`EXPIRED` anvendes kun gennem en deterministisk expiry-policy og kun på
fortsat `RESERVED` records. Expiry-worker skal bruge CAS, så den ikke
kan udløbe en reservation samtidigt med en attempt-authorization.

##### Research report og gate-publicering

Et schema-validt AI-output må først blive en canonical
`research_reports`-record efter den tilhørende attempt-completion er
committed og budget/usage-status er håndteret efter D005.

Rapport-publicering må ske i samme transaktion som completion/settlement
eller i en efterfølgende idempotent transaktion, men rapporten skal
referere til den allerede eksisterende immutable
`generation_attempt_id`.

Et invalidt output må gerne have attempt-completion/audit, men må ikke
oprette en canonical gyldig researchrapport.

Reconciliation mellem primary og second opinion sker først, når begge
rapporter eksisterer som immutable canonical records.

Gate-evaluation må aldrig bruge en researchrapport, validity assessment
eller reconciliation, som endnu ikke er committed.

##### Job-run state machine

V3.0 bruger mindst følgende operative `job_runs.current_run_state`:

- `RUNNING`
- `SUCCEEDED`
- `FAILED`
- `CANCELLED`

Et nyt `job_run_id` oprettes i `RUNNING` sammen med et immutable
start-event.

Tilladte terminale transitioner er:

- `RUNNING` -> `SUCCEEDED`
- `RUNNING` -> `FAILED`
- `RUNNING` -> `CANCELLED`

Terminale job-runs genåbnes ikke.

Et crash kan efter recovery markeres `FAILED` med et versioneret
reason-code, når Aureum kan dokumentere, at det tidligere run ikke
længere er aktivt. Et crash må ikke blot overskrive eller genbruge det
gamle `job_run_id` til en ny kørsel.

Hver state-transition opdaterer job-head med CAS og opretter det
tilsvarende immutable `job_run_events`-record i samme transaktion.

##### Job leases

Lease acquisition, renewal og release er korte transaktionelle
coordination-writes og må ikke holdes åbne under netværks-, provider-
eller AI-kald.

Lease acquisition/reacquisition må lykkes, når:

- `lease_key` ikke findes
- eksisterende head er `RELEASED`, eller
- eksisterende `ACTIVE` lease er dokumenteret udløbet efter canonical
  time og CAS/versionkontrol

Første acquisition opretter en `ACTIVE` head med positivt
`fencing_token`. Reacquisition fra `RELEASED` og takeover fra udløbet
`ACTIVE` skal bruge nyt owner-token og en fencing-generation, der er
højere end den tidligere.

Acquire/reacquire/takeover skal opdatere head og oprette det relevante
immutable `job_lease_events`-record i samme transaction.

Renew kræver `ACTIVE` state, samme owner-token, samme fencing-generation
og forventet state-version. Renew ændrer ikke `fencing_token`, men
opdaterer head-version/expiry og opretter et immutable `RENEW`-event.

En gammel owner må ikke kunne renew eller release et lease, som er
reacquired/overtaget af en nyere fencing-generation.

Release skal CAS-transitionere `ACTIVE` -> `RELEASED`, bevare
`fencing_token`, sætte `released_at` og oprette immutable
`RELEASE`-event i samme transaction. Lease-headen må ikke slettes.

Lease expiry er ikke bevis for, at et tidligere job aldrig udførte en
ekstern side effect. Recovery af alerts, paid AI-attempts og andre
irreversible handlinger følger deres egne reconciliation-regler.

##### Cross-database workflows

Ingen transaktion må forsøge at skabe falsk atomisk commit mellem
`aureum_v3.sqlite3` og `aureum_accounts.sqlite3`.

Hvis en brugerhandling kræver account-data og derefter et V3-write,
læses/valideres account-entitlement først. Det efterfølgende V3-write
gemmer nødvendig stabil external identity/policy-basis og er idempotent.

Hvis account-state ændres mellem de to stores, skal workflowet opdage
og håndtere stale authorization efter sin versionerede policy. Der må
ikke kompenseres ved at omskrive immutable V3-historik.

##### Generelle transaktionsregler

Ingen ekstern HTTP-, provider-, OpenAI-, Telegram- eller anden
potentielt langsom/irreversibel I/O må udføres inde i en åben SQLite
write-transaction.

Write-transaktioner skal være korte og deterministiske. Alt dyrt
forarbejde, der sikkert kan ske før transactionen, udføres før
`BEGIN IMMEDIATE`, men alle correctness-kritiske current-state,
idempotency-, validity- og budgetchecks genvalideres inde i den
beskyttede transaktion.

Når `schema_migration_control` findes, skal enhver normal canonical
V3-write-transaction desuden verificere `write_mode = NORMAL` inde i
den beskyttede transaction før første canonical ændring. Ved
`QUIESCED` eller `MIGRATING` skal normale writers deferere/fail closed
uden canonical write. Kun den eksplicit autoriserede migration-/
maintenance-workflow må skrive under migration-barrieren.

En exception før `COMMIT` skal rulle hele write-settet tilbage.
Application code må ikke efterfølgende antage, at en del af
transactionen blev committed.

Efter et `COMMIT`, hvor næste trin er en ekstern side effect, skal den
committed authorization/outbox/binding kunne opdages og reconciles efter
procescrash.

#### D006.5 SQLite-concurrency, worker claims, fencing og crash recovery

V3.0 er designet til Aureums nuværende enkeltserver og SQLite. WAL giver
concurrent readers, men SQLite har fortsat kun én aktiv writer ad
gangen. D006 må derfor optimere for korte, deterministiske write-
transaktioner frem for at forsøge at omgå SQLite-writer-serialization.

Hvis den dokumenterede production-load senere overstiger denne model,
skal storage-adapteren kunne migreres kontrolleret til en anden
transaktionel database. Correctness-kravene i D004-D006 må ikke
svækkes for at få SQLite til at håndtere en workload, den ikke længere
passer til.

##### Connection ownership og transaction discipline

En SQLite-connection må ikke deles ubeskyttet mellem samtidige threads,
workers eller requests.

V3.0 bruger som udgangspunkt én connection pr. afgrænset unit of work
eller en tilsvarende connection-management-model, som dokumenterer
samme isolation.

Hver ny normal V3-connection skal verificere/anvende D006.1s runtime-
kontrakt, herunder mindst:

- `foreign_keys = ON`
- forventet WAL-mode
- `busy_timeout = 15000` ms som V3.0 production-default
- `synchronous = FULL` for canonical writes
- ingen aktivering af dirty-read-/`read_uncommitted`-adfærd
- understøttet `user_version`

En connection med forkert eller ukendt canonical write-konfiguration
må ikke udføre writes.

Correctness-kritiske read-modify-write flows bruger
`BEGIN IMMEDIATE`, så writer-lock erhverves før state, idempotency og
budgeteksponering læses som grundlag for et efterfølgende write.

Simple immutable inserts kan bruge en kortere normal transaction, når
hele correctness-kontrakten stadig håndhæves af PK/FK/UNIQUE/CHECK og
ingen ubeskyttet cross-row-beslutning er nødvendig.

Der må ikke ligge en SQLite write-transaction åben under:

- HTTP/provider-kald
- OpenAI-kald
- Telegram/delivery-kald
- filesystem-backup eller komprimering
- langvarig parsing/research
- sleep/backoff
- anden ikke-deterministisk eller langsom I/O

##### Busy/locked handling

`SQLITE_BUSY`, `SQLITE_LOCKED` eller tilsvarende lock-contention må
aldrig føre til bypass af transaction, CAS, foreign keys eller
idempotency.

Efter connectionens `busy_timeout` må application-level retry kun ske,
når:

- fejlen er klassificeret som transient lock-contention
- operationen er idempotent eller endnu ikke committed
- hele transactionen startes forfra
- canonical state og alle gates genlæses/genvalideres
- retry-count er bounded af en versioneret runtime-policy

Retry må bruge bounded backoff/jitter uden for en åben transaction.

Et ukendt commit-resultat må ikke blindt retries som et nyt write.
Writeren skal først slå den stabile idempotency-key op og afgøre, om
den oprindelige transaction allerede committed.

Hvis contention fortsætter efter den tilladte retry-policy, skal jobbet
defereres/fejle eksplicit. Aureum må ikke falde tilbage til et
concurrency-usikkert write.

##### Worker claims

Et worker-claim må ikke implementeres som:

1. ubeskyttet `SELECT eligible`
2. transaction afsluttes
3. samme worker forsøger senere at markere recorden claimed

fordi flere workers ellers kan vælge samme arbejde.

Et canonical claim skal ske i én kort beskyttet transaction gennem en
af følgende kontrakter:

- CAS-transition af den relevante mutable head
- oprettelse af en UNIQUE authorization-/binding-record
- acquisition af et fenced `job_leases`-record
- en kombination af ovenstående, når workflowet kræver det

Claim-transaktionen skal verificere eligibility igen umiddelbart før
commit.

Ekstern eller dyr behandling sker først efter claim-commit.

Hvis to workers konkurrerer om samme logical arbejde, må højst én få
det canonical claim. Den tabende worker skal behandle uniqueness/CAS-
conflict som forventet concurrency-resultat og ikke som signal til at
omgå claim-logikken.

##### Lease-kontrakt og fencing tokens

`job_leases` skal ud over `lease_state`, `owner_token`, expiry og
`state_version` indeholde et monotonisk stigende `fencing_token` pr.
`lease_key`.

Første gyldige acquisition får et positivt fencing-token. Hver
reacquisition efter `RELEASED` og hver takeover efter dokumenteret
expiry får et højere token.

Release bevarer det seneste `fencing_token` i headen.
`fencing_token` må aldrig nulstilles eller genbruges for samme
`lease_key`.

Enhver committed acquisition, reacquisition, takeover, renewal eller
release skal i samme transaction som ændringen af `job_leases` oprette
præcis ét immutable `job_lease_events`-record.

`job_lease_events` er den canonical lease-audit og skal mindst binde:

- `lease_key`
- monotonisk `event_sequence`
- event-type: `ACQUIRE`, `RENEW`, `RELEASE` eller `TAKEOVER`
- tidligere og resulterende `state_version`
- relevant owner-identitet/fingerprint og `fencing_token`
- event-tidspunkt
- reason codes

Lease-head og seneste committed lease-event skal være indbyrdes
konsistente. Ved et ukendt commit-resultat bruges både den persistente
head og `job_lease_events` til at afgøre, om operationen allerede
committed; writeren må ikke skabe et nyt event eller en ny
fencing-generation ved blind retry.

Lease-expiry gør kun et nyt acquisition-forsøg eligible. Expiry er ikke
i sig selv bevis for, at den gamle worker er stoppet.

En worker, som udfører et write beskyttet af et lease, skal i samme
write-transaction kontrollere:

- `lease_key`
- eget `owner_token`
- forventet `state_version`
- eget `fencing_token`
- at leasen fortsat er gyldig efter den aktive lease-policy

Hvis en nyere worker har overtaget leasen og fået et højere
`fencing_token`, skal alle efterfølgende writes fra den gamle worker
afvises som fenced-out, også hvis den gamle proces stadig kører.

Canonical records, der skabes af et lease-beskyttet job og hvor
ownership er relevant for audit/recovery, skal gemme
`producer_job_run_id` og det anvendte `fencing_token` eller en
tilsvarende immutable producer-reference.

Et fencing-token giver ikke tilladelse til at omgå recordens normale
idempotency-, freshness-, budget- eller lifecycle-gates.

##### Lease acquisition, renewal og takeover

Et logical acquisition-forsøg genererer sit random/unguessable
candidate `owner_token` før write-transaktionen og genbruger samme token
ved reconciliation af et eventuelt ukendt commit-resultat.

Lease acquisition sker i `BEGIN IMMEDIATE` og skal:

1. læse eksisterende lease-head
2. afgøre om head mangler, er `RELEASED` eller er en dokumenteret
   udløbet `ACTIVE` lease
3. beregne næste monotone `fencing_token`: første acquisition starter
   positivt; ellers større end den senest bevarede generation
4. INSERT eller CAS-opdatere head til `ACTIVE` med candidate owner-token,
   ny expiry, `released_at = NULL` og næste `state_version`
5. oprette immutable `ACQUIRE`- eller `TAKEOVER`-event
6. verificere CAS/row count
7. committe

Hvis commit-resultatet er ukendt, skal writeren først læse
`lease_key` og sammenligne med det præ-genererede owner-token. Matcher
headen den forventede owner/fencing-generation, behandles acquisition
som committed; den må ikke skabe en ny generation ved blind retry.

Renew må kun forlænge expiry for samme aktuelle `ACTIVE` owner og
fencing-generation og skal ske med CAS samt immutable `RENEW`-event i
samme transaction.

Renew må ikke ændre `fencing_token`.

Takeover efter expiry og reacquisition fra `RELEASED` skal altid bruge
nyt owner-token og højere fencing-token.

Release må kun lykkes for aktuel `ACTIVE` owner/fencing-generation.
Den CAS-transitionerer headen til `RELEASED`, bevarer fencing-token og
opretter immutable `RELEASE`-event. Head-recorden må ikke slettes.

Clock-time bruges til eligibility efter den versionerede lease-policy,
men correctness må ikke afhænge alene af perfekt clock-synkronisering.
Fencing-token og CAS er den bindende beskyttelse mod en gammel worker,
der vågner efter expiry.

##### Batch- og scheduler-concurrency

Cron, manuel trigger og web-trigger må ikke antage, at en anden trigger
ikke kan starte samtidigt.

Jobs, som er semantisk eksklusive, skal bruge en dokumenteret
`lease_key`, der er stabil for den beskyttede workload, fx jobtype +
scope.

Et globalt lease må kun bruges, når hele jobbet faktisk kræver global
eksklusivitet. Instrument-/scope-baserede leases foretrækkes, når de
bevarer correctness og tillader sikker parallelisme.

Batch-processing skal isolere fejl pr. instrument/arbejdsenhed, hvor
D004 tillader det. Én fejlende aktie må ikke automatisk holde en lang
global SQLite transaction åben eller rulle allerede committed,
uafhængige instrumenter tilbage.

Et lease må ikke holdes længere end nødvendigt. Lang analyse kan køre
uden åben SQLite transaction, men en lease-beskyttet worker skal renew
før expiry efter den aktive policy og skal kontrollere fencing igen ved
hver efterfølgende canonical write.

##### Outbox worker concurrency

Outbox-workers må kun vælge records, som er eligible efter D006.4.

Claim/authorization af et outbox-item følger D006.4s atomiske
authorization-transaction og UNIQUE
`(alert_outbox_id, attempt_number)`.

Flere outbox-workers må derfor køre samtidigt, men kun én kan
autoriseres til samme logical attempt.

`AUTHORIZED` og `AMBIGUOUS` outbox-records er ikke almindelig
send-queue. De behandles af recovery/reconciliation-pathen.

Et worker-crash må ikke få en anden worker til blot at ændre
`AUTHORIZED` tilbage til `PENDING`.

##### Budget-controller concurrency

Alle paid admission-forsøg, uanset V2/V3/caller, bruger samme canonical
V3 budgetledger og D006.3/D006.4s `BEGIN IMMEDIATE` admission.

Der må ikke eksistere en separat in-memory counter, JSON-counter eller
per-process cache, som kan autorisere paid calls uden den canonical
transaction.

Read-only budgetvisninger må bruge projections/caches, men disse må
aldrig bruges som den bindende hard-cap admission-value.

Concurrent requests med forskellige `reservation_key` kan derfor blive
serialiseret kort under admission; det er tilsigtet correctness-
adfærd.

Hvis én reservation eller reconciliation opretter en global
budget-integritetsblocker, skal efterfølgende admission-transaktioner se
blockeren i canonical state før de kan godkende et nyt paid kald.

##### Lifecycle/gate concurrency

Flere workers må gerne beregne immutable gate-evaluations parallelt,
når input/policies tillader det.

Kun lifecycle-transitionen ændrer den canonical opportunity-head.

To workers, der forsøger transition fra samme
`lifecycle_state_version`, må højst få én committed CAS-transition.

Den tabende worker skal genlæse opportunity-head og må ikke anvende en
gammel gate til at overskrive den nyere state.

En newer state må ikke rulles tilbage gennem last-write-wins.

##### Crash recovery inventory

Recovery må være database-drevet og må ikke afhænge af, hvad en
in-memory worker mente, den var i gang med før et crash.

Ved service-start og gennem et idempotent periodisk recovery-job skal
Aureum kunne identificere mindst:

- `RESERVED` reservationer, som kan være eligible til deterministic
  expiry/release og ikke har attempt-authorization
- `STARTED` reservationer med autoriserede attempts uden sikker
  completion/settlement
- `UNRESOLVED` reservationer, som kræver reconciliation og fortsat
  binder budget
- generation-attempt-authorizations uden completion
- usage-events uden forventet canonical settlement
- `AUTHORIZED` alert-deliveries uden sikker completion
- `AMBIGUOUS` alert-deliveries
- `RUNNING` job-runs, hvis owning lease ikke længere er gyldig
- udløbne job-leases, som kan overtages med højere fencing-token
- ufuldstændigt publicerede/temp backup-artifacts
- rebuildable projections/caches, der er bag canonical state

Recovery-jobbet må ikke selv antage, at manglende completion betyder,
at en ekstern side effect ikke skete.

Recovery skal anvende de samme idempotency-, reconciliation-, CAS-,
budget- og delivery-regler som normale workflows.

##### Recovery af paid AI-attempts

En authorization uden sikker completion skal klassificeres ud fra den
faktiske tilgængelige provider-/usage-evidens.

Hvis omkostningsstatus ikke sikkert kan afgøres, skal reservationen
forblive/blive `UNRESOLVED`.

Recovery må ikke skabe et nyt paid retry, før D005/D006 igen tillader
det. Især må `UNRESOLVED` ikke bruges som retry-kø.

Hvis provider-evidens senere gør settlement mulig, anvendes den normale
idempotente reconciliation-path.

##### Recovery af job-runs

Et `RUNNING` job, hvis lease er tabt/udløbet, må ikke overtages ved at
genbruge det samme `job_run_id` som ny execution.

Når recovery med tilstrækkelig evidens fastslår, at den tidligere
execution ikke længere er aktiv, afsluttes det gamle run via
CAS + immutable `job_run_events`, normalt som `FAILED` med et eksplicit
recovery/crash reason-code.

En ny execution får nyt `job_run_id` og skal acquire sit eget aktuelle
lease/fencing-token.

Immutable outputs, som det gamle run nåede at committe før crash, bliver
stående og genbruges/deduplikeres efter deres normale idempotency keys.

##### Projection/cache recovery

Current-state projections og JSON/dashboard caches må valideres mod
canonical DB state gennem en source version/high-water mark eller
tilsvarende dokumenteret mekanisme.

En stale eller manglende projection må rebuildes uden at ændre de
canonical source-records.

Et projection-rebuild må ikke:

- skabe nye researchreports
- tælle som ny AI-generation
- skabe nye lifecycle-transitions
- sende alerts
- ændre budgetledger
- ændre immutable history

Hvis en JSON-cache-write fejler, forbliver canonical DB-state gyldig.
Cachefejlen må ikke rulles tilbage ved at omskrive databasehistorikken.

##### WAL og checkpointing

WAL-checkpointing er maintenance og må ikke bruges som correctness-
mekanisme for normale writes eller backups.

Online backup følger D006.1 og må ikke kræve rå kopiering af WAL/SHM.

En versioneret maintenance-policy må styre WAL-checkpoints ud fra
størrelse/drift, men checkpoint skal ske gennem SQLite-understøttet
mekanisme og må ikke slette eller manipulere `-wal`/`-shm` manuelt,
mens databasen er aktiv.

Hvis checkpoint møder aktive readers/writers, skal maintenance
deferere eller bruge en sikker SQLite-checkpoint-mode frem for at
tvinge en destruktiv filoperation.

##### Concurrency observability

Aureum skal kunne måle mindst:

- antal `SQLITE_BUSY`/lock-contention events
- bounded retry-count og exhausted retries
- transaction duration for canonical writes
- lease acquisitions, renewals, takeovers og fenced-out writes
- CAS conflicts pr. recordtype
- outstanding `AUTHORIZED`/`AMBIGUOUS` deliveries
- outstanding `STARTED`/`UNRESOLVED` budgetreservations
- recovery-items og deres alder
- WAL-size/checkpoint health, når relevant

Observability-data må ikke indeholde secrets, rå prompts eller andre
følsomme payloads unødigt.

Stigende lock-contention, lange write-transaktioner eller voksende
recovery-backlog er et capacity/correctness-signal og må ikke løses ved
at deaktivere D006s guards.

#### D006.6 Schema-migrations, deployment/rollback og compatibility

V3-schemaet må kun ændres gennem versionerede, auditerbare migrations.
Runtime-services og webrequests må ikke udføre opportunistiske
production-migrations ved almindelig startup eller sidevisning.

En tom V3-database bootstrappes gennem samme migration-chain som en
eksisterende database. Der må ikke findes en separat, uversioneret
"create current schema"-vej, som kan divergere fra migrationshistorikken.

`PRAGMA user_version` er den kompakte runtime-schema-version, men er ikke
tilstrækkeligt auditspor alene.

V3 skal derfor have en canonical `schema_migrations`-historik med mindst:

- monotonisk `schema_version`
- stabil `migration_id`
- immutable migration-checksum/content-hash
- previous og resulting schema-version
- migration-type/classification
- `applied_at`
- application/deployment-identitet, når tilgængelig
- apply-time resultmetadata, som er kendt før migration-transactionens
  commit

Der skal mindst gælde:

`UNIQUE(schema_version)`

og:

`UNIQUE(migration_id)`

En migration, som allerede er registreret med samme ID/version og samme
checksum, må behandles som idempotent allerede-applied.

Samme migration-ID eller schema-version med en anden checksum er en
integritetsfejl og skal fail closed. En allerede anvendt migration må
aldrig redigeres in place; en rettelse er en ny migration/version.

Post-commit verification må ikke skrives tilbage ved mutation af
`schema_migrations`.

V3 skal have separate immutable `schema_migration_verifications` med
mindst:

- stabil `verification_id`
- stabil scoped `verification_key`
- foreign/reference til `migration_id` og resulting schema-version
- den verificerede migration-checksum
- `verified_at`
- verification-/deploy-identitet
- `result`: mindst `PASS` eller `FAIL`
- schema-/integrity-check-resultater og relevant result-hash

`verification_key` skal være UNIQUE for samme tilsigtede verification.
En ny re-verification er en ny immutable record med ny scoped key.

En migration/deployment må ikke erklæres production-verificeret, før
der findes en post-commit `PASS` for præcis den applied
migration/checksum. Hvis databasen er så beskadiget, at en
verification-record ikke kan gemmes sikkert, er dette i sig selv
deployment failure, og V3-writers må ikke genaktiveres.

##### Schema-version og runtime compatibility

Hver V3-applikationsversion skal eksplicit deklarere mindst:

- `required_write_schema_version`
- minimum/maximum schema-version, som den sikkert kan læse, når et
  sådant read-range understøttes
- nødvendige schema-capabilities/feature-flags
- migration-set/checksums, som binæren forventer

Canonical writes er kun tilladt, når databasen har præcis den
`required_write_schema_version`, som den aktive writer understøtter,
medmindre en senere eksplicit D006-beslutning låser en bredere
write-compatible schema-range.

En database med `user_version` nyere end writeren understøtter skal
blokere writes.

En database med ældre schema end den krævede write-version skal også
blokere V3-writes, indtil den eksplicitte migrationsprocedure er
gennemført.

Read-only adgang til en anden understøttet schema-version må kun ske,
hvis den konkrete binær eksplicit erklærer read-compatibility. Der må
ikke gættes på kompatibilitet.

Hvis den globale D005-budgetcontroller er aktiveret, og budgetledgerens
schema ikke er write-kompatibelt eller kan verificeres, skal alle nye
paid AI-calls fail closed. V2 må ikke falde tilbage til et ubudgetteret
AI-call path.

Andre V2-funktioner, som ikke kræver V3-store-write, skal så vidt muligt
kunne fortsætte efter deres eksisterende kontrakter; en inkompatibel
V3-database må ikke i sig selv korrumpere account/auth-store eller
legacy V2-data.

##### Migration coordination, fencing og write barrier

Kun én schema-migration-driver må være aktiv ad gangen.

Før pre-migration backup skal migratoren acquire et fenced
`job_leases`-lease med stabil lease-key:

`schema-migration:aureum_v3`

Efter lease-acquisition skal migratoren i en kort `BEGIN IMMEDIATE`-
transaction:

1. verificere eget owner-/fencing-token
2. verificere `schema_migration_control.write_mode = NORMAL`
3. CAS-transitionere control-head `NORMAL` -> `QUIESCED`
4. binde den planlagte `migration_id`, checksum og fencing-token
5. oprette det immutable `schema_migration_control_events`-record
6. committe

Før en online migration må stole på barrieren, skal deploymentet
dokumentere, at alle aktive V3-writer-generationer understøtter og
kontrollerer `schema_migration_control` efter D006.4.

En ældre writer-generation, som ikke forstår denne barrier, skal
stoppes/deaktiveres før barrier-transaktionen og må ikke genstartes,
mens migrationen er i gang.

Når `QUIESCED` er committed, må ingen normal canonical V3-writer
commit nye writes. Barrier-aware writer-generationer skal respektere
den canonical barrier; ikke-kompatible writers skal allerede være
deaktiveret.

Fordi barrier-transaktionen selv erhverver SQLite-writer-lock og alle
normale writers kontrollerer barrieren, definerer den committed
`QUIESCED` state grænsen efter de tidligere committed writes og før
pre-migration snapshot.

Initial bootstrap af en helt ny database uden tidligere canonical
V3-data udføres med V3-writers deaktiveret. Den første migration
opretter migration-control-strukturen og den initiale `NORMAL` head;
derefter er barrier-kontrakten obligatorisk.

Pre-migration snapshot tages først efter committed `QUIESCED`.

Hvis migrationen senere committer, forbliver control-head
`MIGRATING`, indtil post-commit verification er bestået.

Migration-driveren skal holde migration-leasen gyldig gennem backup,
migration, verification og writer-release og renew den efter D006.5,
når workflowets varighed kræver det.

Før enhver migration-control-write efter den oprindelige acquisition
skal den aktive `job_leases`-head genvalideres mod samme owner-token og
fencing-generation, som er bundet i `schema_migration_control`.

Hvis migratoren mister leasen eller bliver fenced-out, må den ikke
fortsætte DDL, skrive en ny verification, transitionere
`MIGRATING` -> `NORMAL` eller frigive barrieren.

En ny migration-driver, som overtager et udløbet migration-lease, må
ikke starte en ny schema-migration oven på en eksisterende
`QUIESCED`/`MIGRATING` control-head. Den skal først køre en eksplicit
recovery/reconciliation af den allerede bundne migration-ID/checksum.

Kun efter en gyldig immutable verification med `result = PASS` og
fornyet kontrol af samme aktive migration-lease/fencing-generation må en
kort CAS-transaction transitionere `MIGRATING` -> `NORMAL`, oprette det
tilsvarende immutable control-event og derefter frigive migration-
leasen.

Ved migration-/verification-fejl skal barrieren forblive
`QUIESCED`/`MIGRATING`, indtil en dokumenteret recovery/forward-fix/
restore-plan gør writers sikre igen.

Et ukendt commit-resultat må aldrig udløse blind genkørsel af DDL.
Migratoren skal først reconciles mod `user_version`,
`schema_migrations`, migration-checksum og migration-control-head.

##### Migration ordering og atomicity

Migrationer er sekventielle og må ikke springe ukendte mellemversioner
over.

Før migration skal værktøjet verificere mindst:

- current `PRAGMA user_version`
- eksisterende `schema_migrations`
- forventet previous version
- migration-ID/checksum
- `PRAGMA quick_check = ok`
- nul fejl-rækker fra `PRAGMA foreign_key_check`
- at ingen nyere ukendt migration findes

Korte schema-migrations skal som udgangspunkt køre i én
`BEGIN IMMEDIATE`-transaction.

Migrationen skal i samme transaction:

1. verificere expected previous schema-version igen
2. verificere migration-lease owner/fencing-generation
3. verificere control-head `QUIESCED` med samme migration-ID/checksum
4. CAS-transitionere control-head `QUIESCED` -> `MIGRATING` og oprette
   immutable control-event
5. udføre den deterministiske DDL/dataændring
6. validere de invarianter, der kan kontrolleres før commit
7. indsætte præcis én immutable `schema_migrations`-record
8. sætte `PRAGMA user_version` til resulting version
9. committe samlet

Migrationen må ikke destruktivt ændre selve migration-control/
fencing-strukturen i samme release uden en eksplicit specialplan, som
bevarer barrier- og recovery-kontrakten.

En fejl før commit skal efterlade både schema, migrationshistorik og
`user_version` på den tidligere version.

DDL, som ikke kan udføres sikkert efter denne kontrakt, kræver en
eksplicit versioneret special-migrationsplan; application code må ikke
improvisere omkring manglende transactional guarantees.

Migrationer må ikke udføre:

- HTTP/provider-kald
- OpenAI-kald
- Telegram-kald
- afhængighed af live markedsdata
- anden ekstern irreversibel side effect

Migrationens resultat skal afhænge af databaseindholdet og den
versionerede migration, ikke af et eksternt API-svar på migrationstid.

##### Expand, backfill, cutover, contract

Destruktive eller større schemaændringer skal som udgangspunkt følge:

`EXPAND -> BACKFILL -> VERIFY -> CUTOVER -> CONTRACT`

`EXPAND`
- tilføjer den nye backward-compatible struktur
- sletter eller omfortolker ikke gammel canonical data
- nye kolonner skal være nullable/default-kompatible, indtil alle
  eksisterende records kan opfylde de endelige constraints

`BACKFILL`
- migrerer eksisterende data idempotent
- skal kunne genoptages efter crash
- må bruge korte batches frem for én lang writer-transaction

`VERIFY`
- dokumenterer row counts, referential integrity, hashes/invarianter og
  eventuelle domain-specifikke equality checks mellem gammel og ny
  repræsentation

`CUTOVER`
- aktiverer den nye read/write-path gennem versioneret application
  contract/feature flag
- må først ske efter verificeret backfill

`CONTRACT`
- fjerner først gammel struktur, når rollback-/compatibility-vinduet er
  lukket, alle aktive writers bruger den nye kontrakt, og backup/
  recovery-planen er verificeret

En destructive CONTRACT-migration må aldrig skjules inde i en
tilsyneladende additive deployment.

`EXPAND` og `CONTRACT`, når de ændrer fysisk schema, er særskilte
versionerede schema-migrations og ændrer `user_version`.

`BACKFILL`, `VERIFY` og application-`CUTOVER` er ikke i sig selv
kunstige schema-versioner. De refererer til en konkret applied
schema-/migration-version og får egne immutable audit-/coordination-
records. Hvis en af disse faser faktisk ændrer schema, er den ændring
selv en ny schema-migration.

`CUTOVER` må først ske, når alle krævede backfills har dokumenteret
verificeret completion, relevante equality/integrity-checks er bestået,
og den aktive deploy-plan tillader cutover.

`CONTRACT` må først ske efter cutover, lukket rollback-/compatibility-
vindue og ny pre-migration backup.

##### Langvarige backfills

Et backfill, som er for stort til én kort transaction, skal have en
persistent, idempotent progress-kontrakt.

V3 må bruge en `migration_backfills` mutable coordination-head med
mindst:

- stabil `backfill_id`
- migration/schema reference
- state
- state-version
- deterministic scope/cursor
- processed/error counters
- timestamps

Backfill-state begrænses mindst til:

- `PENDING`
- `RUNNING`
- `PAUSED`
- `FAILED`
- `VERIFIED`
- `COMPLETED`

`VERIFIED` kræver, at backfill-data og krævede equality/integrity-checks
er bestået. `COMPLETED` må først bruges efter den deployfase, der gør
backfill-resultatet endeligt efter den aktive plan.

Backfill-headens state ændres med CAS. Auditworthy stateændringer gemmes
som immutable `migration_backfill_events`.

Backfill-state er coordination og må ikke være eneste evidens for, om en
canonical række er migreret. Hver canonical write under backfill skal
fortsat være idempotent gennem normale PK/UNIQUE/content-regler.

Et crash må derfor kunne genstarte batchen uden dobbelte canonical
records eller datatab.

Backfill må ikke holde et globalt job-lease længere end nødvendigt, når
arbejdet sikkert kan scopes. Fencing/idempotency følger D006.5.

##### Pre-migration backup

Enhver production-migration, som ændrer canonical V3-schema eller
canonical data, kræver et verificeret pre-migration snapshot efter
D006.1.

Snapshotmetadata skal mindst binde:

- database-identitet
- pre-migration `user_version`
- seneste applied migration-ID/checksum før ændringen
- target `migration_id` og target migration-checksum
- expected previous og resulting schema-version
- migration/deployment, som snapshot beskytter imod
- migration-control `state_version`
- migration-lease `fencing_token`
- creation timestamp
- SHA-256
- quick-/foreign-key-check-resultat

Snapshot skal skabes efter committed `QUIESCED` og før første
schemaændring.

Efter snapshot og umiddelbart før migration-transactionen skal
migratoren genvalidere samme lease/fencing-generation, control-head,
migration-ID/checksum, previous `user_version` og migrationshistorik.
Enhver mismatch invaliderer snapshotets anvendelse til den planlagte
migration og skal afbryde migrationen.

Migrationen må ikke starte, hvis det krævede snapshot ikke kan skabes
og verificeres.

Et snapshot er recovery-materiale; det må ikke opfattes som automatisk
tilladelse til at miste writes, som senere sker efter migrationen.

##### Deployment sequence

En normal production-deployment med V3-schemaændring skal have en
versioneret deploy-plan og mindst:

1. verificere forventet application/Git-version og schema-version
2. verificere V2/production-health efter den aktive deploy-policy
3. acquire det dedikerede migration-lease/fencing-token
4. CAS-sætte den canonical write-barrier `NORMAL` -> `QUIESCED`
5. stoppe/deaktivere gammel V3 writer-generation og afklare in-flight
   authorization/reconciliation efter D006.4/D006.5
6. skabe og validere pre-migration backup under samme barrier/fencing
7. genvalidere snapshotets migration/checksum/schema/barrier-binding
8. køre de eksplicitte schema-migrations og efterlade control-head i
   `MIGRATING`
9. køre `PRAGMA quick_check` og `PRAGMA foreign_key_check`
10. verificere `user_version`, `schema_migrations` og checksums
11. oprette immutable `schema_migration_verifications` for den konkrete
    migration/checksum
12. deploye kun application code, som er kompatibelt med det nye schema,
    mens normale V3-writers fortsat er blokeret
13. køre smoke-/integrity-tests og holde nye features bag feature flag
14. genvalidere den aktive migration-lease, owner/fencing-generation
    og migration-control-binding
15. først ved gyldig verification/smoke-resultat CAS-transitionere
    `MIGRATING` -> `NORMAL`
16. oprette det immutable control-event og derefter frigive migration-
    leasen med samme fencing-generation
17. verificere budgetledger, recovery-backlog, leases/outbox og andre
    kritiske V3-heads efter deployment

Hvis verification eller smoke-test fejler, må trin 14 ikke ske.

Ordinary webtraffic må ikke selv være migrationsmekanismen.

##### Mixed-version safety

V3.0 production er enkeltserverbaseret og må ikke antage, at to
forskellige application-writer-versioner sikkert kan skrive samtidigt
til samme V3-database.

Under deploy skal der derfor være højst én aktiv canonical writer-
generation for et schema-contract.

Hvis en fremtidig multi-process/multi-host architecture tillader
overlappende app-versioner, kræver det eksplicit dokumenteret
cross-version write compatibility; det er ikke implicit godkendt af
D006.

Feature flags kan styre anvendelse af nyt schema, men må ikke gøre en
ellers inkompatibel writer kompatibel.

##### Rollback classes

Hver migration skal klassificeres før deployment, mindst som én af:

- `ADDITIVE_BACKWARD_COMPATIBLE`
- `FORWARD_FIX_PREFERRED`
- `SNAPSHOT_RESTORE_REQUIRED`

`ADDITIVE_BACKWARD_COMPATIBLE`
- tidligere application-version kan dokumenteret ignorere den additive
  struktur
- application rollback kan derfor være mulig uden database rollback

`FORWARD_FIX_PREFERRED`
- ny canonical data kan allerede være skrevet i det nye schema
- rollback af application/schema kan risikere datatab eller semantic
  corruption
- recovery bør normalt ske gennem ny forward migration/fix

`SNAPSHOT_RESTORE_REQUIRED`
- rollback kræver tilbagevenden til et dokumenteret recovery point
- writers skal quiesces før restore
- ethvert canonical write efter snapshot-tidspunktet kan ellers gå tabt

Rollback-classification skal fremgå af migration-/deploymetadata.

##### Database rollback

SQLite schema rollback må ikke som standard implementeres gennem
uafprøvet reverse-SQL.

Hvis migration-transactionen fejler før commit, er den tidligere
databaseversion fortsat canonical, og ingen særskilt rollback-migration
skal fabrikeres.

Hvis migrationen er committed, men **ingen nye canonical domain-/
business-writes, som skal bevares, er committed efter migrationen**, kan
en verificeret restore af pre-migration snapshot anvendes efter D006.1
sammen med den kompatible tidligere application-version.

De forventede migration-control-, verification- og deployment-
auditrecords, som nødvendigvis kan være oprettet efter schema-commit,
tæller ikke alene som nye business-writes i denne rollback-test.

Før snapshot-restore skal den post-migrerede database, når det er
teknisk muligt, quiesces og bevares separat som hashed forensic
recovery-materiale sammen med migration-ID/checksum, verification- og
deploymetadata. Den forensic kopi må ikke forveksles med et valideret
canonical restore-snapshot.

Når nye canonical domain-/business-writes er sket efter migrationen, må
Aureum ikke blindt restore pre-migration snapshot, fordi dette kan miste
legitim data, alerts, budgetsettlements eller audit.

I det tilfælde kræves enten:

- en eksplicit testet, data-preserving forward fix
- en eksplicit testet reverse migration, som bevarer alle nye canonical
  writes
- eller en bevidst disaster-recovery beslutning, hvor det accepterede
  recovery-point/data-loss dokumenteres

Der må aldrig køres en gammel application-writer mod et schema, den
ikke eksplicit understøtter.

##### Application rollback

Application rollback skal verificere den tidligere binaries
`required_write_schema_version` og read-compatibility **før** den får
lov at skrive.

Hvis schemaet er additive/backward-compatible med den tidligere app,
kan code rollback ske uden schema rollback efter dokumenteret
compatibility-test.

Hvis ikke, skal den gamle app forblive read-only/V3-disabled, indtil
database rollback eller forward fix gør schemaet kompatibelt.

Når D005-budgetcontrolleren er aktiv, betyder V3-disabled/incompatible
budget-store fortsat fail-closed for paid AI — ikke bypass.

##### Migration validation

Efter hver committed migration skal mindst følgende kontrolleres:

- expected `PRAGMA user_version`
- migrationshistorik uden gaps
- migration-ID/checksum match
- migration-control-head og fencing-generation matcher deploymentet
- en separat immutable `schema_migration_verifications`-record kan
  bindes til præcis den applied migration/checksum
- `PRAGMA quick_check = ok`
- nul fejl-rækker fra `PRAGMA foreign_key_check`
- critical UNIQUE/CHECK/FK constraints eksisterer som forventet
- canonical table families/columns/indexes matcher schema-contract
- current heads kan valideres mod immutable eventhistorik, hvor
  kontrakten kræver det
- budgetperioder/reservationer/settlements bevarer D005-invarianter
- lifecycle/outbox-relationer er intakte
- lease fencing-generationer er monotone
- ingen migration har omskrevet immutable audit-records uden eksplicit
  migrationskontrakt

Migrationen/deployment må ikke erklæres succesfuld alene fordi SQL
returnerede uden exception.

##### Migration testkrav

Hver migration skal testes mindst på:

- tom database
- database på præcis previous schema-version
- representative production-lignende fixture/data
- retry efter allerede-applied migration
- checksum mismatch
- newer-than-supported schema
- afbrudt/fejlende migration før commit
- integrity/foreign-key failure
- relevante backfill restart/cursor-cases
- rollback-classens dokumenterede recovery-path

For kritiske migrationer skal en kopi af et production-lignende
database-snapshot kunne migreres og valideres offline før production.

Migrationstests må aldrig bruge den levende production-database som
testfixture.

##### Schema audit og observability

Aureum skal kunne vise mindst:

- current `user_version`
- senest applied migration-ID/checksum
- applicationens required write-version
- read-compatible range, når relevant
- pending migrations
- seneste migration/deploy-resultat
- seneste verificerede pre-migration backup
- aktive/ufærdige backfills
- integrity-check status

En schema-version mismatch er et health/correctness-signal og må ikke
skjules ved automatisk at ændre `PRAGMA user_version` uden den
tilsvarende migration.

#### D006.7 Retention, archivering, deletion, compaction og audit-preservation

D006.7 konkretiserer D004s allerede låste retention-kontrakt. D006 må
ikke udvide en providerlicens, gøre en tidsbegrænset pin permanent eller
bevare rådata længere, end den aktive provider-/source-/retention-
kontrakt tillader.

Retention er record-/payload-specifik. Rå providerpayload, provider-
snapshot, normalized/derived data, inputpakke, researchrapport,
auditrecord, backup og cache må ikke antages at have samme retention-
regel alene fordi de stammer fra samme retrieval.

##### Retention-prioritet og effective deadline

Den aktive retention-vurdering skal mindst tage højde for:

- provider-/licenskrav og source-contract
- eventuelle bindende legal/privacy deletion-krav
- D004s normale raw-payload-retention
- gyldige retention-pins
- recordens rolle i en bevaret inputpakke, gate, rapport eller audit
- den konkrete datatype og om derived retention er tilladt
- backup-/archivekopier, som Aureum selv kontrollerer

Hvis flere bindende regler sætter maksimale retention-frister, vinder
den tidligste obligatoriske sletningsfrist.

En retention-pin må kun forlænge opbevaring inden for det, provider-,
source- og øvrige bindende regler tillader. En pin kan aldrig override
en mandatory deletion deadline.

Hvis et bindende legal krav og en provider-/licensregel tilsyneladende
kræver indbyrdes uforenelig retention, må Aureum ikke stiltiende vælge
den længste opbevaring.

Konflikten registreres som et eksplicit compliance-incident, og ny brug,
kopiering, archivering eller anden udvidelse af payloadens footprint
skal fail closed, indtil konflikten er afklaret.

Et `compliance-hold` er ikke i sig selv en retention-override. Hvis en
tidlig mandatory deletion deadline er entydigt bindende, må en intern
hold-state ikke alene forlænge retention ud over denne deadline.
Retention ud over en ellers bindende frist kræver dokumenteret
legal/provider-basis, som faktisk tillader eller kræver den fortsatte
opbevaring.

For raw providerpayload beregnes den aktuelle retention-basis mindst fra:

- `normal_delete_at`, efter D004s 30–90-dages policy
- eventuel tidligere `mandatory_delete_at`
- eventuel seneste gyldige pin-`review_after`

En gyldig pin kan løfte normal retention, men den effektive keep-period
begrænses altid af en tidligere mandatory deadline.

Retention-klokken nulstilles ikke ved komprimering, arkivering,
database-migration, backup, restore, renaming eller flytning til et nyt
storage-medium.

##### Retention assessments

V3 skal have immutable `retention_assessments` med mindst:

- stabil `retention_assessment_id`
- subject-kind og subject-ID
- `evaluated_at`
- provider-/source-/retention-policyreferencer
- `normal_delete_at`, når relevant
- `mandatory_delete_at`, når relevant
- aktuel pin-basis, når relevant
- beregnet `effective_delete_at`
- recommended action
- reason codes
- assessment-hash

En retention-action må ikke baseres på en gammel assessment, hvis
provider-/source-policy, pin-status, legal deletion-basis eller recordens
dependency-status kan have ændret sig. Correctness-kritiske retention-
checks genvalideres umiddelbart før action authorization.

##### Raw providerpayload: manifest og fysisk storage

`provider_raw_payloads` er det immutable canonical manifest. Manifestet
bevarer mindst Aureums lovligt bevarbare identitet, provider/retrieval-
reference, content-hash, størrelse, relevante observationstider og
retention/provenance-metadata.

Den fysiske raw-payload-body må ikke være den eneste kopi af manifest,
hash eller provenance.

V3.0 skal som udgangspunkt holde den fysisk deletable raw-payload-body
uden for de immutable canonical SQLite-rows i et retention-managed
runtime store. Dette gør provider-mandated deletion mulig uden at
omsætte et immutable auditrecord til et mutable blob-record.

`provider_raw_payload_storage`
- er mutable physical-storage-head for et `provider_raw_payloads`-
  manifest
- gemmer mindst `storage_state`, `state_version`, locator/storage
  backend, compression-format når relevant, payload-size, senest
  verificerede content-hash og eventuel `active_retention_action_id`
- må kun ændres gennem CAS og immutable storage-/retention-events
- `active_retention_action_id` skal være `NULL`, når ingen
  retention-action har et eksklusivt claim på den fysiske storage-head
- må ikke bruges som erstatning for det immutable manifest

Mindst følgende storage states anvendes:

- `PRESENT`
- `COMPRESSED`
- `PURGE_AUTHORIZED`
- `PURGED`

En manglende fysisk fil/object uden en committed purge-workflow er en
integritetsafvigelse og må ikke stiltiende omskrives til `PURGED`.

Provider-/source-data, som er underlagt en fremtidig mandatory deletion,
må ikke embeddes i en ellers permanent immutable auditrow på en måde,
der gør korrekt deletion umulig. Hvis en provider-snapshot-body,
licensed excerpt eller anden payload har en kortere retention end dens
envelope/auditmetadata, skal den deletable body fysisk isoleres bag en
retention-managed payload/storage-kontrakt.

##### Retention-pins

D004s retention-pins konkretiseres som `retention_pins` med mindst:

- `retention_pin_id`
- foreign key/reference til den raw-payload, som pinnes
- `pin_reason`
- `owner_record_type`
- `owner_record_id`
- `retention_policy_version`
- `pin_state`
- `state_version`
- `created_at`
- aktuel `review_after`
- eventuel `released_at`

Tilladte `pin_reason` må kun være de D004-låste kategorier:

- aktiv Deep Research/second opinion
- High-Conviction-gate eller committed overgang
- Thesis-Broken-undersøgelse
- eksplicit audit/anomali/kalibrering

Rutinescans, uændrede scorer og almindelige outcomes må ikke oprette
pins.

`pin_state` er mindst:

- `ACTIVE`
- `RELEASED`
- `EXPIRED`

`review_after` må ved create/renew højst ligge 365 dage fremme.

Create, renewal, release og expiry opretter immutable
`retention_pin_events` med monoton event-sequence. Renewal er en ny
auditerbar state/event-transition og må ikke omskrive pinhistorikken.

Owner-recorden skal eksistere og være en tilladt owner-type på
create/renew-tidspunktet. Fordi owner-referencen kan være polymorf på
tværs af flere canonical table families, skal existence/type valideres
i den beskyttede pin-transaction; en opaque owner-ID uden validering er
ikke nok.

En expired/released pin må ikke automatisk reaktiveres. Fortsat
retention kræver ny eksplicit, versioneret og auditerbar beslutning.

Permanente raw-data-pins er fortsat forbudt i V3.0.

##### Retention action authorization og irreversible deletion

Fysisk purge er en irreversibel side effect og følger samme
pre-authorization/completion-princip som AI- og delivery-attempts.

`retention_action_authorizations`
- har stabil `retention_action_id` og UNIQUE scoped action-key
- refererer til subject/storage-head og den aktuelle
  `retention_assessment_id`
- gemmer action-type, expected storage state/version, relevant
  provider/retention-policy, expected content-hash og `authorized_at`
- oprettes før fysisk compression/purge/archive-operation

Mindst følgende primitive action-types understøttes:

- `COMPRESS`
- `PURGE`
- `ARCHIVE`

`ARCHIVE_PURGE` må ikke være én udelelig action i V3.0. En workflow,
som både skal arkivere og derefter fjerne aktiv storage, består af:

1. en separat `ARCHIVE` authorization/completion med verificeret
   archive-integritet
2. en ny retention-assessment
3. en separat `PURGE` authorization/completion

Dermed kan et crash mellem archive og purge reconciles uden at gætte på,
hvilken af to eksterne side effects der fandt sted.

Authorization og storage-claim skal ske atomisk i én kort
`BEGIN IMMEDIATE`-transaktion. Den skal mindst:

1. genvalidere subject/storage state og `state_version`
2. genvalidere retention-assessment, provider/source-policy,
   mandatory deadline, aktive pins og dependency-impact
3. kræve `active_retention_action_id IS NULL`
4. oprette præcis én immutable `retention_action_authorizations`-record
5. CAS-sætte `active_retention_action_id` til samme
   `retention_action_id`
6. for `PURGE` samtidig transitionere storage-state til
   `PURGE_AUTHORIZED`
7. committe samlet

Den scoped action-key skal være UNIQUE, og storage-headens eksklusive
claim betyder, at to workers ikke kan autorisere konkurrerende
`COMPRESS`, `PURGE` eller `ARCHIVE` mod samme fysiske storage-generation.

Det irreversible filesystem/object-store-kald sker først efter
authorization-commit og uden åben SQLite write-transaction.

`retention_actions`
- er immutable completion-record under samme `retention_action_id`
- gemmer completion-tid, result, reason codes, verificeret efter-state
  og relevante object/hash-metadata
- må højst indsættes én gang pr. authorization

`retention_action_reconciliations`
- håndterer authorization uden sikker completion
- må dokumentere om action faktisk blev gennemført, ikke blev gennemført
  eller fortsat er uklar
- må aldrig omskrive authorization eller tidligere completion

Ved dokumenteret completion/reconciliation skal completionrecord,
eventuel storage-stateændring og frigivelse af
`active_retention_action_id` ske i samme CAS-beskyttede transaction.

Ved fortsat ukendt fysisk outcome må det eksklusive action-claim ikke
frigives blot på timeout. Storage-headen forbliver recovery-blocked,
indtil reconciliation gør næste action sikker.

Efter en vellykket purge skal storage-head CAS-transitionere til
`PURGED` og `active_retention_action_id = NULL`, mens
`provider_raw_payloads`-manifestet, de lovligt bevarbare hashes og
provenance forbliver uændrede.

Efter en vellykket `COMPRESS` transitionerer raw-storage-head til
`COMPRESSED`.

En vellykket `ARCHIVE` opretter/verificerer archive-records efter
D006.7s archive-kontrakt, men ændrer ikke i sig selv den aktive
raw-payload-retentionsfrist eller autoriserer purge.

Recovery efter crash skal kontrollere den faktiske object/file-state,
authorizationen og storage-headens active-action claim. Manglende
completion må ikke automatisk betyde, at payloaden stadig findes eller
allerede er slettet.

##### Komprimering

Fra D004s tilladte tidspunkt kan raw payload komprimeres tabsfrit.

Før den ukomprimerede kopi slettes, skal Aureum mindst:

1. skabe komprimeret candidate
2. fsync/atomisk publicere candidate efter storage-kontrakten
3. dekomprimere/verificere content mod det oprindelige canonical
   content-hash
4. committe retention/compression-completion
5. først derefter fjerne den erstattede fysiske kopi

Komprimering må ikke ændre raw payloads canonical content-hash,
observationstid, provideridentitet eller retention-deadline.

Lossy compression er ikke tilladt for raw evidence, som stadig tæller
som reproducerbart input.

##### Provider-/legal deletion scope

En mandatory deletion er først komplet, når alle Aureum-kontrollerede
kopier, som policyen kræver slettet, er håndteret.

Deletion-scope skal mindst kunne omfatte:

- aktiv raw payload body
- tidligere compressed/archived raw copies
- midlertidige retention-/compression-files
- caches med samme deletable payload
- eksport-/backupkopier, hvis disse indeholder payloaden og er omfattet
  af samme deletion-krav

Logs, prompts, researchoutputs og andre længerelevende records må derfor
ikke ukontrolleret kopiere providerindhold, som source-contracten senere
kræver slettet. Før data må indgå i en længerelevende canonical
artefakt, skal den relevante source-/provider-contract tillade denne
derived/excerpt-retention.

Mandatory deletion må ikke løses ved at ændre et historisk
content-hash, observationstidspunkt eller beslutningsrecord for at få
det til at se ud, som om dataet aldrig fandtes. Det lovligt bevarbare
manifest/tombstone/auditspor skal beskrive, at payloaden blev purged og
hvorfor.

Aureum må ikke hævde cryptographic/secure erase af underliggende disk,
filesystem eller SSD, medmindre storage-platformen faktisk giver en
dokumenteret sådan garanti. D006s `PURGED` betyder, at Aureums
kontrollerede logical/physical copies er fjernet efter den verificerede
storage-kontrakt.

##### Reproducibility efter retention/deletion

En immutable inputpakke eller rapport må ikke omskrives, når en senere
retention-action fjerner et nødvendigt raw input.

V3 skal derfor have immutable `reproducibility_assessments` med mindst:

- stabil `reproducibility_assessment_id`
- relevant input-package/report eller reproduction-scope
- `evaluated_at`
- `reproducibility_level`: `FULL` eller `PARTIAL`
- konkret missing/purged evidence
- retention/provider-policy-basis
- reason codes
- assessment-hash

Et aktuelt `FULL`/`PARTIAL`-view er en rebuildable projection af de
immutable assessments og må ikke være eneste auditspor.

`FULL` må kun vurderes, når D004s fulde input-/kontrakt-/policy- og
lovligt bevarede evidencekrav faktisk kan verificeres.

Hvis mandatory deletion fjerner nødvendigt evidence, oprettes en ny
`PARTIAL` assessment. Den tidligere inputpakke, rapport, gate eller
historiske beslutning omskrives ikke.

En senere rehydrering må ikke automatisk gøre en tidligere
reproduction-assessment `FULL`; der kræves en ny immutable assessment
med verificeret evidence/provenance.

##### Canonical snapshots, research og audit-retention

V3.0 må ikke bruge en generel age-based DELETE mod auditkritiske
canonical table families alene for at spare disk.

Mindst følgende records har ingen automatisk TTL-delete i V3.0, medmindre
en senere versioneret retention-policy og dependency-analyse eksplicit
tillader det:

- instrument-/alias-history
- snapshot envelopes og lovligt bevarbar provenance
- input-package manifests/relationer
- score/gate/lifecycle-history
- researchreport-/generation-/reconciliation-audit
- budget reservation/settlement/reconciliation
- outbox-/delivery-audit
- migration-/lease-/job-audit
- retention-/deletion-audit

Provider-/legal-regler kan stadig kræve deletion/redaction af en
deletable payload-del. I så fald isoleres/fjernes payloaden efter denne
D006.7-kontrakt, mens lovligt bevarbar envelope/hash/audit forbliver.

Canonical record-envelopes med aktive foreign-key-dependents må ikke
fysisk slettes, så der skabes dangling references.

##### Archivering

Archivering er en storage-tier-ændring, ikke en ny retentionperiode.

Et archive-object skal mindst bevare:

- canonical subject/reference
- content-hash
- archive-format/version
- original retention-/provider-policy reference
- original/effective deletion deadline
- created/archived timestamps
- storage locator
- integrity verification

V3 skal repræsentere archivekopier eksplicit:

`retention_archive_objects`
- immutable archive-manifest med stabil `archive_id`
- refererer til source subject og den `ARCHIVE` action, som skabte
  objektet
- gemmer content-hash, format/version, retention-/provider-policy,
  effective deletion deadline og integrity metadata

`retention_archive_storage`
- mutable physical-storage-head pr. `archive_id`
- gemmer mindst `storage_state`, `state_version`, locator/backend og
  eventuel `active_retention_action_id`
- archive-storage-state er mindst `PRESENT` eller `PURGED`
- archivekopien kan derfor purges/reconciles uden at omskrive det
  immutable archive-manifest

En archivekopi må kun skabes, hvis source/provider-policy tillader den.

En `ARCHIVE` action er først succesfuld, når archive-objectet er
atomisk publiceret, dets content-hash/integritet er verificeret, og
archive-manifest/storage-head er committed. Først derefter må en
eventuel separat purge af source autoriseres.

Archivering må ikke bruges til at omgå en deletion deadline eller gøre
en expiring raw payload permanent.

Rehydration fra archive skal genvalidere den aktuelle
provider-/retention-policy før payloaden publiceres som aktiv storage.

V3.0 må ikke flytte relationelle canonical gate/lifecycle/budget/audit-
records ud af `aureum_v3.sqlite3` alene for size optimization, hvis det
bryder foreign-key-integritet eller kræver cross-database auditjoins for
normal correctness. Cold relational archive kræver en senere eksplicit
beslutning med dokumenteret referential-integrity-model.

##### Deduplikering og compaction

To semantisk forskellige immutable records må ikke kollapses, blot fordi
de har samme payload/content-hash.

Særligt må snapshot-ID, observationstid, normalization-version,
provider-/source-scope og provenance ikke mistes gennem content
deduplication.

Raw/provider-licensed payloads må som V3.0-default ikke dele én fysisk
blob på tværs af provider-/retention-scopes, hvis deletion af den ene
logical subject dermed kan slette eller ulovligt bevare den anden.

Cross-subject physical deduplication er kun tilladt, når retention-,
license- og reference-lifetime kan dokumenteres uafhængigt og en purge
af ét subject ikke ændrer andre subjects.

SQLite `VACUUM`, `VACUUM INTO` eller anden database-rewrite er
maintenance og ikke en erstatning for retention-audit.

En compaction, som rewrites canonical V3-databasefilen, skal:

- følge D006.5/D006.6 maintenance/write-barrier/fencing
- have verificeret backup/recovery-plan, når operationens risikoklasse
  kræver det
- køre integrity/FK-check efter operationen
- bevare `user_version`, migration-history og immutable recordidentitet
- aldrig ændre logical retention-deadlines eller genskabe purged data

##### Backup og restore under retention

Den retention-managed raw-payload store skal som V3.0-default ikke
kopieres ukritisk ind i almindelige platform-/full-backups.

Hvis en backup eller eksport indeholder deletable providerpayload, skal
den være retention-aware og mindst kende:

- hvilke payloads/retention-cohorts den indeholder
- relevante provider-/retention-policies
- tidligste mandatory deletion deadline
- backupens egen expiry/deletion-status
- hash/integrity metadata

En backup må ikke bruges til at forlænge raw-data retention ud over det,
som source/provider-policy tillader.

Når en mandatory deletion kræver sletning fra Aureum-kontrollerede
backupkopier, skal backupcatalog/action-audit dokumentere dette.
En backup, som ikke længere er retention-compliant, må ikke præsenteres
som gyldigt restore-point.

Restore fra et ældre snapshot må ikke reintroducere data, som efter
snapshot-tidspunktet er blevet mandatory deleted.

Før en restore kan erstatte den nuværende V3-database, skal Aureum skabe
et retention-aware `retention_restore_guard` uden for den databasefil,
som skal erstattes.

Guard-artifactet skal mindst indeholde:

- stabil guard-ID og creation timestamp
- restore-snapshotets identitet/hash
- kendte mandatory deletion-/purge-tombstones efter snapshotets
  `as_of`
- relevante subject/content-hashes, uden at genindlejre slettet payload
- provider-/retention-policyreferencer
- kilde til guard-data, herunder nuværende canonical retention-audit og
  retention-aware backupcatalog, når relevant
- guard content-hash

Guard-artifactet skal flush/fsynces og bevares uafhængigt af den
database, som overskrives/restores.

Restore sker først til quiesced staging. Guardens deletion/tombstones
skal anvendes mod den restored database, raw-store, archive-store,
caches og relevante backup-/export-referencer, før restored data må
publiceres som canonical.

Hvis den nuværende database er beskadiget eller utilgængelig, skal
restoreprocessen bruge den senest uafhængigt bevarede retention-aware
deletion/backupcatalog-evidens. Hvis det ikke kan dokumenteres
tilstrækkeligt, må raw providerpayload fra et gammelt restore-point ikke
blindt publiceres som aktiv storage; den skal forblive quarantined/
utilgængelig, indtil retention-compliance kan etableres.

`retention_restore_guard` er audit-/sikkerhedsmetadata og må ikke
indeholde selve den mandatory-deleted payload.

Før writers frigives efter restore skal Aureum derfor genvalidere:

- backupens retention-validitet
- aktuelle provider-/source-policies
- kendte mandatory deletion-deadlines/tombstones, som restoreprocessen
  har adgang til
- raw-payload store og archivekopier
- aktuelle reproducibility-assessments

Hvis det valgte restore-point indeholder data, som ikke længere lovligt
må bevares, skal restore ske til quiesced staging, de krævede
retention-actions gennemføres/verificeres, og først derefter må
databasen/storage blive canonical.

##### Personlige/external identity references

V3 må fortsat ikke kopiere account/auth-secrets ind i Opportunity Store.

Hvis V3 gemmer stabile external user/account IDs til audit eller
personlige workflows, skal disse felter have en eksplicit
privacy/retention-policy.

En privacy-required deletion eller pseudonymisering af et personligt
link må ikke omskrive objektive markedsdata, gates eller researchhistorik
som om disse aldrig fandtes. Personhenførbare linkage-felter skal kunne
isoleres/pseudonymiseres gennem en versioneret, auditeret maintenance-
kontrakt, når gældende policy kræver det.

##### Retention workers og concurrency

Retention/compression/purge-jobs bruger stabile `job_run_id`,
idempotency keys og D006.5-leases scoped til den workload, der faktisk
skal være eksklusiv.

Et retention-worker-claim skal ske transactionelt. To workers må ikke
begge autorisere samme purge/compression-action.

Før irreversible action skal workeren genvalidere mindst:

- subject/storage state og version
- content-hash
- seneste retention-assessment
- provider/source-policy
- mandatory deletion deadline
- aktive pins
- dependency/reproducibility-impact
- eget lease/fencing-token, når workloaden er lease-beskyttet

En retention-worker må ikke holde SQLite write-transaction åben under
compression, archive-I/O eller fysisk deletion.

Et crash efter authorization håndteres gennem
`retention_action_reconciliations`; actionen må ikke blindt gentages.

##### Retention observability

Aureum skal kunne vise/måle mindst:

- raw payloads fordelt på `PRESENT`, `COMPRESSED`,
  `PURGE_AUTHORIZED` og `PURGED`
- payloads approaching normal/mandatory deletion deadline
- aktive pins og pins approaching `review_after`
- pins ældre end tilladt review-horizon
- retention-actions awaiting completion/reconciliation
- mandatory deletion failures/backlog
- archive-/backupkopier approaching retention expiry
- antal `FULL` vs. `PARTIAL` reproducibility-assessments
- storage/integrity anomalies, herunder missing payload uden purge-audit

Retention-backlog ved en mandatory deletion deadline er et
compliance/correctness-signal og må ikke skjules ved blot at flytte
payloaden til archive eller forlænge en pin.

#### D006.8 Samlede acceptance criteria

D006 er implementeringsklar, når den fysiske Opportunity Store-
implementering kan dokumentere nedenstående gennem automatiserede
tests, fault-injection, migrations-/restore-tests og auditerbar runtime-
state.

Acceptance-tests må ikke kun kontrollere happy path. Crash-vinduer,
concurrent writers, ukendt commit-resultat, stale workers, manglende
providerresponse, filesystemfejl og genstart skal testes ved de
correctness-kritiske boundaries, som D006.1-D006.7 har låst.

##### Database boundary og runtime

- V3 bruger en separat canonical `aureum_v3.sqlite3`; account/auth-state
  forbliver i `aureum_accounts.sqlite3`
- der findes ingen cross-database foreign keys mellem de to stores
- default-path er `state_path("aureum_v3.sqlite3")`
- `AUREUM_V3_DB_PATH` accepterer kun gyldig absolut override og falder
  ikke stiltiende tilbage ved ugyldig konfiguration
- V3 DB, WAL/SHM og retention-managed runtime-data versionsstyres ikke
  i Git
- nye/eksisterende DB/WAL/SHM-filer sikres med mindst mode `0600`
- normale connections bruger `foreign_keys = ON`, forventet WAL-mode,
  `busy_timeout = 15000` ms og `synchronous = FULL` for canonical writes
- dirty-read-/`read_uncommitted`-adfærd bruges ikke som correctness-
  genvej
- writer med unsupported/newer `user_version` kan ikke skrive
- writer med ældre end required schema kan ikke skrive
- D005 paid AI failer closed, hvis budgetstore/schema ikke kan
  verificeres
- normal sidevisning starter fortsat ingen migrations, provider- eller
  OpenAI-kald

##### Schema, relationer og datatyper

- alle D006.2s canonical table families findes med forventede PK/FK/
  UNIQUE/CHECK/index-kontrakter
- alle foreign keys inden for V3-databasen validerer med nul fejl-rækker
  fra `PRAGMA foreign_key_check`
- immutable references til snapshot, inputpakke, gate, rapport,
  reconciliation, lifecycle, budget og outbox kan følges relationelt
  uden at parse opaque JSON for identity
- felter brugt til idempotency, lifecycle, budget, retention, validity
  eller normal runtime-filtrering ligger ikke kun i opaque JSON
- schema-validerede JSON-payloads kan verificeres mod deres versionerede
  contracts og canonical content-hashes
- semantiske eksternt refererede V3-IDer er stabile opaque IDs; SQLite
  rowid er ikke eneste business-identitet
- canonical timestamps følger den låste UTC-kontrakt
- hard-cap-, reservation- og settlementbeløb gemmes som lossless
  integer `*_dkk_micros`, ikke SQLite `REAL`
- authoritative price-/FX-værdier kan rekonstrueres lossless fra deres
  scaled/rational representation og versionerede contracts

##### Snapshot, provenance, freshness og inputpakker

- D004s provider-snapshot-idempotency håndhæves fysisk
- D004s normalized-snapshot-idempotency håndhæves fysisk
- `PROVIDER` og `NORMALIZED` variantfelter kan ikke danne ugyldige
  hybrid-records
- normalized snapshots kan rekonstruere deres konkrete source snapshots
  gennem `normalized_snapshot_sources`
- field-level provenance kan repræsentere flere faktiske sourcefelter
  for samme derived target field
- provider/raw body kan slettes uden at slette det lovligt bevarbare
  snapshot-/provenance-manifest
- freshness-context og freshness-assessments kan rekonstrueres fra deres
  immutable relationer
- D004s freshness-idempotency håndhæves fysisk
- D004s input-package-idempotency håndhæves fysisk
- hash/UNIQUE-hit med semantic mismatch giver integrity/conflict error
  og aldrig falsk cache-/idempotent success
- inputpakkens snapshot-, freshness- og contract-referencer kan ikke
  ændres efter commit

##### Opportunity, gate og lifecycle

- `COMPOUNDER` og `CATALYST` kan eksistere som separate opportunities
  for samme instrument
- lifecycle-enums accepterer kun de D003-låste states
- gate-resultater accepterer kun `PASS`, `FAIL` og `BLOCKED_DATA`
- gate execution-mode accepterer kun `SHADOW` og `LIVE`
- D004s gate-idempotency håndhæves fysisk
- samme gate-basis kan ikke skabe semantiske gate-dubletter
- gate-evidensreferencer til scores, report-validity, confirmations,
  reconciliation og decision-contracts er auditerbare
- `SHADOW` kan gemme gate-evaluation, men kan ikke oprette LIVE
  lifecycle-transition eller opportunity-alert
- lifecycle-transition, CAS-opdatering af opportunity-head og required
  outbox-record committer samlet eller slet ikke
- fault-injection før/efter hvert trin i transitionstransaktionen kan
  ikke efterlade head, transition eller outbox i modstrid
- concurrent transitioner fra samme `lifecycle_state_version` giver
  højst én committed transition
- stale worker kan ikke overskrive nyere lifecycle-state
- gammel gate kan ikke tvinges igennem efter ændret opportunity-head
- lifecycle-head kan valideres/rebuildes fra immutable
  transitionhistorik
- qualification-label-events ændrer aldrig lifecycle direkte
- samme semantic label-event kan ikke oprettes flere gange ved retry
- confirmation evidence forhindrer falsk dobbeltælling af samme
  underliggende evidens
- `PROVISIONAL_CATALYST_OPPORTUNITY` forbliver label og bliver ikke en
  ekstra lifecycle-status

##### Global AI-request, routing og generationsaudit

- både eksisterende V2- og nye V3-paid AI-requests får canonical
  `ai_requests.request_id`
- V3 research er en extension af samme globale logical request-model
- retry af samme logical request genbruger `request_id`
- legitimt paid retry/fallback får nyt positivt `attempt_number`
- `UNIQUE(request_id, attempt_number)` forhindrer parallelle
  generation-attempt-dubletter
- route-decision er immutable, scoped idempotent og kan ikke referere
  til et andet logical request
- fallback/re-routing kan oprette ny immutable route-decision uden at
  omskrive den tidligere
- `generation_attempt_authorizations` committer før provider-kald
- provider-kald kan ikke starte uden committed authorization og
  budgetbinding
- generation-authorization er immutable efter commit
- generation-completion er separat immutable record og kan højst
  indsættes én gang pr. authorization
- crash efter authorization men før completion frigiver aldrig budget
  alene på timeout
- usage-events deduplikeres deterministisk og kan ikke afregnes to gange
- report-output kan ikke blive canonical gyldig researchrapport uden
  schema-valid output og eksisterende attempt-completion
- invalidt modeloutput kan have audit/completion, men ikke blive gyldig
  gate-evidens
- primary og independent second opinion forbliver fysisk særskilte
- reconciliation omskriver aldrig rapporterne

##### Global AI-budgetledger og hard cap

- alle paid OpenAI-call paths, V2 såvel som V3, bruger samme canonical
  V3 budgetledger
- ingen JSON-/memory-counter kan autorisere paid AI uden canonical
  reservation
- der findes præcis én canonical budgetperiode pr. relevant
  `Europe/Copenhagen`-kalendermåned
- policyændring midt i måneden nulstiller ikke periodens exposure
- `reservation_key` er globalt idempotent for den tilsigtede
  reservation
- reservationens immutable cost-components summerer reproducerbart til
  `reserved_dkk_micros`
- samtidige admissions kan ikke tilsammen overskride den aktive
  100 DKK hard cap
- hard-cap testes med concurrent writers umiddelbart under, på og over
  loftet
- `RESERVED`, `STARTED`, `SETTLED`, `RELEASED`, `EXPIRED` og
  `UNRESOLVED` følger præcis D005s tilladte transitioner
- `RELEASED`/`EXPIRED` kan kun anvendes, når intet paid provider-attempt
  blev autoriseret/startet
- første paid attempt transitionerer reservationen atomisk
  `RESERVED -> STARTED`
- ekstra covered attempts opretter ikke en falsk
  `STARTED -> STARTED` state-transition
- samme generation-attempt kan højst bindes til én reservation
- samme pre-reserverede attempt-slot kan ikke forbruges to gange
- multi-attempt reservation forbliver `STARTED`, indtil alle faktisk
  startede attempts er afregnet eller workflowet bliver `UNRESOLVED`
- uklar cost/providerstatus kan ikke fabrikeres som `SETTLED`
- ét unresolved startet attempt gør hele reservationen `UNRESOLVED`
- `UNRESOLVED` kan ikke autorisere et nyt paid attempt
- faktisk cost over reservation registreres fuldt og skaber canonical
  global admission-blocker
- immutable resolution kan ophæve blocker uden at omskrive oprindelig
  settlement/incident
- settlement og budget-reconciliation er idempotente
- restart kan rekonstruere exposure uden application-memory

##### Alert-outbox og irreversible delivery side effects

- præcis én committed alert-triggerende lifecycle-transition giver højst
  én logical outbox-record pr. kanal
- D004s outbox-idempotency
  `(status_transition_id, alert_type, channel)` håndhæves fysisk
- outbox authorization committer før Telegram/provider-send
- samme logical delivery-attempt kan kun få én authorization og én
  completion
- eksternt send sker uden åben SQLite write-transaction
- crash efter send-authorization men før sikker completion bliver
  `AUTHORIZED`/`AMBIGUOUS` recovery-work, ikke automatisk resend
- recovery-worker sender aldrig direkte fra efterladt `AUTHORIZED`
- dokumenteret levering kan reconciles til `DELIVERED`
- dokumenteret ikke-levering kan reconciles til `RETRYABLE`
- ukendt levering kan ikke skabe et nyt send uden sikker
  provider-idempotency eller auditerbar reconciliation
- `DELIVERED` og `DEAD_LETTER` genåbnes ikke stiltiende
- concurrent outbox-workers kan ikke autorisere samme logical attempt
- duplicate Telegram opportunity-alert efter crash/retry kan ikke
  produceres af den canonical outbox-workflow

##### Transactions, busy handling og unknown commit

- correctness-kritiske read-modify-write flows anvender `BEGIN IMMEDIATE`
- ingen HTTP-, OpenAI-, Telegram-, provider-, backup-, compression- eller
  anden langsom ekstern I/O sker inde i åben SQLite write-transaction
- `SQLITE_BUSY`/`SQLITE_LOCKED` kan ikke bypass-e CAS/idempotency/FK
- retry efter lock-contention genstarter hele transactionen og
  genvaliderer canonical state
- bounded retry exhaustion giver eksplicit defer/failure, ikke
  concurrency-usikkert write
- ukendt commit-resultat håndteres ved lookup af stabil idempotency-key/
  owner-token og ikke ved blind ny INSERT
- fault-injection ved commit-boundaries dokumenterer, at samme logical
  operation aldrig bliver committed to gange

##### Worker claims, jobs, leases og fencing

- ubeskyttet SELECT-then-later-claim bruges ikke til canonical work
- claim sker gennem CAS, UNIQUE authorization/binding eller fenced lease
- to concurrent workers kan højst få ét canonical claim på samme logical arbejde
- `job_run_id` genbruges ikke til ny execution efter crash
- job-head og immutable job-run-events er konsistente
- terminale job-runs genåbnes ikke
- `job_leases` slettes ikke ved release
- lease state er mindst `ACTIVE`/`RELEASED`
- release bevarer seneste `fencing_token`
- reacquisition/takeover får højere fencing-token
- fencing-token nulstilles eller genbruges aldrig for samme lease-key
- `ACQUIRE`, `RENEW`, `RELEASE` og `TAKEOVER` opretter præcis ét
  immutable `job_lease_events`-record sammen med head-write
- ukendt acquisition-commit kan reconciles via præ-genereret owner-token
  uden ny fencing-generation
- gammel worker med lavere fencing-token kan ikke skrive efter takeover
- renewal/release fra gammel owner/fencing-generation afvises
- lease expiry alene behandles ikke som bevis for, at ekstern side effect ikke skete
- lease-beskyttede canonical writes verificerer owner/fencing-generation
  i samme transaction

##### Recovery efter crash/restart

Ved restart og periodisk recovery kan systemet database-drevet finde og
klassificere mindst:

- `RESERVED` reservationer uden started attempt
- `STARTED` reservationer uden sikker completion/settlement
- `UNRESOLVED` budgetreservations
- generation-authorizations uden completion
- usage uden forventet settlement
- `AUTHORIZED` alert-deliveries uden completion
- `AMBIGUOUS` alert-deliveries
- stale `RUNNING` job-runs
- expired leases eligible til takeover
- ufuldstændige retention-actions
- ufuldstændige/temp backup-artifacts
- stale rebuildable projections/caches

Recovery antager aldrig, at manglende completion betyder, at ekstern
side effect ikke fandt sted.

Recovery kan køres idempotent flere gange uden dublerede provider-kald,
Telegram-send, settlements, lifecycle-transitions eller retention-actions.

##### Migrationer og schema compatibility

- en tom database og en eksisterende database bruger samme versionerede migration-chain
- almindelig startup, webrequest eller sidevisning udfører ingen opportunistisk production-migration
- `schema_migrations` og `PRAGMA user_version` ændres atomisk
- allerede-applied migration med samme ID/version/checksum er idempotent
- samme migration-ID/version med anden checksum failer closed
- post-commit verification omskriver ikke `schema_migrations`
- hver production-verificeret migration har en separat immutable
  `schema_migration_verifications` med `PASS`
- barrier-inkompatibel gammel writer-generation stoppes før online migration
- migration-driveren acquires `schema-migration:aureum_v3` med fencing
- `NORMAL -> QUIESCED` blokerer normal canonical write før snapshot
- pre-migration snapshot skabes først efter committed `QUIESCED`
- snapshotmetadata binder præcis source schema, target migration,
  checksum, barrier-version og fencing-generation
- migration-transaktionen binder samme lease/fencing/migration/checksum
  og transitionerer `QUIESCED -> MIGRATING`

- migration-lease holdes/renewes gennem backup, migration, verification
  og writer-release
- fenced-out migrator kan ikke fortsætte DDL, verification eller åbne
  writer-barrieren
- takeover af migration-leasen mod eksisterende `QUIESCED`/`MIGRATING`
  kræver recovery/reconciliation af den allerede bundne migration
- writers kan først genaktiveres efter gyldig verification/smoke og
  fenced CAS `MIGRATING -> NORMAL`
- ukendt DDL-commit-resultat fører til reconciliation af
  `user_version`/ledger/checksum/control-head, ikke blind DDL-retry
- migration-tests dækker tom DB, exact previous version, retry,
  checksum mismatch, newer schema, pre-commit crash, integrity/FK-fejl
  og production-lignende fixture
- kritiske migrations kan valideres offline på production-lignende
  snapshot før production

##### Expand/backfill/cutover/contract

- større/destruktive ændringer følger
  `EXPAND -> BACKFILL -> VERIFY -> CUTOVER -> CONTRACT`
- fysisk schemaændrende EXPAND/CONTRACT er egne `user_version`-
  migrations
- BACKFILL/VERIFY/CUTOVER skaber ikke kunstige schema-versioner, medmindre
  de faktisk ændrer schema
- long-running backfill er persistent og resumable
- backfill-state følger den versionerede state machine og CAS
- backfill-events er immutable
- crash/restart kan genoptage deterministic cursor uden dubletter
- `VERIFIED` kræver beståede equality/integrity-checks
- CUTOVER sker ikke før required backfills/verifications er bestået
- CONTRACT sker ikke fôr rollback-/compatibility-vindue er lukket og ny
  pre-migration backup foreligger

##### Rollback

- rollback-classification er kendt fôr deployment
- `ADDITIVE_BACKWARD_COMPATIBLE` rollback er testet mod tidligere app
- `FORWARD_FIX_PREFERRED` bruges, når nye canonical writes gør snapshot-
  rollback risikabel
- `SNAPSHOT_RESTORE_REQUIRED` har dokumenteret recovery point og
  data-loss-konsekvens
- gammel writer får aldrig skrive mod unsupported schema
- pre-commit migration failure efterlader previous schema canonical
- pre-migration snapshot restore efter committed migration er kun
  automatisk tilladt, når ingen nye canonical domain/business-writes,
  som skal bevares, er committed efter migrationen
- migrationens egne control/verification/deploy-auditrecords forveksles
  ikke med business-writes i denne test
- før snapshot-restore bevares post-migration database, når muligt, som
  hashed forensic recovery-materiale
- hvis nye business-writes findes, kræves tested forward fix, tested
  data-preserving reverse migration eller dokumenteret disaster-
  recovery-beslutning
- application rollback kontrollerer tidligere binaries
  `required_write_schema_version` fôr writes frigives

##### Backup og restore

- live V3-backup bruger SQLite online-backup eller mekanisme med samme
  consistency-garanti og aldrig rå usynkroniseret DB/WAL/SHM-kopiering
- backup-snapshot validerer `PRAGMA quick_check = ok` og nul
  `PRAGMA foreign_key_check`-fejl
- backupmetadata indeholder mindst schema-version, source identity,
  timestamp, size og SHA-256
- snapshot og metadata flush/fsynces og publiceres atomisk, inklusive
  parent-directory durability
- backup virker også, når V3 state/database ligger uden for `PROJECT_DIR`
- platform/full-backup arkiverer det validerede V3-snapshot og ikke live
  DB/WAL/SHM
- backup-temp/artifacts kan identificeres og ryddes/reconciles efter crash
  uden at blive præsenteret som gyldigt restore-point
- restore sker quiesced uden aktive V3 writers
- restore validerer hash, metadata, schema/user_version, quick-check og
  foreign-key-check før publication
- previous canonical database bevares som rollback-/forensic-materiale,
  indtil restore er verificeret
- stale WAL/SHM fra tidligere database kan ikke åbnes sammen med restored
  hoveddatabase
- restored database publiceres atomisk og crash-durable med fsync af
  fil og parent-directory
- efter publication genkøres integrity-, FK- og schema-checks
- writers frigives først, når restored database har bestået den
  krævede verification
- restore må ikke omgå D006.6 migration-control/fencing eller D006.7
  retention-/deletion-guards

##### Retention, provider deletion og pins

- D004s normale raw-payload 30–90-dages retention er fysisk implementerbar
- provider-/legal mandatory deletion kan sætte tidligere deadline
- tidligste obligatoriske sletningsfrist vinder over normal retention og pins
- `compliance-hold` kan ikke alene forlænge en entydig mandatory deletion deadline
- raw-body er fysisk separeret fra immutable manifest, når deletion kan kræves
- manglende raw file uden purge-audit registreres som integritetsfejl
- `retention_assessments` gemmer normal, mandatory og effective deadline,
  action, reasons og policy-/contract-hash
- retention-assessment genvalideres umiddelbart før fysisk retention-action
- `provider_raw_payload_storage` bruger versioneret mutable storage-head og
  `active_retention_action_id`
- storage-state accepterer kun de låste states `PRESENT`, `COMPRESSED`,
  `PURGE_AUTHORIZED` og `PURGED`
- retention-clock nulstilles ikke af compression, archive, migration,
  backup eller restore
- pins kan kun oprettes for D004s tilladte reasons
- routine scans, unchanged scores og almindelige outcomes kan ikke oprette
  raw-data pins
- pin `review_after` kan ved create/renew højst ligge 365 dage fremme
- permanente raw-data pins kan ikke oprettes
- expired/released pin reaktiveres ikke automatisk
- polymorf pin-owner valideres mod eksisterende tilladt owner-record
- en pin kan aldrig override en mandatory deletion deadline
- konflikt mellem retention/pin og provider/legal deadline registreres som
  compliance-incident og fører ikke til tavs retention-forlængelse

##### Retention actions, archive og irreversible purge

- irreversible retention-action har immutable pre-authorization før fysisk I/O
- storage-head claimes atomisk med `active_retention_action_id`
- authorization revaliderer storage-state/version, retention-assessment,
  policy/contracts, deadline, pins, dependencies og fencing-generation
- to concurrent workers kan ikke autorisere konkurrerende retention-actions
  mod samme storage-generation
- fysisk retention-I/O sker uden åben SQLite write-transaction
- completion/reconciliation opdaterer storage-head og frigiver active claim
  atomisk med den relevante immutable audit-record
- timeout frigiver ikke et ambiguous physical-action claim
- crash efter authorization kræver reconciliation og ikke blind repeat
- `ARCHIVE_PURGE` er ikke én udelelig action
- archive og purge kræver separate authorization/completion og en ny
  retention-assessment mellem dem
- archive-object er en storage-tier-ændring og ikke en ny retentionperiode
- archivekopi kan kun skabes, hvis provider/source-policy tillader delj- archive-integritet verificeres før separat source-purge kan autoriseres
- `retention_archive_objects` bevarer immutable archive-manifest
- `retention_archive_storage` kan ændre fysisk storage-state uden at
  omskrive det immutable archive-manifest
- rehydration fra archive genvaliderer aktuelle provider/source/legal policies
  før payload gøres tilgængelig
- successful purge efterlader lovligt bevarbart manifest/hash/provenance
  og fysisk storage-state `PURGED`
- purge må omfatte aktive, compressed, archive-, temp-, cache-, export- og
  Aureum-kontrollerede backupkopier, når mandatory policy kræver det
- compression er lossless, verificeres mod original content-hash og ændrer
  ikke retention-deadline
- compression publiceres først efter fsync/atomic publish og verificeret
  decompression/content-hash; gammel kopi fjernes først derefter
- logical `PURGED` lover ikke cryptographic secure erase uden dokumenteret
  storage-garanti
- missing payload uden purge-audit og hash/state mismatch registreres som
  integrity/compliance incident

##### Reproducibility og audit-preservation

- mandatory raw-data deletion omskriver aldrig tidligere inputpakke,
  rapport, gate eller historisk beslutning
- ny immutable `reproducibility_assessments` oprettes, når retention,
  purge eller providerkrav ændrer verificerbarheden
- assessment-status accepterer kun de låste værdier `FULL` og `PARTIAL`
- `FULL` kan kun anvendes, når alle D004-required inputs, contracts,
  policies, provenance og lovligt retained evidence faktisk kan
  verificeres
- manglende required raw evidence efter lovlig deletion giver ny
  `PARTIAL` assessment frem for omskrivning af tidligere historik
- rehydration ændrer aldrig en tidligere reproducibility-assessment
  in place
- senere genetableret verificerbarhed kræver en ny immutable assessment
- auditkritiske canonical table families har ingen generel age-based
  DELETE/TTL i V3.0
- canonical record-envelopes med aktive foreign-key-dependents slettes
  ikke fysisk
- retention/deletion efterlader ingen dangling canonical references
- lovligt bevarelige manifests, hashes, provenance, policy- og
  contract-referencer bevares, når providerregler tillader det
- content-deduplication kollapser ikke semantisk forskellige snapshots,
  provenance-records, assessments eller decisions
- raw providerpayload må ikke deles som cross-scope blob, hvis scopes
  kan have forskellige retention-lifetimes
- compaction/VACUUM må ikke genskabe purged data eller ændre immutable
  IDs, audit-history eller retention-deadlines
- integrity-checks kan opdage manifest/storage/hash mismatch og
  reproducibility-regression som eksplicit incident

##### Retention-aware backup/restore

- almindelig backup kopierer ikke ukritisk retention-managed raw store
- backup, der indeholder providerpayload, registrerer retention-cohorts,
  relevante policies/contracts, earliest mandatory deadline, backup-expiry
  og content-/manifest-hashes
- backup må ikke anvendes til at forlænge provider-/legal retention
- mandatory deletion omfatter relevante Aureum-kontrollerede backup-,
  archive-, cache-, temp- og exportkopier, når gældende policy kræver det
- backup, som ikke længere er retention-compliant, må ikke præsenteres
  som gyldigt restore-point
- restore fra ældre snapshot må aldrig blindt reintroducere
  mandatory-deleted raw providerpayload
- før destructive restore skabes en uafhængig `retention_restore_guard`
  uden for den databasefil, der skal erstattes
- restore-guard binder guard-ID, tidspunkt, restore-point hash/as-of,
  relevante deletion-/purge-tombstones efter snapshot-as-of,
  subject/content-hashes, policies/contracts/sources og guard-hash
- `retention_restore_guard` må ikke selv indeholde den slettede payload
- guard/evidens publiceres crash-durable og uafhængigt af den database,
  der kan være beskadiget eller blive erstattet
- restore udføres først til quiesced staging
- staging genvalideres mod current retention policies, restore-guard,
  deletion-catalog/tombstones, raw store, archive store og caches
- data, som ifølge post-snapshot deletion-evidens ikke længere må
  eksistere, purges i staging før canonical publication
- hvis current DB er beskadiget, anvendes seneste uafhængigt bevarede
  deletion-/backup-catalog evidence til samme kontrol
- hvis tilstrækkelig deletion-evidens ikke kan dokumenteres, holdes
  gammel raw providerpayload quarantined/unavailable frem for blindt at
  blive gjort canonical/tilgængelig
- restore må ikke nulstille retention-clock, pin-review eller mandatory
  deletion deadline
- før writers frigives, genvalideres retention compliance, backups,
  raw/archive storage, tombstones og reproducibility state
- successful restore kan oprette nye immutable
  `reproducibility_assessments`, men omskriver aldrig historiske
  assessments
- restore-/guard-/purge-reconciliation er idempotent og auditerbar

##### Privacy/external identity

- Opportunity Store kopierer ingen account/auth-secrets, MFA-materiale,
  session-secrets eller andre credentials fra account-databasen
- external user/account linkage har eksplicit privacy/retention-policy
  og kun den minimale linkage, som V3-funktionen kræver
- nødvendig pseudonymisering/deletion kan isolere personlink uden at
  omskrive objektive markeds-, snapshot-, gate-, research- eller
  lifecycle-records
- privacy-maintenance er versioneret, idempotent og auditerbar
- privacy/deletion-work må ikke omgå D006 foreign-key-, retention-,
  provenance- eller reproducibility-kontrakter
- logs, metrics og operational observability må ikke kopiere secrets
  eller retention-managed providerpayload som convenience-data

##### Projections, caches og maintenance

- JSON/dashboard/current-state projections kan rebuildes fra canonical
  V3-database og versionerede source-records
- cache/projection rebuild skaber ingen ny AI-generation, lifecycle-
  transition, alert, provider-fetch eller budgetændring
- cache-write failure ændrer ikke canonical DB-history eller committed
  workflow-state
- stale projection kan opdages via high-water mark, source-version,
  canonical hash eller tilsvarende deterministisk kontrakt
- rebuild af samme canonical state er idempotent
- WAL checkpointing bruges som maintenance og ikke som correctness-
  mekanisme
- WAL/SHM manipuleres ikke manuelt under aktiv database
- VACUUM/compaction følger migration/write-barrier/fencing- og
  integrity-regler og må ikke køre opportunistisk i request-path
- compaction ændrer ikke retention deadlines, migration history,
  immutable IDs, idempotency-keys eller canonical audit history
- maintenance må ikke genskabe purged data fra cache, temp, archive,
  backup eller stale projection
- maintenance failure kan rapporteres/deferres uden at deaktivere
  transaction-, fencing-, retention- eller budgetguards

##### Observability og capacity

Aureum kan uden følsomme payloads vise eller måle mindst:

- schema/`user_version` og migration-/verification-health
- backup-/restore-health og seneste gyldige restore-point
- `SQLITE_BUSY`/`SQLITE_LOCKED`, retry-count og exhausted retries
- canonical transaction duration og write-contention
- CAS-conflicts og integrity conflicts
- lease acquire/renew/release/takeover samt fenced-out workers
- outstanding `STARTED` og `UNRESOLVED` budgetreservations
- outstanding `AUTHORIZED` og `AMBIGUOUS` alert-deliveries
- recovery backlog, alder og unresolved recovery-items
- WAL/checkpoint health uden at bruge checkpoint som correctness-mekanisme
- retention deadlines, aktive pins og kommende mandatory deletions
- mandatory deletion failures/backlog og compliance-incidents
- ambiguous/claimed retention-actions
- `FULL`/`PARTIAL` reproducibility state
- quick-check/FK/integrity/anomaly status

Representative concurrency/load-tests for Universe Scan, snapshot ingestion,
gate writes, budget-admission, retention-workers og dashboard reads skal vise,
at SQLite writer-contention håndteres inden for den versionerede runtime-policy
uden at deaktivere CAS, fencing, idempotency, budget-, retention- eller
audit-guards eller holde lange write-transactions åbne.

Hvis load/correctness-målinger viser, at enkeltserver/SQLite ikke længere er
passende, skal kapacitetsproblemet føre til en kontrolleret storage-migration
frem for at svække transaction-, fencing-, budget-, retention- eller
auditkontrakten.

##### Production-sikkerhed og rollout

D006-implementeringen må først betragtes som production-klar, når:

- V2 account/auth og øvrige legacy data er uændrede af V3 DB-initialization
  og V3-migrations
- V3-store kan feature-flages/disable-es uden tab eller omskrivning af V2-data
- den globale D005-budgetcontroller erklæres først aktiv, når samtlige
  eksisterende paid OpenAI-paths er dækket af canonical admission,
  authorization, usage og settlement/reconciliation
- ordinary sideviews starter ingen provider-, OpenAI-, migration- eller
  retention-side effects
- shadow mode kan bruge V3-store uden automatiske High-Conviction
  lifecycle-alerts eller andre LIVE business side effects
- crash/fault-injection tests er bestået ved alle eksterne
  authorization/completion boundaries
- concurrency-tests er bestået for lifecycle, budget, outbox, jobs/leases,
  migrations og retention-actions
- migration-/backfill-/rollback-/restore-tests er bestået på
  production-lignende data
- backup/restore og retention-aware `retention_restore_guard` er dokumenteret
  testet end-to-end
- `PRAGMA quick_check`, `PRAGMA foreign_key_check` og D006 integrity-tests er
  grønne
- recovery kan køres idempotent efter simuleret procescrash uden dublerede
  paid AI-kald, alerts, settlements, lifecycle-transitions eller
  retention-actions
- required feature flags, schema-compatibility og rollback-plan er
  dokumenteret før V3 canonical writers aktiveres
- paid AI failer closed, hvis global budgetledger, pris/FX, schema eller
  migration-integritet ikke kan verificeres
- ingen D006-test kræver service-restart, deploy eller productionændring under
  blueprint-/reviewfasen

D006 låser persistence-/databasekontrakten. Det implementerer ikke V3 og
autoriserer ikke i sig selv deployment. Før kodeimplementering skal de
efterfølgende relevante V3-beslutninger fortsat respekteres.

### V3-D007

**Status:** LOCKED

D007 låser Opportunities-UX oven på D001-D006. D007 må ikke ændre
Opportunity-profiler, scoredefinitioner, confidence-semantik, lifecycle-
states, High-Conviction-gates, alertregler, persistence-kontrakter eller
AI-budgetregler.

#### D007.1 Informationsarkitektur og user-facing semantics

Opportunities-siden er den dedikerede arbejdsflade for V3-opportunities.
Den er ikke Command Center V3; tværgående executive informationsarkitektur
hører fortsat til D009.

##### Primær informationsenhed

Den primære UI-enhed er en opportunity-case identificeret ved
`opportunity_id`, ikke blot en aktie eller ticker.

Samme instrument kan derfor have to separate cases:

- `COMPOUNDER`
- `CATALYST`

De må ikke fusioneres til én samlet aktievurdering. Hver case beholder
egen lifecycle-status, score, confidence, labels, research, timeline og
alert-historik.

Hvis samme instrument har begge profiler, må UI give tydelig navigation
mellem dem, men profilerne skal fortsat fremstå som selvstændige cases med
forskellig tidshorisont, evidens og lifecycle.

##### At-a-glance hierarchy på opportunity-card

Et opportunity-card skal som minimum vise følgende som tydeligt adskilte
felter:

1. instrumentnavn og ticker
2. opportunity-profile: `COMPOUNDER` eller `CATALYST`
3. current lifecycle-status
4. profilens objektive Opportunity Score
5. AI Confidence
6. Data Confidence
7. relevante qualification labels
8. Portfolio Fit som separat portfolio-vurdering
9. tidspunkt for seneste relevante vurdering/observation
10. tydelig validity/freshness-indikation, når data eller research ikke er
    fuldt aktuelle

Profilens score skal navngives konkret som `Compounder Score` eller
`Catalyst Score`; UI må ikke erstatte dem med ét samlet overall-score.

##### Visuel og semantisk adskillelse

Følgende begreber må aldrig smeltes sammen til ét tal, én badge eller én
uklar samlet vurdering:

- Opportunity Score
- AI Confidence
- Data Confidence
- lifecycle-status
- qualification labels
- Portfolio Fit

Lifecycle-status er den primære state-badge.

Opportunity-profile vises som en separat, stabil profilmarkør og må ikke
ligne en lifecycle-status.

Qualification labels er sekundære. Især
`PROVISIONAL_CATALYST_OPPORTUNITY` skal vises som label og må aldrig
fremstilles som lifecycle-status, High Conviction eller sendt alert.

Portfolio Fit vises separat fra opportunity-kvaliteten. Det må påvirke
prioritering, anbefalet portfoliohandling og visning, men må ikke ændre
Opportunity Score, AI Confidence, Data Confidence eller gate-resultat.

AI Confidence må ikke visuelt eller tekstligt fremstilles som kompensation
for lav Data Confidence. Hvis datagrundlaget er svagt, stale eller blokeret,
skal dette være synligt også ved høj AI Confidence.

`High-Conviction-eligible` fra D002s scoreintervaller er ikke det samme som
canonical lifecycle-status `HIGH_CONVICTION`. UI må kun vise
`HIGH_CONVICTION` som status efter en faktisk committed D003/D004-godkendt
lifecycle-overgang.

`DEEP_RESEARCH` er en arbejdsstatus og må ikke styles som et kvalitetsstempel
eller som en højere conviction end `STRONG_CANDIDATE`.

##### Lifecycle-specifik UX-semantik

UI skal bevare D003-betydningen af hver canonical lifecycle-status:

- `SCREENED`: kvalificeret til videre pipeline, men ikke en aktiv stærk case
- `MONITOR`: interessant, men utilstrækkelig evidens; normalt sekundær visning
- `CANDIDATE`: aktiv opportunity, som fortjener brugerens opmærksomhed
- `STRONG_CANDIDATE`: stærkere aktiv case, men ikke High Conviction
- `DEEP_RESEARCH`: arbejdsstatus, ikke kvalitetsstempel
- `HIGH_CONVICTION`: kun efter faktisk committed og gyldig lifecycle-overgang
- `DATA_HOLD`: neutral datablokering, ikke negativ investeringsdom
- `REJECTED`: casen opfylder ikke aktive krav; historikken bevares
- `EXPIRED`: primært Catalyst-case, hvor event/katalysator ikke længere er relevant
- `THESIS_BROKEN`: materiel thesis-invalidation og skal være visuelt tydelig

`BLOCKED_DATA` er et gate-resultat og må ikke vises som en ekstra
lifecycle-status. Hvis canonical lifecycle er `DATA_HOLD`, vises
`DATA_HOLD`; `BLOCKED_DATA` kan vises som forklaring/evidens.

##### Default relevant universe

Opportunities-arbejdsfladen skal gøre følgende aktive eller
beslutningsrelevante cases direkte tilgængelige:

- `CANDIDATE`
- `STRONG_CANDIDATE`
- `DEEP_RESEARCH`
- `HIGH_CONVICTION`
- `DATA_HOLD`
- `THESIS_BROKEN`

Disse cases behøver ikke ligge i samme tab. D007.2 fastlægger den konkrete
fordeling mellem `ACTIVE` og `NEEDS_ATTENTION`.

`SCREENED` og `MONITOR` findes som udgangspunkt i sekundære views/filtre.

`REJECTED` og `EXPIRED` bevares og kan findes via historik/filtre, men skal
ikke dominere den normale arbejdsflade.

Denne view-definition ændrer ingen canonical state og er ikke en business-
regel for scoring, gates eller lifecycle.

##### Alert-semantik i UI

UI skal skelne mellem mindst:

- lifecycle-status
- logical alert oprettet
- delivery-status
- delivery-/recovery-problem

`HIGH_CONVICTION` betyder derfor ikke automatisk "Telegram leveret".
Levering må kun vises som gennemført, når canonical delivery-state
dokumenterer det.

`THESIS_BROKEN` kan være alert-relevant efter D003, men UI må ikke fabrikere
en sendt alert alene ud fra lifecycle-status.

##### Freshness og ærlighed

Opportunities-UX må aldrig skjule dataproblemer ved blot at vise seneste
kendte score.

Når relevant skal brugeren kunne se:

- vurderingens/scorens observationstidspunkt
- Data Confidence
- stale/aging/error eller anden validity-begrænsning
- `DATA_HOLD`, når canonical lifecycle faktisk er sat dertil
- om research er gyldig, udløbet eller invalideret

Providerfejl i sig selv må ikke fremstilles som negativt investeringssignal.

##### Side-effect-fri rendering

Åbning, refresh, sortering, filtrering eller navigation på Opportunities-
siden må ikke i sig selv:

- starte provider-fetch
- starte OpenAI-generation
- starte Deep Research eller second opinion
- skabe lifecycle-transition
- skabe alert
- ændre Portfolio Fit
- ændre budgetledger

Siden læser canonical state og versionerede projections/caches.
Eventuelle senere brugerhandlinger med side effects skal defineres som
separate, eksplicitte actions med egne guards.

#### D007.2 Tabs, filtre, sortering, søgning og prioritering

Tabs og filtre er read-only views over canonical opportunity-state. De må
ikke oprette eller ændre lifecycle-status, labels, score, confidence,
Portfolio Fit, alerts eller research.

##### Primære tabs

Den normale Opportunities-side bruger fire primære workflow-tabs:

1. `ACTIVE`
   - `CANDIDATE`
   - `STRONG_CANDIDATE`
   - `DEEP_RESEARCH`
   - `HIGH_CONVICTION`
2. `NEEDS_ATTENTION`
   - `DATA_HOLD`
   - `THESIS_BROKEN`
3. `PIPELINE`
   - `SCREENED`
   - `MONITOR`
4. `HISTORY`
   - `REJECTED`
   - `EXPIRED`

Tabs er præsentationsgrupper og bliver ikke nye lifecycle-states.

`ACTIVE` er default-tab og svarer til den normale aktive liste fra D007.1,
mens `DATA_HOLD` og `THESIS_BROKEN` bevidst flyttes til
`NEEDS_ATTENTION`, så datablokering og thesis-invalidation ikke drukner
blandt normale aktive kandidater.

`HIGH_CONVICTION` må gerne have en sekundær quick-filter/chip, men må ikke
defineres som en separat canonical state ud over D003s eksisterende
`HIGH_CONVICTION`.

##### Opportunity-profile filter

Alle primære tabs kan filtreres på:

- `ALL_PROFILES`
- `COMPOUNDER`
- `CATALYST`

Profilfilteret ændrer kun visningen. En case skifter aldrig profile på grund
af et UI-filter.

Hvis samme instrument har både Compounder- og Catalyst-case, skal begge
kunne vises samtidigt under `ALL_PROFILES` som separate opportunity-cases.

##### Canonical filtre

UI skal mindst kunne filtrere på:

- exact lifecycle-status
- opportunity-profile
- Opportunity Score eller scoreinterval
- AI Confidence eller interval
- Data Confidence eller interval
- qualification labels
- Portfolio Fit-kategori, når den relevante portfolio-vurdering findes
- research-validity/status
- freshness/data-validity
- logical alert-status og delivery-status, når alert-records findes

Et filter må ikke skjule, at en case er `DATA_HOLD`, stale eller har
udløbet/invalideret research, hvis brugeren samtidig ser andre felter fra
den case. Kritiske validity-begrænsninger skal fortsat være synlige på
kort/detailvisning.

##### Søgning

Søgning er read-only og må kun arbejde på allerede tilgængelig canonical
state/projection. En søgning må ikke udløse provider-fetch eller AI-kald.

Søgning skal mindst kunne matche:

- instrumentnavn
- ticker
- `instrument_id` ved eksplicit identifikatorsøgning
- `opportunity_id` ved eksplicit identifikatorsøgning

Søgning må ikke deduplikere Compounder- og Catalyst-cases til én række.
Hvis begge profiler matcher, vises de som separate opportunity-cases.

##### Bruger-valgt sortering

UI skal mindst tilbyde:

- `RECOMMENDED` som default
- Opportunity Score faldende
- AI Confidence faldende
- Data Confidence faldende
- seneste relevante vurdering/ændring først
- instrumentnavn alfabetisk

For Catalyst kan næste gyldige relevante event tilbydes som særskilt
sortering, når event-data faktisk findes og er valide.

En bruger-valgt sortering ændrer kun præsentationen og må aldrig ændre
canonical score, lifecycle, gates, Portfolio Fit eller persistence.

##### Default prioritering

`RECOMMENDED` er en deterministisk præsentationsprioritering og er ikke en
ny score.

I `ACTIVE` prioriteres først canonical `HIGH_CONVICTION`. Derefter holdes
`DEEP_RESEARCH` som en tydeligt navngivet workflow-gruppe, så arbejdsstatus
ikke fejlagtigt fremstilles som højere conviction. `STRONG_CANDIDATE` og
`CANDIDATE` prioriteres efter deres eksisterende canonical status og score.

Inden for samme relevante status-/workflow-gruppe bruges som udgangspunkt:

1. højere objektiv Opportunity Score
2. højere AI Confidence
3. højere Data Confidence
4. relevant Portfolio Fit som sekundær prioritering, når den findes
5. seneste materielle vurdering/ændring
6. `opportunity_id` som stabil sidste tie-breaker

Portfolio Fit må aldrig flytte en svagere canonical lifecycle-status til at
se ud som en stærkere status; det er kun en sekundær præsentationsfaktor.

For Catalyst kan en nært forestående, gyldig og relevant katalysator/event
bruges som yderligere præsentationsprioritet inden for samme canonical
status, men må ikke ændre Catalyst Score eller lifecycle-status.

I `NEEDS_ATTENTION` prioriteres `THESIS_BROKEN` før `DATA_HOLD`; inden for
samme status prioriteres portfolio-relevans og derefter nyeste relevante
transition/ændring.

I `PIPELINE` prioriteres `MONITOR` før `SCREENED`; inden for samme status
bruges Opportunity Score og derefter confidence som sekundære nøgler.

I `HISTORY` vises nyeste terminale lifecycle-transition som default først.

Alle default-rækkefølger skal være stabile og reproducerbare, så samme
canonical input giver samme ordering og undgår unødvendig UI-støj.

##### Filterkombinationer og mixed-profile visning

Filtre kombineres deterministisk:

- forskellige filterdimensioner kombineres som AND
- flere valgte værdier inden for samme multi-select-dimension kombineres som OR
- søgning kombineres med de aktive filtre

Et filterresultat er kun en view-projection og må ikke fortolkes som en ny
opportunity-vurdering.

Ved `ALL_PROFILES` skal UI fortsat bevare Compounder og Catalyst som
semantisk separate profiler. En numerisk Opportunity Score må ikke bruges
til at antyde, at Compounder Score og Catalyst Score er én fælles
tværprofil-ranking.

Default- og scoreprioritering anvendes derfor inden for den relevante
opportunity-profile. Hvis begge profiler vises samlet, skal profiltilhørsforhold
forblive tydeligt, og UI må ikke fremstille forskellen mellem de to
scoremodeller som direkte investeringsmæssig overlegenhed.

Ved `RECOMMENDED` sammen med `ALL_PROFILES` grupperes cases først efter
opportunity-profile og prioriteres derefter inden for hver profil. Der skabes
ingen samlet attraktivitetstotalorden mellem Compounder og Catalyst.

Ved eksplicitte ikke-scorebaserede sorteringer, fx instrumentnavn eller
tidspunkt, må profilerne godt interleaves, fordi rækkefølgen da ikke
repræsenterer relativ opportunity-kvalitet.

##### URL- og view-state

Read-only view-state må kunne repræsenteres reproducerbart i URL/query-state
for mindst:

- valgt tab
- opportunity-profile filter
- øvrige aktive filtre
- søgetekst
- sortering

View-state må ikke indeholde secrets, provider-credentials, account secrets
eller andre følsomme værdier.

Ukendte eller ugyldige enum-/filterværdier må ikke skabe canonical writes.
De skal ignoreres eller normaliseres til en sikker default-visning.

Genindlæsning af samme gyldige URL/view-state skal give samme view over samme
canonical snapshot/projection og må ikke udløse side effects.

##### Counts

Tab- og filter-counts skal beregnes fra samme canonical snapshot/projection
som den viste liste.

Counts må ikke blandes fra forskellige refresh-tidspunkter på en måde, der
får UI til at vise et antal, som den aktuelle liste ikke kan forklare.

Hvis et count ikke kan beregnes pålideligt, vises det som utilgængeligt
frem for som `0`.

##### Empty states

UI skal skelne mellem mindst:

- ingen canonical cases i det valgte view
- aktive filtre/søgning skjuler alle cases
- nødvendig projection/data er utilgængelig eller ugyldig

Et tomt søgeresultat må ikke fremstilles som bevis for, at Aureum ikke har
opportunities i universet.

En data-/projection-fejl må ikke fremstilles som `0 opportunities`.

##### Anti-misleading regler

UI må ikke:

- vise manglende score/confidence som `0`, medmindre canonical værdi faktisk er 0
- fremstille stale eller invalideret research som aktuelt
- skjule `DATA_HOLD` bag en tidligere positiv score
- fremstille `DEEP_RESEARCH` som højere conviction end `STRONG_CANDIDATE`
- fremstille `PROVISIONAL_CATALYST_OPPORTUNITY` som lifecycle-status
- fremstille High-Conviction-eligible score som committed `HIGH_CONVICTION`
- fremstille Portfolio Fit som en del af den objektive Opportunity Score
- fremstille Compounder- og Catalyst-score som én fælles scoremodel
- fremstille manglende alert-delivery som leveret

#### D007.3 Opportunity-detailrapport, thesis, research og evidens

Detailvisningen beskriver præcis én canonical opportunity-case identificeret
ved `opportunity_id` og dens `opportunity_profile`.

Den må ikke fusionere en Compounder- og Catalyst-case for samme instrument
til én samlet thesis, score eller conviction.

Detailvisningen er read-only ved almindelig åbning og rendering. Den må ikke
i sig selv starte provider-fetch, OpenAI-kald, Deep Research, second opinion,
lifecycle-transition, alert eller budgetreservation.

##### Top-level summary

Øverst skal brugeren kunne se mindst:

- instrumentnavn og ticker
- `COMPOUNDER` eller `CATALYST`
- current canonical lifecycle-status
- Compounder Score eller Catalyst Score
- AI Confidence
- Data Confidence
- relevante qualification labels
- Portfolio Fit som separat portfolio-vurdering
- seneste relevante evaluation-/observationstidspunkt
- data-/research-validity eller freshness-begrænsning, når relevant

`HIGH_CONVICTION`, `DEEP_RESEARCH`, `DATA_HOLD` og øvrige states skal
bevare præcis samme UX-semantik som i D007.1.

##### Detailrapportens sektioner

Detailrapporten organiseres mindst i følgende semantiske sektioner:

1. `OVERVIEW`
   - case-summary, profile, lifecycle, score og confidence
2. `THESIS`
   - investeringscase, katalysatorer, risici og thesis-invalidation
3. `SCORE_EXPLANATION`
   - objektiv score, delkomponenter og forklarbarhed
4. `RESEARCH`
   - Candidate Review, Deep Research og independent second opinion
5. `CONFIDENCE_AND_DATA`
   - AI Confidence, Data Confidence, freshness og validity
6. `EVIDENCE`
   - beslutningsrelevant evidens, provenance og kildegrundlag
7. `PORTFOLIO_FIT`
   - separat portfolio-relevans uden at ændre opportunity-kvaliteten

Disse sektioner er UI-grupper og bliver ikke nye persistence-objekter eller
business-states.

##### Thesis-visning

`THESIS` skal fremstille investeringscasen som en struktureret,
efterprøvbar case og ikke som et fritstående AI-resume.

Når de relevante data findes, skal thesis-visningen mindst kunne vise:

- tidshorisont for den konkrete opportunity-profile
- business quality og centrale konkurrencemæssige styrker/svagheder
- vækst og indtjeningsudvikling
- marginer og relevante afkastmål som ROIC/ROE
- balance, gæld, likviditet og cash flow
- valuation relativt til kvalitet, vækst og relevante peers/metoder
- konkrete katalysatorer og deres forventede tidshorisont
- centrale risici og red flags
- bull-, base- og bear-case
- eksplicitte thesis-invalidation-kriterier
- næste relevante event, når en valid event findes

Ikke alle felter behøver være relevante for begge opportunity-profiler.
UI skal bevare profilens semantik og må ikke fremstille et manglende eller
ikke-relevant felt som negativ evidens.

For Catalyst skal en konkret katalysator, eventvindue og invalidation være
tydeligt adskilt fra en langsigtet Compounder-thesis.

For Compounder må kortvarigt momentum eller en enkelt event ikke få
thesis-visningen til at ligne en Catalyst-case uden separat Catalyst-evidens.

##### Bull, base og bear

Bull/base/bear skal vises som scenarier og ikke som sandsynlighedsgaranterede
kursmål.

Hvert scenario skal, når data findes, gøre det muligt at forstå:

- hvilke antagelser scenariet bygger på
- hvilke fundamentale eller eventdrevne forhold der skal udvikle sig
- hvilke risici der kan føre casen mod bear-scenariet
- hvilke observationer der vil invalidere den aktuelle thesis

Et scenario må ikke skjule Data Confidence, freshness eller kildebegrænsninger.

##### Thesis-invalidation

Thesis-invalidation skal være synlig som en selvstændig del af detailrapporten
og må ikke gemmes nederst i generisk risikotekst.

UI skal skelne mellem:

- et defineret invalidationskriterium
- observation/evidens der nærmer sig kriteriet
- et faktisk canonical thesis-brud/lifecycle-status `THESIS_BROKEN`

Et opfyldt eller næsten opfyldt kriterium må ikke i UI alene fabrikere en
lifecycle-transition. Canonical `THESIS_BROKEN` vises kun, når den låste
lifecycle-kontrakt faktisk har committed overgangen.

##### Research-visning

`RESEARCH` skal bevare de låste research-roller og rapporttyper separat:

- `CANDIDATE_REVIEW`
- `DEEP_RESEARCH`
- `SECOND_OPINION`

og mindst skelne mellem research-role:

- `PRIMARY`
- `INDEPENDENT_SECOND_OPINION`

En second opinion må ikke præsenteres som en fortsættelse eller redigering
af primary research. Dens uafhængige rolle skal være synlig.

For hver rapport skal brugeren, når felterne findes, kunne se mindst:

- report type og research role
- genereringstidspunkt
- data-/input-observationstidspunkt
- validity/expiry-status
- om rapporten er current, expired eller invalidated
- relevant input-/contract-version eller tilsvarende audit-reference

En udløbet eller invalideret rapport bevares som historik, men må ikke
styles som aktuel beslutningsstøtte.

##### Reconciliation

Når både primary research og independent second opinion findes, skal UI
vise den canonical reconciliation separat fra begge rapporter.

Mindst følgende alignment-statusser skal kunne vises:

- `ALIGNED`
- `MATERIAL_CONTRADICTION`
- `INCONCLUSIVE`

`ALIGNED` betyder ikke i sig selv `HIGH_CONVICTION`; de øvrige låste gates
skal fortsat være opfyldt.

`MATERIAL_CONTRADICTION` og `INCONCLUSIVE` skal være tydelige som blockers
for High Conviction, men må ikke omskrive eller skjule nogen af de to
underliggende researchrapporter.

UI må ikke fremstille reconciliation som en tredje uafhængig opinion.

##### Scoreforklaring

`SCORE_EXPLANATION` skal forklare den canonical objektive score, ikke
beregne en ny UI-score.

UI skal vise `Compounder Score` eller `Catalyst Score` efter den aktive,
versionerede score-policy for den konkrete opportunity-profile.

Når de canonical beregningsdata findes, skal brugeren mindst kunne se:

- total Opportunity Score
- relevante delkomponenter/delscores
- anvendte vægte eller anden canonical bidragslogik
- datadækning for de komponenter, hvor coverage er relevant
- score-/policyversion eller tilsvarende audit-reference
- evaluation-/observationstidspunkt

UI må ikke:

- genberegne score med egne vægte
- udfylde manglende komponenter som `0`, medmindre canonical policy gør det
- lade AI-fortolkning overskrive den objektive score
- fusionere Compounder- og Catalyst-score til én samlet score
- fremstille afrunding eller grafisk præcision som mere præcis end inputdata

##### Gate-forklaring

Når en canonical gate-evaluation findes, må detailvisningen forklare dens
gemte resultat uden at genkøre gaten.

UI skal skelne mellem:

- `PASS`
- `FAIL`
- `BLOCKED_DATA`

og skal, når canonical data findes, kunne vise relevante opfyldte, ikke-
opfyldte eller datablokerede krav samt evaluationstidspunkt og validity.

`FAIL` må ikke fremstilles som synonym for `REJECTED` eller
`THESIS_BROKEN`.

`BLOCKED_DATA` må ikke fremstilles som lifecycle-status.

Et tidligere `PASS` må ikke fremstilles som aktuelt, hvis gaten er udløbet,
invalideret eller ikke længere matcher current opportunity/input/policies.

##### AI Confidence

AI Confidence skal vises som en separat vurdering af, hvor robust og
sammenhængende investeringscasen er.

AI Confidence må ikke:

- ændre den objektive Opportunity Score
- skjule modsigelser mellem primary research og second opinion
- kompensere visuelt eller semantisk for utilstrækkelig Data Confidence
- fremstilles som sandsynligheden for et bestemt fremtidigt afkast

Når relevant skal UI vise, hvilken current research/reconciliation der
understøtter den viste AI Confidence.

##### Data Confidence

Data Confidence skal vises som en separat vurdering af datagrundlagets
komplethed, aktualitet og konsistens.

UI skal gøre det tydeligt, når Data Confidence begrænses af eksempelvis:

- manglende kritiske data
- stale eller aging data
- modstridende kilder
- provider-/valideringsfejl
- utilstrækkelig relevant datadækning

En providerfejl må ikke i sig selv fremstilles som et negativt
investeringssignal.

Ved `DATA_HOLD` skal dataårsagen kunne forklares uden at skjule den seneste
historiske score, men den historiske score skal samtidig markeres som ikke
tilstrækkelig til en aktuel beslutning.

##### Evidens og provenance

`EVIDENCE` skal gøre det muligt at skelne mellem:

- canonical input/data
- afledte objektive metrics/scores
- AI-researchfortolkning
- gate-/reconciliation-resultater

AI-genereret tekst må ikke fremstilles som den oprindelige datakilde.

For beslutningsrelevant evidens skal UI, når canonical provenance findes,
kunne vise mindst:

- kilde/provider-identitet
- relevant data-/observationstidspunkt
- freshness/validity-status
- reference til den immutable input-, evidence- eller source-record

Hvis provenance mangler eller ikke kan valideres, skal UI vise dette
ærligt frem for at fabrikere en kilde eller skjule begrænsningen.

Detailvisningen må ikke omskrive immutable research-, evidence-, gate- eller
reconciliation-records for at gøre forklaringen mere læsevenlig.

##### Falsk præcision og usikkerhed

UI må ikke bruge grafisk eller sproglig præcision til at skjule usikkerhed.

Det betyder mindst:

- ingen opdigtede decimaler ud over canonical præcision
- ingen implicit afkastsandsynlighed ud fra AI Confidence
- ingen falsk sikkerhed ved manglende eller stale data
- ingen skjult konflikt mellem rapporter eller evidenskilder
- ingen omdøbning af `BLOCKED_DATA` til en negativ investeringsdom

#### D007.4 Timeline, lifecycle-historik, ændringsforklaring og outcomes

Timeline er en read-only historisk visning af canonical records for én
`opportunity_id`. Den er ikke en alternativ state machine og må ikke
rekonstruere eller omskrive canonical lifecycle.

##### Timeline-semantik

Timeline skal gøre det muligt at forstå, hvad der faktisk skete med casen
over tid, uden at blande forskellige recordtyper sammen til én syntetisk
historie.

Når de relevante canonical records findes, kan timeline mindst vise:

- lifecycle-transitions
- score-/evaluation-observationer
- ændringer i AI Confidence og Data Confidence
- qualification-label events
- Candidate Review, Deep Research og second-opinion events
- research expiry/invalidation
- reconciliation-resultater
- gate-evaluations
- relevante data-/freshness-blockers
- logical alert creation og efterfølgende delivery/recovery-status
- relevante outcome-observationer

De enkelte eventtyper skal fortsat kunne identificeres som forskellige
canonical typer. UI må ikke fremstille fx en gate-evaluation som en
lifecycle-transition eller en alert-delivery som en ny opportunity-status.

##### Tidsorden

Timeline sorteres efter de canonical event-/evaluation-/observationstider,
som hører til de underliggende records.

Hvis flere records har samme relevante tidspunkt, skal visningen bruge en
stabil, reproducerbar tie-breaker fra canonical identitet/orden. UI må ikke
opfinde en falsk sekvens alene for at gøre historien mere læsevenlig.

Registrerings- eller ingestionstid må ikke stiltiende fremstilles som
økonomisk observationstid, når de to tider er forskellige.

##### Lifecycle-historik

Lifecycle-historikken skal vise de faktisk committed transitions og mindst
kunne forklare:

- `from_status`
- `to_status`
- transitionens canonical tidspunkt
- relevant reason/trigger-reference, når den findes
- den evidens/gate-reference, som canonical transitionen faktisk knytter til

UI må aldrig udlede en manglende transition ud fra score alene.

Eksempelvis må en score i et High-Conviction-eligible interval ikke
fabrikeres som en historisk transition til `HIGH_CONVICTION`.

`DEEP_RESEARCH` bevares som arbejdsstatus også i historikken og må ikke
efterfølgende styles som et historisk kvalitetsstempel.

`DATA_HOLD` skal i historikken fortsat fremstå som datablokering og ikke som
en bearish investeringsdom.

`THESIS_BROKEN`, `REJECTED` og `EXPIRED` skal vises som de canonical states,
de er, uden at UI omskriver dem til en fælles negativ slutstatus.

##### Current state versus history

Detailvisningen skal visuelt skelne mellem current canonical state og
historiske states/evalueringer.

En gammel `HIGH_CONVICTION`, `PASS`, høj score eller høj confidence må ikke
fremstå som current, hvis en nyere canonical transition, invalidation,
freshness-vurdering eller anden gældende record har afløst den.

Historiske records må gerne forklares, men deres originale betydning,
timestamp, identitet og immutable indhold må ikke ændres af UI-laget.

##### Hvad ændrede sig?

Detailvisningen må tilbyde en forklaring af ændringer mellem to relevante
canonical observationer eller evaluations, men forklaringen skal være
forankret i de records, der faktisk findes.

En ændringsforklaring skal skelne mellem mindst:

- observeret ændring i canonical input/data
- ændring i objektiv score eller delscore
- ændring i AI Confidence
- ændring i Data Confidence
- ændring i research/reconciliation
- lifecycle-transition
- qualification-label event
- alert-/delivery-event

UI må ikke fremstille tidsmæssig samtidighed som dokumenteret kausalitet.

Eksempelvis må en kursbevægelse og en scoreændring, der sker tæt på
hinanden, ikke automatisk beskrives som årsag og virkning uden canonical
evidens for den sammenhæng.

##### Før/efter-sammenligning

Når to kompatible canonical records sammenlignes, skal UI tydeligt vise:

- hvilket tidspunkt/version der er `before`
- hvilket tidspunkt/version der er `after`
- hvilke felter der faktisk ændrede sig
- hvilke felter der er uændrede
- hvilke felter der ikke kan sammenlignes pålideligt

Sammenligning må kun ske mellem semantisk kompatible felter. UI må fx ikke
sammenligne Compounder Score direkte med Catalyst Score som om de var samme
måleenhed.

Hvis score-policy, input-contract eller anden relevant beslutningskontrakt
har ændret sig mellem to records, skal dette være synligt. En numerisk
forskel må ikke fremstilles som ren økonomisk ændring, hvis definitionen
eller beregningsgrundlaget samtidig er ændret.

##### Material change

`material change` er en præsentationsklassifikation over canonical events
og må ikke blive en ny lifecycle-status eller en ny objektiv score.

En event må kun fremhæves som material, når en versioneret canonical regel,
eventtype eller allerede gemt vurdering understøtter det.

UI-laget må ikke selv opfinde nye tærskler for materialitet.

Material changes kan blandt andet omfatte:

- væsentlig ændring i score eller relevant delscore
- væsentlig ændring i AI Confidence eller Data Confidence
- nyt eller ændret thesis-invalidation-signal
- ny eller ændret væsentlig katalysator
- research invalidation/expiry
- reconciliation der skifter alignment-status
- lifecycle-transition
- væsentlig freshness-/datablokering

Listen er kun en UX-kategorisering; de underliggende canonical records
forbliver autoritative.

##### Forklaring versus evidens

En menneskeligt læsbar forklaring må opsummere canonical før/efter-data,
men må ikke erstatte evidensen.

Brugeren skal kunne skelne mellem:

- fakta fra canonical records
- beregnede forskelle
- AI-/systemforklaring
- dokumenteret årsag/trigger, når en sådan faktisk findes

Hvis årsagen ikke kan dokumenteres, skal UI bruge formuleringer som
"samtidig med" eller "ændrede sig fra/til" frem for at hævde kausalitet.

##### Outcome-visning

Outcome-visningen er read-only og viser canonical outcome-observationer for
den konkrete opportunity-case. UI må ikke hente live markedsdata eller
genberegne historiske outcomes ved almindelig rendering.

Outcome-horisonterne følger D001 og holdes profilspecifikke:

- Catalyst: 1, 3, 6, 12 og 18 måneder
- Compounder: 6, 12, 24, 36 og 60 måneder

UI må ikke fusionere de to profiler til én fælles performance-horisont eller
bruge en Catalyst-horisont som direkte kvalitetsdom over en Compounder-case.

##### Outcome-status

For hver relevant horisont skal UI skelne mellem mindst:

- endnu ikke moden/pending
- canonical outcome tilgængeligt
- outcome-data utilgængelige eller ugyldige

En fremtidig eller endnu ikke moden horisont må aldrig vises som `0%`.

Manglende eller ugyldige outcome-data må heller ikke fremstilles som nulafkast.

Når canonical outcome-recorden indeholder dem, skal brugeren kunne se:

- opportunity-profile
- reference-/starttidspunkt
- outcome-horisont
- observationstidspunkt/as-of
- den canonical målte performance/outcome-værdi
- relevant benchmark eller relativ performance, hvis canonical record faktisk
  indeholder og validerer dette
- data-/validity-status

UI må ikke konstruere et benchmark efterfølgende alene for at få casen til at
se bedre eller dårligere ud.

##### Outcome versus beslutningskvalitet

Et realiseret kursafkast er ikke i sig selv bevis for, at den oprindelige
thesis, score eller AI-vurdering var korrekt eller forkert.

Outcome-visningen skal derfor holde mindst følgende adskilt:

- hvad systemet vurderede på beslutningstidspunktet
- hvilke data/evidenser der var tilgængelige på det tidspunkt
- hvad der efterfølgende faktisk skete
- hvilke senere events eller ændringer der først blev kendt bagefter

UI må ikke retroaktivt omskrive en historisk score, thesis, confidence eller
lifecycle-status ud fra et senere outcome.

##### Hindsight- og look-ahead-beskyttelse

Historiske vurderinger skal præsenteres med deres daværende input-, policy-,
research- og freshness-kontekst.

Senere kendte data må ikke fremstilles som om de var kendt ved den oprindelige
beslutning.

En ændringsforklaring eller outcome-kommentar må ikke bruge efterfølgende
information til at fabrikere en årsag, som ikke var dokumenteret i de
canonical records.

##### Survivor- og selection-bias

Outcome-visningen må ikke kun fremhæve succesfulde eller stadig aktive cases.

`REJECTED`, `EXPIRED`, `THESIS_BROKEN` og øvrige historiske cases skal kunne
indgå i outcome-evaluering, når canonical outcome-data findes og retention-
kontrakten tillader det.

Filtrering i UI må gerne ændre den viste population, men det skal være tydeligt,
hvilket udvalg brugeren ser. Et filtreret subset må ikke fremstilles som hele
systemets historiske performance.

##### Performance-præsentation

UI må ikke:

- bruge én enkelt kort horisont som samlet bevis på modelkvalitet
- sammenligne Compounder og Catalyst uden tydeligt at bevare profil og horisont
- skjule manglende eller umodne outcomes
- erstatte canonical outcomes med live-genberegnede tal
- omskrive historiske vurderinger efter resultatet er kendt
- fremstille korrelation mellem efterfølgende events og afkast som dokumenteret
  kausalitet uden canonical evidens

Outcome-data er evaluerings- og kalibreringsgrundlag. De er ikke nye
lifecycle-states, gates eller Opportunity Scores.

#### D007.5 Portfolio Fit, portfolio-relevans og personaliseret visning

Portfolio Fit er et separat personaliseringslag oven på den canonical
opportunity-case. Det er ikke en del af den objektive Compounder- eller
Catalyst-vurdering.

##### Objektiv case versus portfolio-kontekst

UI skal altid holde følgende adskilt:

- objektiv Opportunity Score
- AI Confidence
- Data Confidence
- lifecycle-status
- gate-resultat
- Portfolio Fit
- faktisk portfolio-medlemskab/position, når den findes

Portfolio Fit må efter D002 påvirke anbefalet portfoliohandling,
prioritering og visning, men må ikke:

- ændre Compounder Score eller Catalyst Score
- ændre AI Confidence
- ændre Data Confidence
- opfylde eller underkende en High-Conviction-gate
- ændre lifecycle-status
- omskrive research eller reconciliation
- skabe qualification labels

En stærk Portfolio Fit må derfor ikke få en svagere opportunity-case til at
fremstå som `HIGH_CONVICTION`, og en svag Portfolio Fit må ikke nedskrive
den objektive opportunity-kvalitet.

##### Portfolio-medlemskab versus Portfolio Fit

UI skal skelne mellem:

- om instrumentet faktisk findes i den aktuelle portfolio
- den aktuelle positions relevante portfolio-kontekst
- Portfolio Fit-vurderingen

`IN_PORTFOLIO` eller tilsvarende visningsindikator er portfolio-kontekst og
må ikke fremstilles som en opportunity lifecycle-status.

En aktie kan have høj objektiv opportunity-kvalitet uden at være i
portfolioen, og en eksisterende portfolio-position kan have lav Portfolio
Fit uden at dette i sig selv ændrer opportunity-status.

##### Read-only portfolio-visning

Almindelig åbning, refresh, sortering, filtrering eller navigation må ikke
i sig selv:

- købe, sælge eller ændre en position
- ændre portfolio-vægte
- ændre Portfolio Fit
- starte provider-fetch eller OpenAI-kald
- skabe lifecycle-transition eller alert
- ændre budgetledger

Opportunities-UX læser kun den autoriserede canonical portfolio-kontekst
eller en versioneret read-only projection.

##### Manglende portfolio-kontekst

Hvis portfolio-data eller Portfolio Fit ikke findes, er utilgængelig eller
ikke kan valideres, skal UI vise dette som utilgængeligt/ukendt.

Manglende Portfolio Fit må ikke fremstilles som neutral, dårlig eller `0`.

Manglende portfolio-kontekst må heller ikke ændre den objektive
Opportunity Score, AI Confidence, Data Confidence eller lifecycle-status.

##### Portfolio Fit-faktorer

Når den canonical portfolio-kontekst indeholder dem, skal UI kunne forklare
Portfolio Fit med de underliggende faktorer frem for kun at vise et samlet
personaliseret label eller tal.

Relevante faktorer omfatter mindst de D002-låste portfolio-dimensioner:

- sektor-/enkeltaktiekoncentration
- overlap med eksisterende eksponeringer
- valuta-/markedsrisiko

Derudover må UI vise factual portfolio-kontekst, når den findes, fx om
instrumentet allerede er i portfolioen og relevant eksisterende eksponering.

UI må ikke selv konstruere nye Portfolio Fit-faktorer, vægte eller tærskler
og derefter fremstille dem som canonical beslutningslogik.

##### Ingen skjult samlet opportunity-score

Portfolio Fit må gerne have sin egen canonical kategori eller værdi, hvis
den eksisterer i den låste portfolio-vurdering, men UI må ikke kombinere
den med Opportunity Score, AI Confidence eller Data Confidence til et nyt
samlet attractiveness-, conviction- eller recommendation-score.

Der må heller ikke skabes en skjult UI-formel, hvor fx høj Portfolio Fit
automatisk løfter en `CANDIDATE` over en objektivt stærkere case.

Når Portfolio Fit bruges som sekundær sorterings- eller prioriteringsfaktor
efter D007.2, skal den fortsat vises som portfolio-kontekst og ikke som
objektiv opportunity-kvalitet.

##### Anbefalet portfoliohandling

Hvis canonical portfolio-logik producerer en anbefalet portfoliohandling,
må Opportunities-UX vise den som et separat personaliseret output.

Anbefalet portfoliohandling må ikke:

- fremstilles som lifecycle-status
- ændre Opportunity Score eller confidence
- fremstilles som selve High-Conviction-gaten
- fabrikeres af UI ud fra Portfolio Fit alene
- fremstilles som gennemført handel eller ordre

UI skal skelne mellem mindst:

- objektiv opportunity-vurdering
- personaliseret anbefalet portfoliohandling
- faktisk portfolio-/positionsstate
- eventuel senere udført brugerhandling, hvis en sådan canonical record findes

En anbefaling om portfoliohandling er derfor ikke det samme som, at en
position er blevet købt, solgt eller ændret.

##### Konflikt mellem stærk case og svag Portfolio Fit

Hvis en opportunity er objektivt stærk, men Portfolio Fit er svag, skal UI
vise begge vurderinger samtidigt og forklare portfolio-begrænsningen uden
at nedskrive den objektive case.

Tilsvarende må en høj Portfolio Fit ikke skjule en lavere Opportunity Score,
lav Data Confidence, `DATA_HOLD`, `THESIS_BROKEN` eller andre canonical
begrænsninger.

Personaliseret prioritering må aldrig skjule canonical risici eller
validity-problemer.

##### Portfolio-freshness og tidssemantik

Portfolio-kontekst og opportunity-kontekst kan have forskellige canonical
observationstidspunkter. UI må ikke antyde, at de er synkrone, hvis de ikke er det.

Når relevant skal brugeren kunne se:

- portfolio-snapshot/as-of
- Portfolio Fit evaluation/as-of
- opportunity evaluation/as-of
- freshness/validity for den anvendte portfolio-kontekst

En gammel portfolio-position, vægt eller Portfolio Fit må ikke fremstilles som
current, hvis den relevante canonical portfolio-kontekst er stale, invalid eller
afløst.

Stale portfolio-data må ikke skjules bag en aktuel opportunity-score.

##### Identitets- og cross-store-grænse

Når portfolio- og opportunity-data kommer fra forskellige stores eller projections,
skal sammenkoblingen ske via de låste stabile identiteter og canonical mappings.

UI må ikke gætte et portfolio-match alene ud fra displaynavn eller ticker, hvis
instrumentidentiteten er tvetydig.

Ved identitetskonflikt eller manglende sikker mapping vises portfolio-konteksten
som utilgængelig frem for at knytte den til den forkerte opportunity-case.

D007 ændrer ikke D006s fysiske persistence-, database- eller transaktionsgrænser.
En read-only detailvisning må ikke skabe en skjult cross-store write eller
distribueret side effect.

##### Autorisation og privacy

Personaliseret portfolio-kontekst må kun vises, når den aktuelle request er
autoriseret til de relevante portfolio-data.

Autorisation skal håndhæves server-side; det er ikke tilstrækkeligt blot at skjule
et UI-element.

Opportunities-UX må ikke eksponere eller kopiere secrets som:

- passwords
- session-/auth-tokens
- provider-credentials
- API-nøgler
- andre account secrets

sådanne secrets må heller ikke placeres i URL/query-state, client-visible debugdata
eller opportunity-/Portfolio Fit-visningsfelter.

Hvis portfolio-kontekst ikke er autoriseret, skal UI udelade den personaliserede
information uden at ændre den objektive opportunity-case.

##### Anti-misleading portfolio-regler

UI må ikke:

- fremstille utilgængelig portfolio-kontekst som `ikke i portfolio`
- fremstille manglende Portfolio Fit som `0` eller neutral fit
- fremstille stale Portfolio Fit som current
- skjule tidspunktet for en væsentligt ældre portfolio-vurdering
- gætte instrumentmatch ved tvetydig identitet
- kombinere Portfolio Fit med Opportunity Score til en skjult samlet score
- fremstille anbefalet portfoliohandling som udført handel
- fremstille portfolio-medlemskab som lifecycle-status
- skjule `DATA_HOLD`, `THESIS_BROKEN` eller andre canonical begrænsninger
  fordi den personaliserede portfolio-kontekst ser positiv ud

##### Side-effect-fri personalisering

Al almindelig rendering af personaliseret portfolio-kontekst skal være read-only.

En senere eksplicit brugerhandling, som faktisk ændrer portfolio eller anden
canonical state, skal være en separat navngivet action med egne authorization-,
validation-, concurrency- og persistence-guards. Den må ikke skjules i page load,
filter, sortering eller navigation.

#### D007.6 Alert-historik, delivery/recovery og alert-relaterede handlinger

Alert-UX er en read-only visning af de canonical alert-, outbox-, delivery-
og recovery-records, medmindre brugeren senere udfører en særskilt eksplicit
handling, som er defineret med egne guards.

D007.6 ændrer ikke D003-D006s regler for, hvornår en alert må oprettes,
deduplikeres, leveres, retries eller sendes gennem recovery.

##### Fire separate lag

UI skal altid kunne skelne mellem mindst:

1. opportunity/lifecycle-event
2. logical alert oprettet
3. delivery attempt/status pr. kanal
4. recovery-/ambiguity-status

Disse lag må ikke fusioneres til én badge som fx `ALERTED`.

En lifecycle-transition kan eksistere uden en logical alert, og en logical
alert kan eksistere uden dokumenteret succesfuld levering.

##### Alert-historik pr. opportunity

For den konkrete `opportunity_id` skal alert-historikken, når canonical
records findes, kunne vise mindst:

- alert type
- relevant lifecycle-transition/reference
- kanal
- logical alert created-at
- delivery-status
- seneste delivery-attempt tidspunkt
- provider-/delivery-reference, når den canonical record indeholder den
- recovery-/ambiguity-status, når relevant

UI skal bevare den canonical identitet mellem status-transition, logical
alert, kanal og delivery-records og må ikke rekonstruere en ny alertidentitet
ud fra ticker, timestamp eller tekst alene.

##### HIGH_CONVICTION

`HIGH_CONVICTION` må kun fremstilles som årsag til en normal opportunity-alert,
når den canonical committed transition faktisk har oprettet den logical alert
efter de låste D003-D006-regler.

En case med lifecycle-status `HIGH_CONVICTION` må derfor ikke automatisk
vises som `alert sendt` eller `Telegram leveret`.

UI skal kunne vise forskellen mellem:

- `HIGH_CONVICTION` uden logical alert
- logical alert oprettet
- delivery pending/attempted
- delivery dokumenteret gennemført
- delivery/recovery-problem

##### THESIS_BROKEN

`THESIS_BROKEN` kan være alert-relevant efter D003, men lifecycle-status alene
er ikke dokumentation for, at en logical alert blev oprettet eller leveret.

Kun eksisterende canonical alert-/delivery-records må bruges til at vise en
faktisk sendt eller leveret Thesis Broken-alert.

##### Qualification labels og gate-resultater

`PROVISIONAL_CATALYST_OPPORTUNITY`, `PASS`, `FAIL` og `BLOCKED_DATA` må ikke
i sig selv fremstilles som opportunity-alerts.

UI må gerne forklare, at sådanne records indgår i beslutningsgrundlaget, men
må ikke fabrikere alert creation ud fra dem.

##### Read-only alert rendering

Åbning, refresh, filtrering, sortering eller navigation i alert-historikken må
ikke i sig selv:

- oprette en logical alert
- oprette et nyt outbox-item
- starte et delivery-attempt
- retry en delivery
- ændre recovery-state
- ændre lifecycle-status
- starte provider-fetch eller OpenAI-kald

##### Dedup og idempotency i visningen

UI skal respektere den canonical logical-alert-identitet og må ikke fremstille
retries eller flere delivery-attempts som flere forskellige alerts.

For normal opportunity-alerting følger logical dedup fortsat den låste
alert-/outbox-kontrakt, herunder kombinationen af:

- `status_transition_id`
- `alert_type`
- `channel`

UI må ikke skabe sin egen alternative dedup-nøgle.

Hvis flere attempts tilhører samme logical alert, skal de vises som attempts
under den samme alert og ikke som nye opportunity-alerts.

##### Delivery attempts

Et delivery-attempt er ikke det samme som dokumenteret levering.

Når canonical records findes, skal UI kunne skelne mellem mindst:

- attempt endnu ikke startet
- attempt startet/pending
- dokumenteret succes
- dokumenteret fejl
- udfald der kræver recovery eller afklaring

Provider-reference eller request-id må gerne vises som auditinformation, når
den canonical record indeholder det, men må ikke bruges af UI til at gætte
delivery-status.

En timeout eller manglende provider-respons må ikke automatisk vises som
`FAILED`, hvis canonical delivery/recovery-state siger, at udfaldet er
uafklaret.

##### Recovery og ambiguity

UI skal bevare forskellen mellem canonical recovery-resultater, herunder
`AUTHORIZED` og `AMBIGUOUS`, når disse findes i den låste recovery-kontrakt.

`AUTHORIZED` betyder kun, at den konkrete recovery-kontrakt tillader den
næste definerede handling. Det er ikke dokumentation for, at en ny levering
allerede er gennemført.

`AMBIGUOUS` betyder, at systemet ikke med tilstrækkelig sikkerhed kan afgøre
det tidligere delivery-udfald.

Ved `AMBIGUOUS` må UI aldrig tilbyde eller udføre blind resend som en
ubegrænset direkte handling.

Recovery skal følge den canonical recovery-proces, så systemet ikke skaber
semantiske dubletter ved at gensende en besked, der muligvis allerede blev
leveret.

##### Retry er ikke en ny logical alert

Et autoriseret retry/recovery-attempt må ikke:

- skabe en ny lifecycle-transition
- fremstilles som en ny High-Conviction-hændelse
- skabe en ny logical alert for samme dedup-identitet
- nulstille den historiske delivery/recovery-kontekst

UI skal vise retry/recovery som fortsættelse af den eksisterende logical
alert-historik.

##### Concurrent og gentagen rendering

Gentagne page loads, refreshes eller parallelle browserrequests må ikke skabe
nye alerts, attempts eller recovery-records.

Hvis canonical backend-state ændres mellem to reads, skal UI vise den senest
læste canonical state uden selv at forsøge at reparere eller komplettere
alert-workflowet.

##### Eksplicitte alert-handlinger

Hvis Opportunities-UX senere tilbyder brugerhandlinger omkring alerts, skal
de være separate, navngivne actions og aldrig skjulte side effects ved
page load, refresh, filter, sortering eller navigation.

En action skal operere på canonical alert-/delivery-identitet og må ikke
udlede target alene ud fra ticker, visningstekst eller seneste synlige række.

Før en action med side effects må udføres, skal backend mindst validere:

- authorization
- den konkrete logical-alert-/delivery-identitet
- current canonical state
- idempotency/dedup-kontrakt
- recovery-/ambiguity-state, når relevant
- at handlingen fortsat er tilladt efter concurrent ændringer

UI-tilgængelighed af en knap er ikke authorization. Server-side validation
er autoritativ.

##### Confirmation og konsekvens

En handling, der kan medføre en ny ekstern delivery, skal gøre konsekvensen
tydelig for brugeren før udførelse.

UI må ikke formulere en recovery-action som generisk `Send igen`, hvis den
canonical state ikke med sikkerhed tillader et resend.

Ved `AMBIGUOUS` skal UI i stedet vise, at tidligere delivery-udfald ikke er
sikkert kendt, og at normal blind resend ikke er tilladt.

En eventuel autoriseret recovery-action skal navngives efter den canonical
handling, den faktisk udfører, og følge backendens egne guards.

##### Delivery-status skal være evidensbaseret

UI må kun vise fx `leveret`, `sendt` eller tilsvarende successtatus, når den
canonical delivery-state dokumenterer den relevante betydning.

Følgende må ikke sidestilles:

- request accepteret til behandling
- delivery-attempt startet
- provider request-id modtaget
- logical alert oprettet
- dokumenteret succesfuld levering

Hvis provideren eller canonical state ikke kan bevise levering, skal UI vise
pending, failed, ambiguous eller anden faktisk canonical status frem for
at optimistisk antage succes.

##### Alertkanaler

Delivery-status skal vises pr. kanal. Succes på én kanal må ikke fremstilles
som succes på en anden kanal.

Hvis flere kanaler senere understøttes, forbliver logical alert og channel-
delivery adskilte. UI må ikke komprimere dem til én samlet `delivered`-status,
hvis channel-states er forskellige.

##### Anti-misleading alert-regler

UI må ikke:

- fremstille lifecycle-status som bevis for alert creation
- fremstille alert creation som bevis for delivery
- fremstille attempt som bevis for delivery
- fremstille provider-reference som bevis for delivery
- fremstille timeout som sikker failure, hvis canonical state er ambiguous
- fremstille retry som en ny logical alert
- fremstille `AUTHORIZED` som allerede gennemført recovery
- tilbyde blind resend ved `AMBIGUOUS`
- skjule delivery-/recovery-problemer bag en grøn opportunity-status
- ændre alert-historik eller canonical state ved almindelig rendering

##### Alert-action auditability

Hvis en eksplicit brugerhandling faktisk udføres, skal den efter de låste
persistence- og auditkontrakter kunne spores til den relevante canonical
alert/delivery/recovery-identitet og authorization-kontekst.

UI må ikke omskrive historiske attempts eller recovery-records efterfølgende
for at få et senere udfald til at se ud som om det var kendt tidligere.

#### D007.7 Tværgående præsentationskrav, accessibility og resilience

D007.7 fastlægger tværgående UX-regler for Opportunities-arbejdsfladen.
Det er ikke Command Center V3-design; den tværgående executive
informationsarkitektur hører fortsat til D009.

##### Loading og read-state

Loading er en UI-tilstand og må aldrig fremstilles som en canonical
opportunity-, lifecycle-, gate-, research-, alert- eller portfolio-state.

Ved almindelig loading må UI kun vente på/read canonical data eller en
versioneret projection/cache. Loading må ikke i sig selv udløse:

- provider-fetch
- OpenAI-generation
- Deep Research eller second opinion
- lifecycle-transition
- gate-evaluation
- alert/delivery
- portfolio-write
- budgetreservation

Skeletons/placeholders må ikke indeholde opdigtede scores, confidence,
statusser eller performance-tal, der kan forveksles med rigtige data.

##### Partial data

Hvis nogle sektioner kan vises sikkert og andre ikke kan, må UI vise den
gyldige del som partial view i stedet for nødvendigvis at skjule hele casen.

Den utilgængelige del skal markeres som utilgængelig, stale, invalid eller
anden faktisk canonical/read-fejl efter den relevante kontrakt.

Partial rendering må ikke:

- udfylde manglende felter med `0`
- genbruge en gammel værdi som current uden validity/freshness-indikation
- beregne manglende canonical felter i browseren
- skjule at en beslutningskritisk sektion mangler

Hvis fraværet betyder, at den canonical lifecycle faktisk er `DATA_HOLD`,
skal `DATA_HOLD` fortsat vises. Et rent UI-/read-problem må omvendt ikke
fabrikere `DATA_HOLD`.

##### Error states

UI skal skelne mellem mindst:

- view/read-fejl
- projection/cache utilgængelig
- canonical data utilgængelig eller ugyldig
- authorization-fejl
- konkret domæne-/validity-state, når en sådan canonical state findes

En teknisk UI- eller read-fejl må ikke fremstilles som negativ
investeringsvurdering, `REJECTED`, `THESIS_BROKEN` eller `DATA_HOLD`.

En fejl i én ikke-kritisk sektion må ikke automatisk gøre andre gyldige
sektioner ugyldige.

##### Retry af UI-read

En brugerhandling som `Prøv igen` må som default kun gentage den read-only
applikationsforespørgsel/projection-read, der fejlede.

Den må ikke skjult starte provider-fetch, AI-research, alert-retry eller
andre side effects.

Hvis en senere eksplicit recovery-/refresh-action har side effects, skal den
være særskilt navngivet og følge de relevante D004-D006-guards.

##### Fejldetaljer og secrets

Brugerrettede fejlbeskeder må gerne være diagnostiske, men må ikke eksponere:

- stack traces med secrets
- passwords eller auth/session-tokens
- provider-credentials eller API-nøgler
- interne secrets fra environment/configuration

Tekniske correlation-/request-identifikatorer må kun vises, når det er
sikkert og nyttigt for audit/support.

##### Responsive informationshierarki

Opportunities-UX skal bevare samme semantiske informationshierarki på
desktop, tablet og mindre skærme.

Responsive layout må ændre placering, kolonner, tabs eller disclosure, men
må ikke skjule eller ændre betydningen af beslutningskritiske felter som:

- opportunity-profile
- lifecycle-status
- Opportunity Score
- AI Confidence
- Data Confidence
- freshness/validity
- `DATA_HOLD` eller `THESIS_BROKEN`

På mindre skærme må sekundære detaljer gerne foldes sammen, men kritiske
status-, confidence- og validity-signaler skal fortsat være direkte synlige
eller entydigt markerede.

Brede tabeller eller evidensvisninger må bruge kontrolleret horizontal scroll,
stacking eller detail-disclosure frem for at trunkere centrale værdier uden
mulighed for at se dem.

##### Keyboard og fokus

Alle interaktive Opportunities-funktioner skal kunne anvendes uden mus.

Det gælder mindst:

- tabs
- filtre
- sortering
- søgning
- åbning/lukning af detailsektioner
- navigation mellem opportunity-cases
- eksplicitte actions, hvis sådanne senere aktiveres

Keyboard-fokus skal være synligt og følge en logisk rækkefølge, der svarer
til den visuelle og semantiske informationsstruktur.

En dialog, disclosure eller modal må ikke efterlade fokus et
uforudsigeligt sted efter lukning.

##### Semantisk struktur

Siden skal bruge en klar heading- og landmark-struktur, så bruger og
assistive technology kan forstå:

- hvilken opportunity-case der vises
- hvilken opportunity-profile der gælder
- hvilken sektion man befinder sig i
- hvilke controls der påvirker den aktuelle visning

Interaktive elementer skal have et entydigt accessible name. Ikoner alene
må ikke være eneste tekstlige forklaring på en væsentlig funktion.

##### Farve-uafhængig statuskommunikation

Farve må gerne understøtte status og risiko, men må aldrig være den eneste
bærer af betydning.

`HIGH_CONVICTION`, `DATA_HOLD`, `THESIS_BROKEN`, delivery-status, freshness
og confidence-begrænsninger skal også kunne forstås via tekst, label, ikon
med accessible name eller anden ikke-farvebaseret information.

Grøn må eksempelvis ikke alene betyde `leveret`, og rød må ikke alene
betyde `THESIS_BROKEN`.

##### Kontrast og læsbarhed

Tekst, controls, fokusindikatorer og statusmarkører skal have tilstrækkelig
visuel kontrast i de understøttede temaer.

Små sekundære metadata må ikke gøres så svage, at observationstidspunkt,
freshness, validity eller provenance reelt bliver ulæselige.

Kompakt informationsdensitet må ikke opnås ved at gøre kritiske labels,
timestamps eller confidence-/validity-information så små eller nedtonede,
at deres betydning går tabt.

##### Tooltips og disclosure

Kritisk information må ikke kun eksistere i hover-tooltip.

Tooltips må bruges til supplerende forklaring, men information som ændrer
fortolkningen af score, confidence, freshness, gate eller delivery skal også
være tilgængelig via keyboard/touch og kunne findes uden hover.

Progressive disclosure må gerne reducere visuel kompleksitet, men må ikke
skjule en kritisk blocker eller validity-begrænsning på en måde, der får
casens primære state til at fremstå misvisende.

##### Charts og grafiske forklaringer

Hvis score-, confidence-, timeline- eller outcome-data vises grafisk, skal
de samme centrale værdier og betydninger også være tilgængelige i tekstlig
eller struktureret form.

Et chart må ikke være den eneste måde at opdage fx:

- en scoreændring
- stale data
- et thesis-brud
- manglende outcome-data
- forskellen mellem Compounder og Catalyst

Grafik må ikke skabe falsk præcision gennem akser, decimaler eller visuel
skalering, som går ud over canonical data.

Hvis to dataserier ikke er semantisk direkte sammenlignelige, må fælles
akse, normalisering eller anden grafik ikke få dem til at fremstå som samme
måleenhed.

##### Motion og dynamiske opdateringer

Dynamiske UI-opdateringer må ikke bruge unødvendig animation til at
signalere investeringsmæssig betydning.

Ændringer i sortering, loading eller status skal kunne forstås uden at være
afhængige af bevægelse alene.

Den konkrete implementation skal kunne respektere reduceret motion, hvor
platformen/browseren understøtter det.

Automatiske visuelle opdateringer må ikke flytte fokus eller reorganisere
brugerens aktuelle kontekst på en måde, der gør det uklart, hvilken
opportunity-case eller handling der var aktiv.

##### Deterministic rendering og stabil view-state

Samme canonical input/projection og samme gyldige view-state skal give samme
semantiske UI-resultat.

Rendering må ikke afhænge af tilfældig rækkefølge, browser-side beregninger
eller ikke-versioneret skjult state, som kan ændre:

- hvilke cases der vises
- hvilken lifecycle-status der fremhæves
- score/confidence-værdier
- freshness/validity
- alert-/delivery-status
- Portfolio Fit

Hvis flere records har samme relevante sorteringsnøgler, skal den stabile
tie-breaker fra D007.2 anvendes.

Et almindeligt page reload må ikke ændre betydningen af en case alene fordi
UI-komponenterne mountes eller loader i en anden rækkefølge.

##### Performance og progressive disclosure

Opportunities-UX skal kunne håndtere den forventede mængde cases uden at
kræve, at alle detaildata renderes samtidigt.

Performance-optimering må bruge fx:

- server-side eller canonical pagination
- begrænset initial rendering
- lazy rendering af allerede tilgængelige read-only detaljer
- progressive disclosure
- versionerede projections/caches

Performance-optimering må ikke:

- starte skjulte provider- eller OpenAI-kald
- ændre canonical sortering eller filtre
- skjule kritiske blockers eller validity-problemer
- vise stale data som current for at reducere loadtid
- droppe cases uden tydelig pagination/view-semantik

Lazy rendering er ikke det samme som lazy data generation. Åbning af en
detaljesektion må ved almindelig read-only UX ikke starte ny research eller
anden betalt behandling.

##### Deep links

Det skal være muligt at linke reproducerbart til en konkret opportunity-case
og relevante read-only views, når authorization tillader det.

Et deep link skal bygge på stabile canonical identiteter som
`opportunity_id` og må ikke afhænge alene af ticker eller displaynavn.

Deep links og URL/query-state må ikke indeholde:

- passwords
- session-/auth-tokens
- API-nøgler
- provider-credentials
- andre account secrets

Et deep link må ikke omgå authorization eller give adgang til portfolio-,
alert- eller andre personaliserede data, som requesten ellers ikke må læse.

Hvis den refererede case ikke findes, er udløbet fra retention eller ikke er
autoriseret, skal UI vise den faktiske read-/authorization-state frem for at
fabrikere en ny case.

##### Browser-navigation og reproducerbarhed

Back/forward-navigation skal så vidt muligt kunne genskabe den read-only
view-state, som URL/query-state beskriver:

- tab
- filtre
- søgning
- sortering
- valgt opportunity-case

Genskabelse af view-state må ikke gentage tidligere side effects eller
genstarte research, alerts, deliveries eller portfoliohandlinger.

##### Opportunities-UX acceptance criteria

D007-UX er først klar til implementation, når mindst følgende kan testes:

- Compounder og Catalyst for samme instrument forbliver separate cases
- lifecycle-status, Opportunity Score, AI Confidence, Data Confidence,
  labels og Portfolio Fit vises som separate begreber
- `PROVISIONAL_CATALYST_OPPORTUNITY` vises aldrig som lifecycle-status
- `DEEP_RESEARCH` fremstilles som arbejdsstatus, ikke kvalitetsstempel
- `DATA_HOLD` fremstilles som datablokering, ikke bearish investeringsdom
- High-Conviction-eligible fremstilles ikke som committed `HIGH_CONVICTION`
- Compounder Score og Catalyst Score bruges ikke som én fælles
  tværprofil-ranking
- stale, invalid eller manglende data kan ikke skjules bag en tidligere score
- manglende data, Portfolio Fit eller outcomes fremstilles ikke som `0`
- normal page load, refresh, filtrering, sortering og navigation er
  side-effect-fri
- almindelig UI-read starter ingen provider-fetch eller OpenAI-generation
- alert creation, delivery attempt og dokumenteret levering kan skelnes
- `AMBIGUOUS` recovery giver ikke blind resend
- historical timeline omskriver ikke immutable records
- outcome-visning bevarer de separate Catalyst- og Compounder-horisonter
- portfolio-personalisering ændrer ikke objektiv opportunity-kvalitet
- authorization håndhæves server-side for personaliserede data og actions
- secrets eksponeres ikke i UI, fejlbeskeder eller URL/view-state
- kritisk statusinformation er forståelig uden farve alene
- centrale funktioner kan anvendes med keyboard
- kritisk information findes ikke kun i hover-tooltips eller charts
- partial/error states kan ikke forveksles med negative investeringsstates
- samme canonical data og samme view-state giver stabil, reproducerbar
  semantisk rendering

Disse acceptance criteria ændrer ingen D001-D006 business-, data-,
budget-, persistence- eller alertkontrakter. De operationaliserer alene,
hvordan de låste kontrakter må præsenteres og interageres med i
Opportunities-UX.














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

1. Kontrollér Git HEAD, `origin/main`, ren worktree og at V3-D007 fortsat er
   `LOCKED`.
2. Fortsæt med V3-D008 — shadow mode og kalibrering — uden at genåbne
   D001-D007s låste kontrakter.
3. V3-D009 forbliver `PENDING`, indtil dens egen Command Center V3- og
   informationsarkitekturkontrakt er designet og godkendt.
4. Implementér ingen V3-kode, før de efterfølgende relevante V3-kontrakter,
   som implementationen afhænger af, er formelt låst.

---

## 18. Checkpointkonklusion

Ved dette checkpoint er:

- V3-D001 låst
- V3-D002 låst
- V3-D003 låst
- V3-D004 låst
- V3-D005 låst
- V3-D006 låst efter D006.1-D006.8, structural/coverage-review,
  semantisk cross-review og final pre-lock diff-/integritetskontrol
- V3-D007 låst efter D007.1-D007.7, individuelle kritiske reviews,
  samlet D001-D006 cross-review og final diff-/integritetskontrol
- V3-D008 og V3-D009 er fortsat `PENDING`
- 100 DKK/måned er låst i D005 som global hard cap for samlet paid
  OpenAI-forbrug på tværs af V2 og V3
- Opportunity Radar er fortsat defineret som V3’s vigtigste nye funktion
- ingen V3-kode er implementeret
- production runtime ikke ændret af V3-blueprintarbejdet
