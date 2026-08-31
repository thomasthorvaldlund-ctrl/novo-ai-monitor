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
