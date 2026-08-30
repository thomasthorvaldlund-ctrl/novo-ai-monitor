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
