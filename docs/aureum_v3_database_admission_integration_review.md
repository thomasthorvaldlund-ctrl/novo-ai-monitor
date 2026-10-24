# Aureum V3 — tværgående database-admission-review

**Status: PROPOSED_FOR_REVIEW.**
**Dato: 2026-10-20.**
**Omfang: R1–R4; dokumentation af åbne integrationsfund.**

Dette notat samler den gennemførte drøftelse af fire integrationskrav. Det er
ikke et tillæg med allerede godkendte normative krav og ændrer ikke D006,
arkitekturdokumentet eller eksisterende kode. Oprettelse, staging, commit eller
push af notatet lukker ikke fundene og godkender ikke runtime.

## 1. Reviewbaseline og evidensgrænse

| Reference | Senest brugerbekræftede værdi |
| --- | --- |
| Repository | `/root/aureum-ai-platform` |
| Branch | `main` |
| HEAD | `1715353319a8c5783a867106e1cb4600fa70e7b2` |
| Arkitekturdokument | `docs/aureum_v3_database_admission_architecture.md` |
| Arkitekturdokument SHA-256 | `458b7e64587df27202291a28500fadd7a53f8b37eaee3efe7ab8e52e8e2e7aab` |
| Autoritativt blueprint | `docs/aureum_v3_blueprint.md` |
| Blueprint SHA-256 | `fc4f6fd2561169d393603eff9badc9e6d9e3e6342d40fbe5cd3eadbe0f27c8da` |
| Git-indeks/arbejdsområde før notatet | Rent ved seneste viste kontrol |

§14–18 er registreret som `APPROVED_ARCHITECTURE_ONLY` i baselinen. Den samlede
admission-arkitektur er ikke derved dokumenteret implementeringsklar. De
konkrete backend-, identitets-, koordinations- og reconciliation-mekanismer
kræver fortsat særskilte beslutninger og verifikation. [B1, B2]

Grundlaget er brugerleverede terminaludtræk af dokumentation, kode og statiske
søgninger samt de officielle kilder nedenfor. Reviewet er ikke en fuldstændig
inventering af alle adgangsveje eller en inspektion af den kørende service.
Guardens testkode er læst, ikke eksekveret i dette review. En tidligere måling af
SQLite `3.45.1` er et historisk observationspunkt, ikke en ny runtimekontrol.

Notatet adskiller tre former for udsagn:

- **Eksisterende grundlag:** Krav eller kodeadfærd fra de viste Aureum-udtræk.
- **Ekstern mekanik:** Dokumenteret SQLite-/Python-adfærd; ikke bevis for en
  bestemt installeret build eller valgt V3-backend.
- **Reviewforslag:** Afledte integrationsregler og foreslåede tests, som endnu
  ikke er godkendt eller implementeret.

## 2. Fundoversigt

| Fund | Status | Afgrænset problem |
| --- | --- | --- |
| R1 — Restore-historik | OPEN | Fravær efter restore kan ikke alene afgøre en tidligere operations udfald eller ekstern eksponering. |
| R2 — Fuld connection-livscyklus | OPEN | Koordinering skal omfatte forbindelsesforsøg før admission og fejl-/cleanup-forløb. |
| R3 — Backend-binding | OPEN | Runtime-evidens skal gælde den backend, som faktisk åbner work-connectionen. |
| R4 — Transaktionskontrol | OPEN | Bindingens faktiske transaktionsadfærd skal bevare L4's D006-grænser. |

Fundene er ikke konstaterede produktionsfejl. De skal afklares, før de berørte
runtime-flows kan godkendes. Notatet gør ikke krav på at være et udtømmende
sikkerhedsreview af hele V3.

## 3. R1 — Databasehistorik efter restore

**Eksisterende grundlag.** D006.1 kræver konsistent backup, snapshotvalidering,
kontrolleret restore og korrekt DB/WAL/SHM-parring. D006.6 forbyder blind
snapshot-rollback efter nyere business-writes og beskriver særskilt
recovery/forward-fix/disaster recovery. D006.7 kræver en uafhængig
`retention_restore_guard`. §18 kræver tilstrækkelig evidens før klassifikation
som `NOT_COMMITTED`. [B1, B2]

Den fremlagte grep-søgning fandt blandt andet lineage for fundamentals-snapshots
og epochs for kalibrering/policy. Disse fund etablerer ikke i sig selv en
restore-generation for hele databasen. Søgningen dækkede kun de valgte ord og
beviser ikke, at beslægtede regler mangler overalt i blueprintet. [B4]

**Ekstern mekanik.** SQLite Online Backup API kan erstatte destinationens
indhold med en kopi af kildedatabasen. Det kan give et konsistent snapshot uden
at bevare operationer fra en senere historik. [E1]

**Tænkt fejlscenarie, ikke en observation:** Backup B oprettes; operation X
committer senere, men kalderen mister resultatet; særskilt godkendt recovery
gendanner B; reconciliation finder ikke X. At den gamle proces er stoppet og
sen commit udelukket, beviser da ikke, at X aldrig tidligere committede.

**Foreslået integrationsregel.** Et fraværsbevis skal bygge på tilstrækkelig
historikevidens for den oprindelige operation. Efter restore eller anden
historikerstatning må manglende records ikke alene give `NOT_COMMITTED`.
Evidens for historikerstatning må ikke alene være en markør, der selv rulles
usynligt tilbage sammen med snapshotet. En restore-markør beviser heller ikke
i sig selv betaling, levering eller tidligere commit.

Hvis audit beviser en tidligere commit, men de nødvendige effekter mangler i
den restored database, er hverken `NOT_COMMITTED` eller almindelig succes uden
forbehold korrekt. Forløbet kræver særskilt recovery. Uklar historik må ikke
omgås med en ny operationsnøgle eller en ny databasegeneration.

Før automatisk genoptagelse skal de berørte workflows fortsat kunne opfylde
D005/D006: Budgeteksponering må ikke vurderes alene fra et ældre, lavere
forbrugstal; en restored `PENDING`-outbox må ikke alene autorisere send, hvis
senere authorization/levering kan være bortfaldet. Dette forslag erstatter ikke
D006.6's begrænsninger på restore. [B1]

**Foreslåede acceptance-cases:**

| Case | Forventet sikkerhedsegenskab |
| --- | --- |
| X committer efter B; derefter restore af B | Fravær klassificeres ikke automatisk som aldrig committed. |
| Tidligere commit er bevist, men effekterne mangler | Konflikten går til recovery, ikke almindelig succes eller blind gentagelse. |
| Nyere budget- eller leveringshistorik er ukendt | Berørte risikable handlinger genoptages ikke på utilstrækkelig evidens. |
| Nyt operations-ID efter restore | Ny identitet omgår ikke uafklaret eksponering eller leveringsrisiko. |

**Åbne valg:** Repræsentation af historikbinding, placering/bevaring af nødvendig
evidens og procedure for sikker genåbning. Ingen ny tabel, ekstern journal eller
generationsmekanisme vælges her.

### 3.1 R1-A — Placering og beskyttelse af historikevidens

**Status: PROPOSED_FOR_REVIEW; R1 forbliver OPEN.**
**Reviewdato: 2026-10-21.**

**Observeret kodegrundlag ved 5f475df.** Platform-/full-backup gennemløber
PROJECT_DIR med os.walk/tar.add, ikke V3-resolveren. Den viste backupkode
etablerer ikke et særskilt, valideret V3-snapshot. [B5]

Uden path-overrides går STATE_DIR via DATA_DIR tilbage til PROJECT_DIR.
Kun en manglende AUREUM_V3_DB_PATH vælger state_path-defaulten; en eksplicit
ugyldig V3-override afvises. Resolverens environ-mapping styrer kun V3-
overriden; defaulten bruger state_path med den allerede indlæste STATE_DIR.
Path-valget er ikke kontrol af filidentitet eller historik. [B6]

Disse observationer er fra committet kildekode. Faktisk servicemiljø,
databaseplacering, backupindhold og drift er ikke undersøgt i dette trin.

**Foreslået integrationskontrakt (ikke godkendt):**

1. Bevar aureum_paths.py og opportunity_database_config.py uændrede.
   Ingen ændring af globale V2-paths, default eller override-semantik.
2. Hold platformarkiv, valideret V3-snapshot og restore-historikevidens
   adskilt i formål. V3-backup skal bruge den konfigurerede, admitted
   database og D006s snapshotkontrakt, ikke blot et PROJECT_DIR-gennemløb.
3. Dokumentér, hvad hvert understøttet restore-forløb kan tilbageføre.
   Evidens, som skal afsløre historikerstatning, må ikke alene ligge i det
   materiale, der tilbageføres. En anden mappe er ikke alene tilstrækkelig,
   hvis hele serverens snapshot kan tilbageføre både database og markør.
   Dette er en designafledning, ikke en observeret hændelse.
4. Berørte paid-AI-, outbox- og reconciliation-forløb må ikke genoptages
   automatisk ved utilstrækkelig historikevidens. Ældre budgettal, restored
   PENDING eller nyt operations-ID er ikke alene sikker genåbning.

**Foreslåede acceptance-cases (ikke udført):**
- Ekstern V3-path: et projektarkiv alene opfylder ikke V3-backupkontrakten.
- Database og eneste markør tilbageføres sammen: ingen falsk NOT_COMMITTED
  eller automatisk genoptagelse på grundlag af den tilbageførte historik.
- Tilstrækkelig evidens mangler: berørte risikable workflows forbliver blokeret.

**Fortsat åbent:** Placering, bevaring, historikbinding og genåbningsmekanisme.
Ingen ny miljøvariabel, tabel, journal, mappe eller ekstern tjeneste vælges.
D006.6s restorebegrænsninger og D006.7s retention-/deletionkrav består.
R1-A lukker ikke R1; R2–R4 ændres ikke. Ingen runtime-/deploygodkendelse.

### 3.2 R1-B — Restore-forløb og kontrolleret genåbning

**Status: PROPOSED_FOR_REVIEW; R1 forbliver OPEN.**
**Reviewdato: 2026-10-21.**

**Grundlag og afgrænsning.** R1-B konkretiserer R1/R1-A som reviewforslag.
D006.1, D006.6, D006.7 og §17–18 bevarer deres eksisterende krav. [B1, B2]
Nedenstående afgrænsning er ikke en godkendt eller implementeret recoveryvej.
Ingen nye observationer af serverens restore- eller genstartsadfærd indgår.

**Foreslået V3.0-scope (ikke godkendt):**
- Kontrolleret V3-database-restore er den normale, testbare restorevej.
  Restore sker til quiesced staging og følger D006s snapshot-, fencing-,
  integritets-, schema- og retention-/deletionkontrakter.
- Server-/volume-rollback behandles som særskilt disaster recovery.
  Tilbageførte data, markører og aktiveringsindstillinger giver ikke alene
  tilladelse til automatisk genåbning af berørte workflows.
- Utilgængelig nyere database eller audit kræver særskilt evidensafklaring.
  Manglende historik må ikke erstattes af antagelser om ingen tidligere
  commit, nul forbrug eller ingen levering.

**Tre adskilte krav før genåbning:**
1. Snapshotvalidering: det valgte snapshot, schema og krævede
   integritetskontroller opfylder D006. Det beviser ikke alene historik.
2. Historikafklaring: tilstrækkelig evidens for relevante tidligere
   operationer, budgeteksponering, levering og obligatoriske sletninger.
3. Kontrolleret genåbning: kun workflows med opfyldte krav frigives gennem
   en eksplicit, auditerbar procedure. Eksisterende admission-, migration-,
   budget- og LIVE-gates gælder fortsat; ingen generel frigivelse.

**Foreslået håndhævelsesgrænse:**
- Genstartsproceduren skal holde berørte workers og eksterne handlinger
  tilbage, før de begynder at arbejde. Et flag, som selv tilbageføres med
  samme serverimage, er ikke alene tilstrækkelig håndhævelse.
- Autoriseret recovery-read er ikke almindelig business-read-admission
  og frigiver ikke betalte AI-kald eller outbox-send. §17 består.
- Ældre budgettal, gendannet PENDING eller nyt operations-ID giver ikke
  alene sikker genoptagelse. Utilstrækkelig evidens holder berørte
  risikable workflows blokeret.
- En disaster-recovery-beslutning ændrer ikke i sig selv D005/D006s
  budget-, dedup- eller retentionkrav og beviser ikke eksterne udfald.

**Foreslåede acceptance-cases (ikke udført):**
- Valideret snapshot med ukendt nyere budget-/leveringshistorik:
  ingen automatisk genåbning af de berørte risikable workflows.
- Database, lokal markør og aktiveringsflag tilbageføres sammen:
  ingen genaktivering alene på grundlag af den tilbageførte state.
- Restart under uafsluttet recovery: beskyttelsen består før worker-start.
- Autoriseret recovery-read: ingen implicit ret til eksterne handlinger.

**Fortsat åbent:** Håndhævelse før worker-start, historikevidens,
bevaring og auditerbar genåbningsmekanisme. Ingen konkret ekstern tjeneste,
journal, tabel, flag, sti eller servicekonfiguration vælges her.
R1-A forbliver et forslag. R1-B lukker ikke R1; R2–R4 ændres ikke.
Ingen ændring af D006, kode, V2-service eller runtime-/deploygodkendelse.

### 3.3 R1-C — Evidensgrundlag og workflowopdelt genåbning

**Status: PROPOSED_FOR_REVIEW; R1 forbliver OPEN.**
**Reviewdato: 2026-10-21.**

**Grundlag og afgrænsning.** R1-C konkretiserer evidenskravene i R1/R1-A/R1-B
som reviewforslag. D005/D006 og §17–18 bevarer deres eksisterende krav. [B1, B2]
Dette er ikke nye runtimeobservationer eller valg af lagringsteknologi.
En restore-markør beviser ikke alene tidligere commit, betaling eller levering.

**Foreslået grundlag pr. genåbningsvurdering (ikke godkendt):**
- Identificér det præcise restore-snapshot og den relevante databasehistorik.
- Angiv evidenskilder, oprindelse og bevaring, herunder om det aktuelle
  restore-forløb kan have tilbageført kilderne sammen med databasen.
- Dokumentér dækkede operationer/intervaller og kendte huller samt hvorfor
  dækningen er tilstrækkelig for den konkrete vurdering.
- Afgræns de berørte workflows og deres afhængigheder.
- Begrund resultatet med verificeret evidens og eksplicitte ukendte forhold;
  ingen generel godkendelse af hele platformen udledes af en delvurdering.

Et tidspunkt eller hash er ikke alene et dækningsbevis. En intakt kilde kan
mangle relevant historik. Oplysningerne ovenfor er foreslåede informationskrav,
ikke nye tabelnavne, API-felter eller implementerede records.

**Foreslåede workflowkrav:**
- Ukendt database-commit: tilstrækkelig historik til at afgøre den oprindelige
  operations udfald. Fravær i restored state er ikke alene NOT_COMMITTED.
  Bevis for tidligere commit, men manglende nødvendige canonical records,
  kræver særskilt recovery; hverken blind gentagelse eller almindelig succes.
- Paid AI: tilstrækkelig evidens til at rekonstruere relevant budgeteksponering,
  inklusive mulige startede attempts og uafklarede omkostninger, efter D005/D006.
  Ældre forbrugstal eller manglende usage må ikke alene give nul eksponering.
- Outbox: authorization-, completion- og reconciliation-evidens skal gøre
  næste handling sikker efter den eksisterende delivery-kontrakt.
  Restored PENDING er ikke alene bevis for, at en tidligere levering udeblev.
- Retention: nødvendige deletion-/purge-oplysninger og gældende policies skal
  anvendes efter D006.7, så restore ikke gør slettet materiale tilgængeligt igen.
  retention_restore_guard omdefineres ikke til bevis for alle betalinger
  eller leveringer.

**Foreslået beslutningsgrænse:**
- Manglende evidens er ikke i sig selv evidens for et negativt udfald.
- Utilstrækkelig historik holder de berørte risikable workflows blokeret.
- Delvis genåbning kræver begrundelse ud fra workflowenes afhængigheder og
  alle deres eksisterende gates. Budgetafklaring frigiver ikke automatisk
  outbox; recovery-read autoriserer ikke i sig selv eksterne handlinger.

**Foreslåede acceptance-cases (ikke udført):**
- Kilde består hashkontrol, men har et relevant dækningshul:
  ingen automatisk konklusion om ingen tidligere commit, omkostning eller levering.
- Tidligere commit er bevist, men canonical records mangler efter restore:
  særskilt recovery, ikke blind gentagelse eller almindelig succes.
- Budgetgrundlag er tilstrækkeligt, men leveringsstatus er ukendt:
  ingen automatisk outbox-frigivelse; andre workflows kræver egne gates
  og verificerede afhængigheder før eventuel genåbning.

**Fortsat åbent:** Evidensformat, lagring, bevaring, kontrol af dækning og
genåbningsmekanisme. Ingen ekstern tjeneste, ekstra database, journal, tabel,
API eller ny state machine vælges her. R1-A/R1-B forbliver forslag.
R1-C lukker ikke R1; R2–R4 ændres ikke. Ingen ændring af D006, kode,
V2-service eller runtime-/deploygodkendelse.

## 4. R2 — Koordinering fra før open til verificeret cleanup

**Eksisterende grundlag.** §12 lader composition root sammensætte dependencies,
men ikke eje SQL eller admission. §13 placerer filesystem-observation i L1,
connection acquisition i L2 og unit-of-work/admission/lifecycle i L4. §17
kræver race-sikker reader-admission og drain og blokerer ved ukendte connections
eller uafklaret lifecycle. R2 præciserer beskyttelsens start og fejlveje. [B2]

**Ekstern mekanik.** Et fejlet SQLite-open kan stadig returnere et handle, der
skal frigives. `sqlite3_close()` kan returnere `SQLITE_BUSY` og efterlade
forbindelsen åben. `sqlite3_close_v2()` kan returnere succes med udskudt
frigivelse, indtil statements, BLOB-handles og backup-objekter er afsluttet.
Interruption er heller ikke i sig selv afslutningsbevis. [E2, E3, E4]

**Tænkt fejlscenarie:** Migratoren ser ingen admitted readers, mens en anden
proces er inde i open, afvist admission eller efterfølgende cleanup.

**Foreslået integrationsregel.** L4 skal sikre deltagelse i fælles
livscykluskoordinering før L2's SQLite-open. Deltagelsen er ikke business-
admission og skal bevares til verificeret afslutning. Registreringen må ikke
forudsætte en uregistreret åbning af samme canonical database.

Ejerskab til et handle skal være entydigt også ved fejl før overdragelse fra L2
til L4. Afvist admission eller et returneret close-kald må ikke skabe et hul i
drain-evidensen. Koordineringen skal dække alle autoriserede processer og
relevante generationer; mekanismen kan være en eksplicit dependency til L4.

Migrationens egne backup-/verification-/recovery-forbindelser kræver særskilt
autorisation og fasepolitik. Kravet er ikke nul forbindelser under hele
migrationsforløbet. Ved fysisk restore/publicering skal adgangen til den gamle
database være afviklet, og nye normale åbninger fortsat være blokeret. SQLite
advarer om filudskiftning, mens eksisterende forbindelser bruger databasen. [E5]

En writer-lås er ikke en generel reader-drain-mekanisme: `BEGIN EXCLUSIVE` og
`BEGIN IMMEDIATE` er ens i WAL-mode. Observation må fortsat ikke bruge rå
open/read/close af aktive databasefiler som genvej; den dokumenterede
POSIX-lock-risiko består. [E5, E6]

**Foreslåede acceptance-cases:**

| Case | Forventet sikkerhedsegenskab |
| --- | --- |
| Barrier aktiveres under et open-forsøg | Forsøget overses ikke af koordineringen. |
| Open fejler og returnerer handle | Ejerskab og oprydning er dækket, selv uden business-admission. |
| Admission afvises efter open | Forsøget forbliver omfattet gennem cleanup. |
| Close er udskudt af statements/BLOB/backup | Ingen for tidlig drain-godkendelse. |
| Connection frigivet, commit-resultat ukendt | Ressourceafslutning og §18-udfald holdes adskilt. |

**Åbne valg:** Tværprocesprotokol, ejerskabsoverdragelse, crash-/cleanup-evidens og
faseautorisation. Ingen låsetype, ny registreringstabel eller public API vælges.

### 4.1 R2-A — Pre-open deltagelse og migrationsbarrierens rækkefølge

**Status: PROPOSED_FOR_REVIEW; R2 forbliver OPEN.**
**Reviewdato: 2026-10-23.**

**Grundlag.** D006.6 fastlægger fenced `NORMAL` -> `QUIESCED`,
writer-barriere og migrationsrækkefølge. §17 kræver race-sikker
read-admission og verificeret drain på tværs af processer. §12 og §13
placerer composition, connection acquisition og lifecycle hos deres
respektive lag. Dette afsnit er en præcisering til review, ikke en
ny godkendt migrationsprotokol.

**Foreslået integrationskontrakt (ikke godkendt):**
- L4 skal gennem en eksplicit koordineringsdependency etablere
  deltagelse i den fælles livscyklus før L2's SQLite-open-forsøg.
  Composition root må kun sammensætte dependencyen, ikke udføre
  koordinering eller database-admission på egen hånd.
- Etablering af deltagelse må ikke selv forudsætte et uregistreret
  open af samme canonical V3-database.
- Deltagelse før open er ikke business-admission og giver hverken
  ret til read, write eller omgåelse af gældende migration-control.
- Nye normale forsøg og committed `QUIESCED` skal have en fælles,
  race-sikker rækkefølge på tværs af processer og generationer.
  Et forsøg, som starter omkring barrier-commit, må hverken
  overses eller opnå ny normal admission efter barrieren.
- Et allerede registreret, men endnu ikke admitted, forsøg får
  ikke adgang alene på grund af registrering før barrier-commit.
  Allerede admitted reads følger §17's bounded afslutningsregler.
- Migrationens drain må ikke erklæres afsluttet alene ud fra
  fraværet af admitted readers. Den skal også håndtere relevante
  open-forsøg, delvist etablerede handles og uafklaret cleanup.
- Deltagelsen skal bevares gennem afvist admission, fejl i open,
  cleanup og eventuel ejerskabsoverdragelse, indtil afslutningen
  er verificeret. Detaljeret handle-ejerskab og cleanup-evidens
  udestår i R2 og fastlægges ikke af R2-A alene.
- Før schemaændrende migration gælder §17's verificerede drain.
  Dette ændrer ikke D006.6's `BEGIN IMMEDIATE`, fencing,
  migration-ID/checksum, atomicitet eller verification.
- BACKFILL og øvrige migrationsfaser skal følge deres særskilte
  D006.6-kontrakter. R2-A indfører ikke en automatisk global
  reader-drain for enhver backfill-batch.
- Migrationens egne backup-, verification- og recovery-forbindelser
  kræver fortsat særskilt faseautorisation; R2-A giver dem ingen
  implicit undtagelse fra den eksisterende sikkerhedspolitik.

**Foreslåede acceptance-cases (ikke udført):**
- Barrier-commit konkurrerer med registrering før SQLite-open:
  ingen tabte forsøg eller normal admission efter barrieren.
- Barrier-commit sker efter registrering, men før faktisk open:
  registreringen er ikke en genbrugelig adgangstilladelse.
- Open fejler eller admission afvises med et uafklaret handle:
  ingen falsk drain-succes før verificeret cleanup.
- To processer og forskellige generationer konkurrerer om
  open, barrier og drain: en lokal tæller kan ikke alene frigive DDL.
- Ukendt participant-/cleanup-status blokerer den berørte
  schemaændring, indtil tilstrækkelig evidens foreligger.
- BACKFILL uden fysisk schemaændring behandles fortsat efter
  sin godkendte fasekontrakt, ikke som implicit ny DDL-barriere.

**Fortsat åbent:** Konkret tværprocesprotokol, lineariseringsmekanisme,
registreringens livscyklus, crash-reconciliation, handle-ejerskab
og særskilte migrationsforbindelser. Ingen ny lås, tabel, journal,
database, public API eller implementering vælges her. R2 forbliver
OPEN; R1/R3/R4 ændres ikke. Ingen ændring af D006, §12-§18,
V2, runtime, service, migration, deploy eller LIVE.

### 4.2 R2-B — Handle-ejerskab og verificeret cleanup

**Status: PROPOSED_FOR_REVIEW; R2 forbliver OPEN.**
**Reviewdato: 2026-10-23.**

**Grundlag og afgrænsning.** §13 og §15 placerer det overordnede
connection-, transaction- og cleanup-ansvar hos L4. §17 kræver
verificeret lifecycle-afslutning før reader-drain. R2-A foreslår
koordineret deltagelse allerede før SQLite-open. [B2]
SQLite C-API kan returnere et handle ved fejlet open. Et close-kald
kan afvises eller efterlade udskudt ressourcefrigivelse. [E2, E3]
Den senere valgte Python-/SQLite-binding skal vurderes særskilt.

**Foreslået integrationskontrakt (ikke godkendt):**
- L4 har det overordnede lifecycle- og cleanup-ansvar fra
  registreret pre-open-forsøg til verificeret endelig afslutning.
- L2 skal have entydig, afgrænset håndtering af ethvert handle,
  som et open-forsøg kan efterlade, indtil L4 udtrykkeligt
  overtager det. Fejl før overdragelsen må ikke miste ejerskab.
- Overdragelsens succes eller fejl skal være entydig. Hverken
  dobbelt cleanup eller et ejerløst handle må kunne antages sikkert.
- Fejl under open, connection-konfiguration, sidecar-verifikation
  eller afvist admission skal følge den kontrollerede cleanup-grænse.
  Ingen sådan fejl giver business-admission eller implicit retry.
- Åbne statements/cursors, BLOB-handles og backup-objekter skal
  medregnes, når den konkrete binding kan holde SQLite-ressourcer
  i live efter et close-forsøg.
- Et returneret close-kald er ikke alene bevis for endelig
  ressourcefrigivelse. Særligt må udskudt frigivelse og fejlet
  close ikke fejlklassificeres som verificeret cleanup.
- Ukendt eller fejlet cleanup må ikke frigive en participant eller
  give reader-drain-succes uden tilstrækkelig lifecycle-evidens.
  Crash- og stale-participant-reconciliation afklares i R2-C.
- Efter-close filesystem-metadata kan klassificere sidecar-tilstand,
  men beviser ikke alene, at handles og SQLite-ressourcer er væk.
  L1 må ikke omgå §15 med rå DB/WAL/SHM-open/read/close.
- Legitimiteten af WAL/SHM-sideeffects afgøres efter §14-§15.
  En fejlet operation kan have autoriserede filesystem-effekter;
  ingen manuel sletning, nulstilling eller reparation indføres.
- Verificeret cleanup, kendt commit, kendt rollback og ukendt
  operationelt udfald skal holdes adskilt. §18's reconciliation
  må ikke erstattes med antagelser ud fra et close-resultat.
- Migrationens særlige connections og process crashes forbliver
  særskilte R2-afklaringer og får ingen implicit adgang her.

**Foreslåede acceptance-cases (ikke udført):**
- Fejlet open returnerer et delvist etableret handle:
  handle-håndtering og cleanup er dækket før drain-succes.
- Fejl mellem L2's open og L4's overtagelse:
  ingen mistet eller tvetydig ressourceejer.
- Afvist admission efter oprettet connection:
  ingen tidlig frigivelse af lifecycle-deltagelsen.
- Close afvises som busy eller frigivelsen udskydes:
  intet falsk bevis for fuldført resource cleanup.
- Aktiv cursor, BLOB eller backup overlever close-forsøg:
  drain følger verificeret ressourceafslutning.
- WAL/SHM findes stadig efter sidste close:
  ingen automatisk korruptionsklassifikation eller manuel unlink.
- Forbindelsen frigives, men commit-udfaldet er ukendt:
  cleanup-succes giver ikke NOT_COMMITTED eller tilladelse
  til blind gentagelse eller ekstern side effect.

**Fortsat åbent:** Bindingens faktiske handle-semantik,
overdragelsesmekanisme, ressourceinventar, dokumenterbar afslutning,
fejlhåndtering og crash-reconciliation. Ingen konkret close-API,
SQLite-backend, lås, tabel, journal eller implementering vælges her.
R2 forbliver OPEN; R1/R3/R4 ændres ikke. D006, §12-§18,
V2, runtime, migration, deploy og LIVE forbliver uændrede.

### 4.3 R2-C — Crash, stale participants og faseautoriserede forbindelser

**Status: PROPOSED_FOR_REVIEW; R2 forbliver OPEN.**
**Reviewdato: 2026-10-23.**

**Grundlag og afgrænsning.** R2-A foreslår koordinering før SQLite-open,
og R2-B foreslår entydigt handle-ejerskab og verificeret cleanup.
§17 kræver fælles, race-sikker reader-drain, herunder ukendte
processer/generationer. D006.5 fastlægger lease-/fencing- og
business-recovery-kontrakter; D006.6 fastlægger migrationsfaser,
pre-migration backup og kontrolleret genåbning. [B1, B2]
R2-C vælger ingen runtime-protokol og lukker ikke R2.

**Foreslået integrationskontrakt (ikke godkendt):**
- En deltagers livscyklus må ikke erklæres afsluttet alene på grund
  af lease-expiry, timeout, manglende heartbeat eller fravær af
  aktiv business-admission. Disse forhold kan udløse afklaring,
  men er ikke i sig selv evidens for frigivne SQLite-ressourcer.
- Crash-/stale-reconciliation skal relatere deltagelsen til dens
  konkrete proces-/generation-/forbindelsesforsøg og afklare,
  om relevant SQLite-aktivitet eller ressourceejerskab kan bestå.
  Genbrugt PID eller ældre registrering må ikke forveksles med
  verificeret afslutning af den oprindelige deltager.
- En konstateret procesafslutning kan indgå i evidensen, men
  er kun tilstrækkelig, hvis den valgte backend, VFS og
  proces-/handlemodel understøtter den konkrete konklusion.
  Ukendte nedarvede/delte handles og uafsluttede ressourcer
  må ikke automatisk klassificeres som lukkede.
- Den fælles koordinering skal bevare eller sikkert reconcile
  uafklarede deltagere på tværs af crash og genstart, så et
  tab af lokal memory-state ikke kan give falsk reader-drain.
  Den konkrete evidenskilde og bevaringsmekanisme er åben.
- Kun verificeret lifecycle-afslutning eller tilsvarende
  dokumenteret sikker crash-reconciliation må lade en deltager
  udgå af drain. Ukendt status blokerer den berørte DDL-/restore-
  grænse; manuel eller automatisk genåbning kræver særskilt
  verificerbar beslutning og må ikke omgå eksisterende gates.
- D006.5's job-lease/fencing og job_run-recovery må ikke bruges
  som erstatning for connection-drain. Business-commit, paid AI
  og outbox-udfald behandles fortsat efter D006/§18 og R1;
  frigivet connection beviser ikke, at ekstern side effect udeblev.
- Normale V3-forbindelser skal respektere committed `QUIESCED`
  og §17's reader-/writer-gates. Tidligere generationer må
  ikke få adgang alene ved procesrestart eller ældre snapshots.
- Migrationsforbindelser skal være eksplicit scope- og
  faseautoriserede samt indgå i relevant lifecycle-evidens.
  Under `QUIESCED` gælder særskilt fenced backup/preflight;
  disse forbindelser afsluttes før schemaændrende migration.
  Under `MIGRATING` gælder særskilt fenced verification/recovery.
- Hver særskilt migration-operation skal respektere relevant
  migration-ID/checksum, aktiv lease/fencing og D006.6's
  kontrol af schema, snapshot og fase. Et mistet lease giver
  ikke ret til at fortsætte DDL, verification eller frigive barrier.
- Der kræves ikke nul autoriserede migrationsforbindelser i
  alle faser. Ved fysisk restore/fil-publicering skal derimod
  være tilstrækkelig evidens for, at relevante ældre forbindelser
  og generationer ikke fortsat anvender den gamle database.
  Ingen manuel WAL/SHM-reparation eller rå DB-open som probe.
- Bounded, idempotente backfills følger fortsat deres særskilte
  D006.6-fasekontrakter og får ikke automatisk et nyt globalt
  drain-krav for hver batch uden en schema-/restore-grænse.

**Foreslåede acceptance-cases (ikke udført):**
- Lease udløber, men den gamle proces kører videre med connection:
  expiry alene må ikke frigive deltageren eller autorisere DDL.
- Worker crasher under open eller cleanup; deltagelse er ukendt:
  migration forbliver blokeret, indtil lifecycle kan reconciles.
- Proces-ID genbruges eller registreringen er stale efter restart:
  ingen falsk klassifikation af originalt handle som afsluttet.
- Procesdød er bevist, men backend-/handle-evidens er utilstrækkelig:
  ingen ubetinget drain-godkendelse eller usikker filudskiftning.
- Autoriseret backup under `QUIESCED` og verification under
  `MIGRATING`: korrekt scope/fencing og afslutning ved fasegrænse.
- Migration-lease mistes under verification eller recovery:
  ingen DDL-fortsættelse eller `MIGRATING` -> `NORMAL` uden ny
  godkendt reconciliation og gældende kontrolkontrakter.
- Connection-lifecycle afsluttes, men commit eller ekstern
  levering er ukendt: ingen afledning af negativt business-udfald.

**Fortsat åbent:** Konkrete participant-identiteter, tværproces-
koordinering, crash-evidens, backend-/OS-semantik, faseautorisation
og verifikation af ressourcefrigivelse. Ingen lock-type, journal,
tabel, database, API, service eller implementering vælges her.
R2 forbliver OPEN; R1/R3/R4 ændres ikke. D006, §12-§18,
V2, migration, runtime, deploy og LIVE forbliver uændrede.

### 4.4 R2-D — V3.0 maintenancekoordinering og verificeret drain

**Status: PROPOSED_FOR_REVIEW; R2 forbliver OPEN.**
**Reviewdato: 2026-10-24.**

**Grundlag og afgrænsning.** R2-A fastlægger som reviewforslag deltagelse
før SQLite-open, R2-B entydigt handle-ejerskab og verificeret cleanup,
og R2-C crash-/stale-reconciliation samt faseautoriserede
migrationsforbindelser. §17 kræver en fælles race-sikker grænse mellem
normal read-admission og committed `QUIESCED`. D006.5/D006.6 og §18
bevarer deres eksisterende fencing-, migration- og reconciliation-krav.
Dette afsnit vælger ingen konkret runtime-mekanisme og lukker ikke R2.

**Præcisering af kandidatmodellerne (ikke godkendt):**
Kontrolleret V3-maintenance med stop/drain og online koordinering er ikke
to alternativer til fælles koordinering. Begge kræver en race-sikker
pre-open-/lifecycle-grænse. Forskellen er, om normale V3-workers holdes
aktive gennem maintenance-forløbet eller afskærmes som del af en
kontrolleret maintenance-procedure.

**Foretrukken kandidat for V3.0 (ikke godkendt):**
Til schemaændrende migrationer på den godkendte enkeltserver-målprofil
foretrækkes kontrolleret V3-maintenance, hvor normale V3-start- og
databaseadgangsveje afskærmes, eksisterende deltagere drænes eller
reconciles, og kun eksplicit faseautoriserede migrationsforbindelser
kan fortsætte. Præferencen begrundes i lavere forventet
koordinationskompleksitet, ikke i at processtop erstatter D006 eller §17.

**Foreslået integrationskontrakt (ikke godkendt):**
- Maintenance-spærringen skal omfatte nye normale V3-units of work og
  SQLite-open-forsøg fra både nye og allerede kørende processer.
  Et service-stop alene er derfor ikke et fuldstændigt adgangsbevis.
- Alle normale V3-adgangsveje skal passere den samme godkendte
  pre-open-/admission-grænse. Et forsøg, som konkurrerer med
  maintenance-overgangen, skal enten være registreret og afvikles
  kontrolleret eller afvises; det må ikke forsvinde mellem to checks.
- D006.6's migration-lease/fencing og committed `NORMAL` -> `QUIESCED`
  bevares. Maintenance-spærringen er et ekstra fail-closed krav og
  må ikke erstatte den canonical migrationsbarriere.
- Migrator-crash må ikke automatisk genåbne normal V3-adgang.
  Frigivet proces-/OS-lås, timeout, lease-expiry eller observeret
  processtop er ikke alene bevis for sikkert afsluttet maintenance.
- Et crash før eller efter barrier-commit skal kunne efterlade en
  blokerende, reconcilerbar tilstand, indtil både maintenance-status,
  migration-control og relevante connection-lifecycles er afklaret.
  Den konkrete persistens- og koordineringsmekanisme vælges senere.
- Migrationens egne lease-, barrier-, backup-, DDL-, verification-
  og recovery-forbindelser skal have eksplicit faseautorisation.
  De må ikke være skjulte undtagelser fra lifecycle-evidensen.
- Drain må ikke kræve nul migrationsforbindelser i alle faser.
  Protokollen skal i stedet skelne normale participants fra
  migrationsparticipants og undgå en rækkefølge, hvor migratoren
  venter på sig selv eller holder en ressource, som cleanup behøver.
- Ventetid på processtop, participant-drain eller ekstern backup må
  ikke indføres som langvarigt arbejde inde i en SQLite-write-
  transaction. D006's korte transactions og fasegrænser består.
- En fri koordinationslås er ikke alene cleanup-bevis. Den valgte
  mekanisme skal dokumentere, at lifecycle-beskyttelsen dækker
  relevante SQLite-ressourcer indtil verificeret afslutning, og at
  crash håndteres efter R2-C.
- Verificeret connection-cleanup beviser ikke `NOT_COMMITTED`.
  §18's COMMITTED/NOT_COMMITTED/UNRESOLVED-reconciliation forbliver
  særskilt og må ikke afledes af processtop, close eller drain.
- Normal genåbning kræver både D006's gyldige verification/fencing og
  committed tilbagevenden til `NORMAL` samt afklaring af den ekstra
  maintenance-/lifecycle-spærre. Ingen af de to lag må alene kunne
  give adgang ved ukendt eller modstridende evidens.
- V3-databaseadgang skal bindes til den betroede V3-konfiguration,
  §14-identitet og korrekt schema-/manifestkontrakt. Forskellige
  miljøvariabelnavne eller pathnames er ikke alene bevis for, at
  canonical V3 er fysisk adskilt fra V2's account/auth-store.
- V2-web/login/TOTP må ikke stoppes eller migreres som en bivirkning
  af V3-maintenance. Eksisterende D005/D006 fail-closed regler for
  funktioner, der senere afhænger af V3, gælder dog fortsat.
- Online tværproceskoordinering forbliver en mulig senere model, men
  får ingen svagere krav til pre-open-race, cleanup, crash, fencing,
  databaseidentitet eller reconciliation.

**Foreslået protokolrækkefølge (ikke implementeret):**
1. Afskærm nye normale V3-open/admission-forsøg gennem den fælles
   maintenance-/pre-open-grænse uden at ændre V2.
2. Acquire og verificér migration-lease/fencing og commit D006.6's
   `NORMAL` -> `QUIESCED` efter dens eksisterende kontrakt.
3. Dræn eller reconcile alle relevante normale participants,
   open-forsøg, transactions og cleanup-forløb. Ukendt status blokerer.
4. Kør kun de særskilt autoriserede backup-/migration-/verification-
   forbindelser, som den aktuelle D006/§17-fase tillader.
5. Efter migration: gennemfør påkrævet verification, smoke/integrity
   og fencing-kontrol før committed `MIGRATING` -> `NORMAL`.
6. Frigiv først normal V3-adgang, når både canonical migration-state
   og maintenance-/lifecycle-evidens er konsistente og sikre.
7. Ved crash eller ukendt udfald: ingen automatisk genåbning eller
   blind DDL-retry; brug særskilt autoriseret reconciliation.

**Foreslåede acceptance-cases (ikke udført):**
- En allerede kørende worker starter nyt open samtidigt med maintenance:
  forsøget overses ikke og får ingen sen normal admission.
- Migratoren crasher før `QUIESCED`, efter `QUIESCED` eller under
  verification: frigivne proceslåse åbner ikke automatisk V3 igen.
- Normal participant crasher med ukendt cleanup eller nedarvede/delte
  handles: ingen drain-succes uden tilstrækkelig lifecycle-evidens.
- Migrationens egen backup-/verification-connection er aktiv:
  protokollen tæller den korrekt og undgår self-deadlock.
- DDL committer, men commit-ACK mistes: §18-reconciliation anvendes;
  ingen blind DDL-gentagelse eller falsk rollback.
- Canonical state er `NORMAL`, men maintenance-afslutningen er ukendt:
  normal V3-adgang forbliver blokeret indtil sikker reconciliation.
- Maintenance-status ser afsluttet ud, men control-head er
  `QUIESCED`/`MIGRATING`: ingen normal admission.
- V3-konfiguration peger mod V2 account/auth-store eller identiteten
  kan ikke bevises: fail-closed før canonical V3-adgang.
- V2 login/TOTP fortsætter uden V3-stophandlinger, mens funktioner
  med låst V3-afhængighed fortsat følger deres egne fail-closed gates.

**Fortsat åbent:** Konkret maintenance-spærre, tværprocesprotokol,
lineariseringsbevis, participant-identitet, crash-persistens,
backend-/OS-handlebinding, resource-cleanup og recovery-API.
Ingen fil-/proceslås, tabel, journal, service, systemd-policy,
SQLite-backend eller implementering vælges her. R2 forbliver OPEN;
R1/R3/R4 ændres ikke. D006, §9-§18, V2, runtime, migration,
deploy og LIVE forbliver uændrede.

## 5. R3 — Runtime-evidens bundet til faktisk backend

**Eksisterende grundlag.** Den viste `require_sqlite_wal_reset_fix()` læser
standardbibliotekets `sqlite3.sqlite_version_info`; den beskriver sig selv som
en snæver release-gate, ikke build-provenance eller fuld admission. §14 udskyder
valget af den identity-capable backend. Den statiske importsøgning fandt ingen
direkte produktionskalder af guarden og ingen match på de søgte APSW-/pysqlite3-
importformer; det beviser ikke fravær af installerede pakker eller dynamiske
adgangsveje. [B2, B3]

Testfilen erstatter versionsattributten med simulerede værdier. Testen med
`(3, 45, 1)` er derfor ikke en aktuel runtimeobservation. I/O-mocks aktiveres
efter modulimport; AST-testen supplerer, men udgør ikke integrationstest af en
fremtidig backend, factory og cleanup. Testene er ikke kørt i dette review. [B3]

**Ekstern mekanik.** Python beskriver versionsattributten som modulets
runtimebiblioteks version. SQLite's library-version/source-ID-funktioner
rapporterer oplysninger fra det kaldte bibliotek, ikke kun headers. Disse
oplysninger er ikke alene bevis for alle connection-capabilities. [E7, E8]

**Foreslået integrationsregel.** Den kontrollerede backend skal være den backend,
som den godkendte factory anvender til L2's work-connection. Evidens fra en anden
binding/proces/connection må ikke alene give admission. Runtime-/build-policy
kontrolleres før open; faktisk connection-evidens kontrolleres før business-
adgang. L4 sammenholder dette inden for den konkrete unit of work.

Et accepteret versionsnummer erstatter ikke §14's filbinding, sidecar-kontrol,
settings eller schema-verifikation. R3 tillader ikke caller-leveret version,
`allow_unpatched` eller fallback til en svagere backend. V2's SQLite-brug og den
snævre guards eksisterende ansvar ændres ikke af notatet.

**Foreslåede acceptance-cases:**

| Case | Forventet sikkerhedsegenskab |
| --- | --- |
| Backend A godkendes, factory forsøger B | A's evidens kan ikke autorisere B. |
| Version accepteres, krævet capability mangler | Ingen business-admission. |
| Backend afvises | Ingen stiltiende fallback. |
| Backend/konfiguration skifter efter kontrol | Tidligere evidens kan ikke ukritisk genbruges. |

**Åbne valg:** Backend, build-/capability-policy og evidensbinding til factory og
connection. Ingen pakkeinstallation, global SQLite-udskiftning eller ny
versionsallowlist vælges.

### 5.1 R3-A — Backend, factory og actual-connection evidensbinding

**Status: PROPOSED_FOR_REVIEW; R3 forbliver OPEN.**
**Reviewdato: 2026-10-24.**

**Grundlag og afgrænsning.** Den eksisterende WAL-reset release-guard
kontrollerer standardbibliotekets loaded SQLite-version og åbner ingen
database. Den eksisterende connection-contract validerer allerede
observerede værdier og udfører ingen I/O. De gennemgåede tests verificerer
disse smalle egenskaber med simuleret metadata og konstruerede
observationer; de er ikke integrationstest af en backend/factory/
work-connection-kæde. [B3]

§13 kræver actual-connection observation i L2, §14 kræver en
identity-capable backend og connection-bundet identitetsevidens,
og R3 kræver, at den kontrollerede backend er den backend, som faktisk
åbner den konkrete work-connection. Dette afsnit vælger ingen backend.

**Foreslået integrationskontrakt (ikke godkendt):**
- Pre-open runtime-, build- og capability-evidens skal være bundet
  til den konkrete SQLite-binding/backend, som den godkendte L2-factory
  efterfølgende bruger. Evidens fra en anden binding eller proces
  kan ikke alene autorisere connection-open.
- Factoryen må ikke kontrollere backend A og derefter åbne gennem
  backend B, direkte eller gennem implicit fallback.
- Standardbibliotekets `sqlite3.sqlite_version_info` kan kun være
  evidens for den SQLite-runtime, som det konkrete stdlib-modul er
  bundet til. Den giver ingen automatisk attestering af APSW,
  pysqlite3 eller en anden fremtidig binding.
- Et accepteret versionsnummer er ikke alene capability-evidens.
  Krævede funktioner fra §14, §15 og den valgte transaction-kontrakt
  skal verificeres særskilt mod den backend, der faktisk anvendes.
- L2 skal indsamle connection-state og krævet backend-evidens fra
  den konkrete work-connection, som L4 ejer. Caller-konstruerede
  `ConnectionStateObservation`-værdier må ikke alene være
  authoritative admission-evidens.
- Den rene connection-contract kan fortsat validere et observation-
  objekt, men provenance/binding af observationen til den faktiske
  connection skal etableres af den godkendte observation/factory-
  kæde uden at gøre kontraktmodulet til I/O-owner.
- Connection-identitet, access mode, relevante settings og
  capabilities skal knyttes til samme bounded unit of work.
  Evidens fra en tidligere connection må ikke ukritisk genbruges.
- Backend-, adapter-, factory- eller relevant konfigurationsskift
  invaliderer tidligere backend-/connection-evidens, medmindre en
  eksplicit versioneret kontrakt dokumenterer sikker genbrug.
- Backend-afvisning eller manglende capability må give fail-closed.
  Ingen automatisk fallback til stdlib, anden binding, svagere
  identity-kontrol eller caller-leveret versionsmetadata er tilladt.
- Build-/source-provenance kan være nødvendig, når releaseversionen
  alene ikke er tilstrækkelig, eksempelvis ved vendor-backport.
  Den konkrete provenance-mekanisme vælges ikke her.
- V2's eksisterende SQLite-adgang må ikke globalt omlægges eller
  opgraderes som bivirkning af V3-backendvalget.
- R3-A giver ingen database-admission alene; L1-L4, §14-§18,
  schema/manifest, migration, transaction og business-gates
  gælder fortsat.

**Foreslåede acceptance-cases (ikke udført):**
- Pre-open kontrol udføres mod backend A, mens factory forsøger B:
  ingen SQLite-open eller business-admission gennem B.
- Samme versionsnummer findes i to forskellige bindings/builds:
  versionslighed alene giver ingen capability- eller provenance-
  lighed.
- Caller leverer et perfekt formet `ConnectionStateObservation`
  uden dokumenteret connection-provenance:
  ingen authoritative admission alene på objektets værdier.
- Factory åbner korrekt backend, men actual connection mangler en
  krævet §14-capability:
  fail-closed før business-adgang.
- Backend eller factory-konfiguration ændres mellem pre-open-gate
  og connection-open:
  tidligere evidens må ikke ukritisk genbruges.
- Godkendt backend afvises eller mangler:
  ingen silent fallback til en anden SQLite-binding.
- Vendor-backport rapporterer en version, som release-guarden afviser:
  ingen runtime-admission gennem den nuværende guard. Eventuel senere
  accept kræver særskilt godkendt build-/source-policy og binding til
  den backend, som den godkendte factory faktisk anvender.
- V3-backendvalget ændres:
  V2's account/auth SQLite-path påvirkes ikke automatisk.

**Fortsat åbent:** Konkret SQLite-backend, factory-shape,
capability-manifest, build-/source-provenance, connection-observer
og den konkrete evidensbinding mellem backend og connection.
Ingen pakkeinstallation, global SQLite-udskiftning, databaseåbning,
public API eller runtime-implementation vælges her. R3 forbliver OPEN;
R1/R2/R4 ændres ikke. D006, §12-§18, V2, deploy og LIVE
forbliver uændrede.

### 5.2 R3-B — Backend capability-manifest og kandidatgrænse

**Status: PROPOSED_FOR_REVIEW; R3 forbliver OPEN.**
**Reviewdato: 2026-10-24.**

**Observeret kandidatstatus.** Den seneste read-only inventering i den
aktive Aureum-venv viste Python 3.12.3 med standardbibliotekets `sqlite3`
og loaded SQLite 3.45.1. Den eksisterende WAL-reset release-policy
accepterer ikke 3.45.1. APSW og pysqlite3 blev ikke fundet ved den
afgrænsede import-specifikationstest. Ingen database blev åbnet.
Observationen er et aktuelt inventory-punkt, ikke et backendvalg.

§14 kræver desuden en identity-capable backend med capabilities, som
ikke alene følger af et accepteret versionsnummer. R3-A kræver binding
mellem backend, factory og den faktiske work-connection.

**Foreslået capability-manifest (ikke godkendt):**
En backendkandidat skal have en versioneret, reviewbar capability-profil,
som mindst beskriver og kan verificere følgende kategorier:

- **Backend/runtime-identitet:** Den konkrete Python-binding/adapter,
  runtime SQLite-version og relevant build-/source-provenance skal
  kunne knyttes til den backend, som factoryen faktisk anvender.
- **Release-policy:** Den gældende WAL-reset release-/build-policy
  skal være bestået ved enhver V3-connection-open, som bruger den
  godkendte backend. En afvist release må ikke fortsætte via override,
  fallback eller anden implicit binding.
- **Existing-only open:** Factoryen skal kunne åbne den valgte
  eksisterende V3-database uden implicit create eller fallback til
  en anden database.
- **No-follow/open-policy:** Backend/factory skal dokumenteret kunne
  anvende §14's godkendte `SQLITE_OPEN_NOFOLLOW`-krav ved den faktiske
  SQLite-open. Bindingens konkrete API-mapping vælges med backendvalget;
  en svagere path-kontrol må ikke bruges som fallback.
- **Actual access mode:** Den faktisk opnåede read-only/read-write
  mode skal kunne observeres fra den konkrete connection; requested
  mode alene er ikke evidens.
- **Connection-bundet databaseevidens:** Backend skal levere de
  connection-bundne filename-/VFS-/movement-observationer, som §14
  kræver, uden at et pathname alene bliver identitetsbevis.
- **DB-object binding:** Backend/VFS/OS-integrationen skal have en
  dokumenterbar og testbar mekanisme til den stærkere binding mellem
  faktisk åbnet databaseobjekt og den betroede filidentitet, som §14
  fortsat lader implementeringsmæssigt åben.
- **WAL/SHM-livscyklus:** Backend skal kunne indgå i §15's kontrollerede
  sidecar-livscyklus uden immutable/nolock-fallback, manuel sidecar-
  reparation eller skjult journal-mode-mutation.
- **Actual-connection settings:** De værdier, som den eksisterende
  `ConnectionStateObservation` validerer, skal kunne observeres fra
  den konkrete work-connection og bindes til samme bounded unit of work.
- **Schema/capability observation:** `user_version`, manifest,
  migrationshistorik/checksums og krævede schema-capabilities skal
  senere kunne verificeres efter §16 og L3 uden at factoryen opfinder
  en permanent admission.
- **Transaction integration:** Backend skal kunne understøtte den
  eksplicitte transaction-kontrakt, som senere godkendes under R4.
  R3-B vælger ikke autocommit-mode, BEGIN-policy eller retry-semantik.
- **Cleanup/resource integration:** Backendens connection-, statement-,
  cursor-, BLOB- og backup-resource-semantik skal kunne indgå i
  R2-B/R2-C's verificerede cleanup- og crash-kontrakt.
- **Introspection failure:** Ukendt, manglende eller ikke-verificerbar
  capability skal være fail-closed. Manglende introspection må ikke
  omskrives til "supported".
- **Ingen global V2-effekt:** Installation eller valg af V3-backend må
  ikke automatisk udskifte eller ændre V2's eksisterende SQLite-binding.

**Manifestets rolle:**
- Capability-manifestet er en policy/kravprofil, ikke runtime-evidens.
- En backend må ikke selv erklære sig compliant uden verificerbar
  mapping fra hvert krævet capability til konkret API/adfærd og tests.
- En capability, som kun findes i en buildvariant, skal bindes til den
  konkrete build/provenance; pakkenavn eller versionsstreng alene er
  utilstrækkelig.
- Factoryens backend-ID, capability-profil og observationer skal kunne
  sammenholdes uden caller-leverede bypass-værdier.
- Et senere backendskift kræver ny capability-review; tidligere
  godkendelse er ikke automatisk portabel mellem bindings/builds.

**Foreslåede acceptance-cases (ikke udført):**
- Stdlib SQLite 3.45.1 på den observerede server:
  ingen normal V3-open gennem den eksisterende release-guard.
- Backend består release-policy, men mangler §14 DB-object binding:
  ingen business-admission.
- Backend understøtter requested read-only, men actual mode kan ikke
  verificeres:
  fail-closed.
- Filename og HAS_MOVED-lignende evidens er tilgængelig, men stærkere
  objektbinding mangler:
  ingen påstand om fuld §14-identitet.
- Connection-settings kan kun leveres som caller-data:
  ingen authoritative actual-connection admission.
- Compile/build-diagnostic er utilgængelig:
  manglende provenance-evidens håndteres efter den senere godkendte
  build-policy, ikke ved at antage standardbuild.
- Backend opfylder R3-capabilities, men den valgte transaction-mode
  bryder R4:
  backend er ikke dermed implementeringsklar.
- Optional backend er ikke installeret:
  ingen silent installation, import-fallback eller stdlib-fallback.
- V3-backend installeres senere:
  V2's account/auth-store fortsætter på sin særskilt godkendte path
  og binding, medmindre en separat V2-beslutning ændrer dette.

**Fortsat åbent:** Den konkrete backendkandidat, capability-ID'er,
manifest-format, build-/source-provenance, OS/VFS-object-binding,
factory-/observer-API og integrationstests. R3-B vælger ingen pakke,
installationsmetode eller runtime-admission. R3 forbliver OPEN;
R1/R2/R4 ændres ikke. D006, §12-§18, V2, deploy og LIVE
forbliver uændrede.

### 5.3 R3-C — Backendkandidater og WAL/VFS-gapanalyse

**Status: PROPOSED_FOR_REVIEW; R3 forbliver OPEN.**
**Reviewdato: 2026-10-24.**

**Grundlag:** Godkendt §14 path-identitet, §15 WAL/SHM-livscyklus,
R3-A factory-binding og R3-B capability-manifest samt officiel
SQLite-/APSW-dokumentation. Dette er dokumentationsbaseret analyse,
ikke installeret-backend-test eller runtime-evidens.

**Aktuel platform:** Aktiv venv blev observeret med Python 3.12.3,
stdlib sqlite3 og SQLite 3.45.1. Sidstnævnte består ikke den
eksisterende WAL-reset release-policy. APSW og pysqlite3 var ikke
installeret ved den afgrænsede inventory-kontrol.

**Kandidatsammenligning:**
- **Stdlib sqlite3:** URI-open kan afgrænse existing-only adgang,
  men den dokumenterede offentlige Python-API eksponerer ikke
  direkte alle de nødvendige §14 C-operationer. Den observerede
  SQLite 3.45.1 afvises desuden af den nuværende release-guard.
  Stdlib-bindingen alene er derfor ikke en kvalificeret løsning
  til den godkendte canonical V3-admission.
- **APSW:** Dokumentationen beskriver sqlite3_open_v2 med eksplicitte
  flags, faktisk read-only-observation, connection-filename,
  file_control og VFS-adgang. Det gør APSW relevant for videre
  undersøgelse af L2-capabilities.
- **APSW default-open:** Standardflags inkluderer READWRITE og
  CREATE. En eventuel V3-factory skal eksplicit fjerne CREATE,
  kræve existing-only og anvende SQLITE_OPEN_NOFOLLOW. Ingen
  almindelig eller implicit fallback er tilladt.
- **HAS_MOVED:** At APSW file_control accepterer en operation
  beviser ikke HAS_MOVED=false. Både operationens succes og
  den konkrete outputværdi kræver godkendt observation.
- **APSW file_control-pointer:** API'en modtager en rå pointer.
  Output-bufferens type og levetid samt operationens return-status
  og faktiske outputværdi skal være verificerbare. Rå pointeradgang
  er ikke i sig selv en sikker identitetsbinding.
- **§14 L4 objektbinding:** Hverken filename, HAS_MOVED=false,
  VFS-navn eller før-/efter-observation af pathname beviser alene
  den faktiske SQLite-fils identitet. Ingen kandidat er på dette
  grundlag kvalificeret til business-admission.
- **§15 sidecar-binding:** APSW's VFS-udvidelsesmuligheder er
  ikke bevis for sammenhæng mellem work-connection og faktiske
  DB/WAL/SHM-objekter eller deres generationer.
- **R2/R4:** Backendens cleanup-, cursor-, statement-,
  transaction-, autocommit- og crash-semantik er fortsat
  særskilte åbne integrationskrav.
- **APSW transaction-context:** `with connection` starter en
  transaction og committer normalt ved afslutning uden exception.
  Indlejrede context managers bruger savepoints. Denne adfærd
  skal vurderes under R4 og er ikke en godkendt L4-policy.
- **APSW close-semantik:** `Connection.close()` lukker også
  udestående cursors, BLOBs og backups; `force=True` ignorerer
  exceptions. Et close-kald alene er ikke verificeret R2-cleanup
  og siger ikke, om en business-transaction blev committed.

**Særlige §15-risici:**
- L1 må ikke åbne og lukke DB/WAL/SHM råt for at skaffe ekstra
  inode-/handle-evidens. Dette kan forstyrre SQLite POSIX-låse.
- Dirfd-relativ no-follow metadataobservation bevares, men er
  ikke alene en racefri connection-/objektbinding.
- Fysisk read-only åbning kan indebære SQLite-styrede WAL/SHM-
  sideeffects. Logisk read-only er ikke identisk med nul
  filsystemændringer.
- Autoriseret sidecar-oprettelse og SHM-genopbygning skal være
  SQLite-styret og verificeret; ingen manuel repair.
- Immutable/nolock, PERSIST_WAL, exclusive locking og ændret
  checkpoint-policy er ikke løsninger godkendt af §15.
- WAL kan indeholde committed data, som endnu ikke er
  checkpointed. Read-admission må ikke ignorere WAL.
- Crash-rester, manglende sidecars og sidste read-only close
  kræver §15-klassifikation, ikke automatisk sletning.
- L4 skal kunne dokumentere sikker read-snapshot-livscyklus,
  ressourceafslutning og relevant efter-close-observation.

**VFS-/OS-integration — mulig, men ikke valgt:**
- En konkret mekanisme skal binde faktiske SQLite-open-handles
  til godkendt filidentitet uden at skabe nye racevinduer.
- Samme løsning skal dokumentere DB/WAL/SHM-relation,
  locking, shared-memory, recovery og sikre close-forløb.
- APSW VFS-arv eller file_control-adgang giver ingen automatisk
  garanti for disse egenskaber.
- Enhver custom VFS/native integration kræver separat review
  af build, OS-semantik, concurrency og failure paths.
- Ingen VFS-implementation, OS-handle-API eller backend vælges her.

**Foreslåede acceptance-scenarier, ikke udført:**
- Manglende CREATE-forbud eller NOFOLLOW: reject.
- Forkert actual access mode eller ukendt HAS_MOVED: reject.
- Samme pathname men udskiftet faktisk DB-objekt: reject.
- Uverificeret DB/WAL/SHM-binding eller sidecar-race: reject.
- Rå close-operation der påvirker SQLite-låse: reject.
- READONLY/WAL med autoriseret SQLite-sidecar-transition:
  kun betinget admission efter fuld §15-validering.
- Samtidige readers/writers, snapshots, graceful close,
  read-only last-close, crash/restart og bevaret WAL:
  kræver isolerede concurrency- og recovery-tests.
- Backendversion eller VFS skifter: tidligere capability-evidens
  kan ikke genbruges uden eksplicit ny godkendelse.

**Foreløbig vurdering:** APSW er en relevant primær
undersøgelseskandidat, ikke en valgt eller godkendt backend.
En separat VFS-/OS-integration kan være nødvendig, men er
endnu ikke specificeret eller sikkerhedsvurderet.

**Fortsat åbent:** Konkret backend/build-provenance,
§14 faktisk OS-object-binding, §15 DB/WAL/SHM-binding,
sikker POSIX-låsehåndtering, R2-resource-lifecycle,
R4-transaktionssemantik og isolerede tests.
R1-R4 forbliver OPEN. Ingen kodeændring, installation,
databaseåbning, V2-ændring, deploy eller LIVE-godkendelse.

## 6. R4 — Bindingens faktiske transaktionskontrakt

**Eksisterende grundlag.** D006 kræver korte transactions, genvalidering af
kritiske checks inde i den beskyttede transaction, `NORMAL` før normale
canonical writes, fuld rollback af write-sættet ved exception før commit og
committed authorization før ekstern I/O. Application-level retry skal følge
D006's bounded policy med ny transaction og genvalidering; ukendt commit følger
§18. §13 placerer transaktionsejerskabet hos L4. [B1, B2]

**Ekstern mekanik.** SQLite's `ABORT` kan annullere kun det fejlende statement,
mens tidligere writes bevares i en aktiv transaction. `ROLLBACK TO` afslutter
ikke den omgivende transaction. `COMMIT` med `SQLITE_BUSY` kan efterlade en aktiv
transaction. Lavniveau-autocommit kan genaktiveres af både commit og rollback;
status alene beviser ikke en bestemt operations udfald. [E6, E9, E10, E11]

Python 3.12 viser, hvorfor bindingstilstand er relevant: Ved `autocommit=True`
er metoderne `commit()`/`rollback()` uden virkning; ved `False` genåbnes en
transaction efter afslutning. `executescript()` under legacy transaction control
committer en pending transaction før scriptet. Disse eksempler vælger ikke en
mode for Aureum. [E7]

I den gennemgåede CPython 3.12-kilde udfører `commit()` under
`AUTOCOMMIT_DISABLED` først `COMMIT` og derpå `BEGIN`, begge med en fejlreturvej.
En fejl i det sidste trin kan derfor forekomme efter en vellykket commit.
Dette er en kildekodeafledning, ikke en observeret fejl på serveren. [E12]

**Tænkt fejlscenarie:** Lifecycle-transition og head opdateres; required outbox-
insert fejler; fejlen opsluges; resttransaktionen committes. Det ville bryde
D006's atomiske lifecycle-/head-/outbox-kontrakt. [B1, E9]

**Foreslået integrationsregel.** Backend og L4 skal have én eksplicit,
versioneret transaktionskontrakt. Faktisk transaction-start, writer-
serialization, barriere-/schemakontrol, mutation, commit/rollback og cleanup må
ikke adskilles af skjulte eller utilsigtede transaktionsskift.

En fejl, der gør unit of work ugyldig, må ikke føre til commit af resttransaktionen.
L4 skal håndtere fuld rollback og dens udfald. Helpers, kontekstmanagere,
savepoints og automatisk transaktionsstyring må ikke omgå L4's grænse.
L2's opsætning skal også kunne etableres korrekt: `foreign_keys` kan ikke
ændres med virkning inde i en aktiv transaction. [E13]

Kendt commit bevares som kendt commit ved senere fejl. Ukendt commit håndteres
efter §18. Et cleanup-resultat eller en generisk exception må ikke alene
autorisere ekstern handling eller gentagelse. SQLite's mulighed for at gentage
et busy COMMIT er ikke automatisk en ændring af Aureums låste retry-policy.

**Foreslåede acceptance-cases:**

| Case | Forventet sikkerhedsegenskab |
| --- | --- |
| Sidste required write fejler efter tidligere writes | Ingen delvis canonical succes; fuld rollback håndteres eksplicit. |
| Bindingens commit-metode er uden virkning i valgt mode | Ingen falsk commit-bekræftelse eller frigivelse af ekstern handling. |
| Helper forsøger implicit commit/transaktionsskift | Den beskyttede operation må ikke opdeles. |
| Busy COMMIT efterlader aktiv transaction | Ingen blind retry eller overset resttransaktion. |
| Commit lykkes; efterfølgende bindingstrin/cleanup fejler | Kendt commit omskrives ikke til `NOT_COMMITTED`. |
| Rollback fejler eller udfaldet er uklart | Ingen fabrikeret rollback-succes. |
| Automatisk transaction forhindrer korrekt setup | Ingen admission med forkert eller ukendt enforcement. |

**Åbne valg:** Transaktionsmode, adapteroperationer, fejlklassifikation og
verifikationsmekanisme for faktisk transaction-state. Ingen specifik Python-
mode, retry-udvidelse eller migrationshelper godkendes her.

## 7. Tværgående afhængigheder og afslutningskriterium

R1 forbinder restore med §18's udfald og D005/D006's eksterne eksponering.
R2 afgrænser hele ressourcelevetiden. R3 binder evidensen til den faktiske
backend. R4 bestemmer, hvordan denne backend bevarer transaktionsgrænserne.

Ressourceafslutning, databaseudfald og ekstern betaling/levering skal holdes
adskilt. Ingen af de fire fund kan lukkes alene ved at ændre dokumentstatus.

Foreslået lukkeprocedure pr. fund: Godkend en afgrænset integrationskontrakt;
vælg mekanisme særskilt; implementér kun efter godkendelse; dokumentér relevante
isolerede integration-/fault-injection-tests og review evidensen. Ingen tests
eller fixtures er oprettet eller kørt som del af dette notat.

R1–R4 er fortsat OPEN. Blueprintet, §14–18 og de eksisterende V3-primitiver
forbliver uændrede. Notatet godkender ikke database-open, migration, provider-
kald, Telegram-send, retention-I/O, serviceændring, deploy, restart eller LIVE.

## 8. Kilder og sporbarhed

### Brugerleveret Aureum-grundlag

[B1] `docs/aureum_v3_blueprint.md` ved ovenstående baseline og SHA-256.
Gennemgåede terminaludtræk omfatter D006.1 backup/restore (2656–2701), D006.4
lifecycle (3729–3769), outbox (3770–3856), AI-authorization/settlement/reconciliation
(3902–4023), generelle transaktionsregler (4121–4160), D006.5 ownership/retry/leases
(4161–4225 og 4265–4350), D006.6 migration/barrier/rollback samt D006.7's
retention-restore-guard. Referencerne gælder de viste uddrag, ikke en påstand om
ny fuldstændig filinspektion.

[B2] `docs/aureum_v3_database_admission_architecture.md` ved ovenstående baseline
og SHA-256. Gennemgået i samtalens udtræk/diffs: §5, §9–13 og §14–18, herunder
§12.2–12.3 composition-root/API, §13 L0–L5, §17 reader-drain og §18 reconciliation.

[B3] Brugerleveret kode fra `opportunity_sqlite_runtime_guard.py`, den fulde
committede `test_opportunity_sqlite_runtime_guard.py` samt statisk grep af
trackede Python-filer. Testkode læst, ikke eksekveret; ingen ny måling af indlæst
SQLite eller production-call paths.

[B4] Brugerens søgeoutput i `Pasted text(20261020-203940).txt`: linje 6–10
angiver mønster og de to søgte dokumenter; linje 20–24 viser fundamentals-lineage;
linje 40–59 viser calibration/policy-epochs. Resultatet er begrænset søgeevidens,
ikke et udtømmende fraværsbevis.

[B5] Supplerende brugerleverede kodeudtræk ved Git-commit
`5f475df346b1256fac80f6d7a41642fb07e8065d`: backup_service.py
(create_platform_backup/create_full_backup), backup_routes.py og app.py's
backupregistrering. Statisk læsning; ingen backup/restore eller driftskontrol.

[B6] Samme commit: aureum_paths.py, linje 20–85, og
opportunity_database_config.py, linje 27–60. Statisk path-kontrakt;
projektmoduler er ikke importeret, og service-environment er ikke aflæst.

### Officielle eksterne kilder

Kilderne er kontrolleret 2026-10-20. De beskriver mekanik, ikke nye Aureum-
beslutninger. Versionssider og kildekodegrene kan ændre sig; den valgte runtime
skal senere bindes til en konkret reviewet build.

[E1] SQLite Backup API, afsnit 1:
https://www.sqlite.org/backup.html

[E2] SQLite — Opening A New Database Connection:
https://www.sqlite.org/c3ref/open.html

[E3] SQLite — Closing A Database Connection:
https://www.sqlite.org/c3ref/close.html

[E4] SQLite — Interrupt A Long-Running Query:
https://www.sqlite.org/c3ref/interrupt.html

[E5] SQLite — How To Corrupt An SQLite Database File, især §2.2 og §2.5:
https://www.sqlite.org/howtocorrupt.html

[E6] SQLite — Transaction, især §2.2, §2.3 og §3:
https://www.sqlite.org/lang_transaction.html

[E7] Python 3.12 sqlite3-dokumentation: runtime-version, commit/rollback,
autocommit og executescript:
https://docs.python.org/3.12/library/sqlite3.html

[E8] SQLite — Run-Time Library Version Numbers:
https://www.sqlite.org/c3ref/libversion.html

[E9] SQLite — The ON CONFLICT Clause, ABORT:
https://www.sqlite.org/lang_conflict.html

[E10] SQLite — Savepoints, ROLLBACK TO:
https://www.sqlite.org/lang_savepoint.html

[E11] SQLite — Test For Auto-Commit Mode:
https://www.sqlite.org/c3ref/get_autocommit.html

[E12] CPython, versionsgren 3.12, `Modules/_sqlite/connection.c`,
`pysqlite_connection_commit_impl` (COMMIT efterfulgt af BEGIN i
AUTOCOMMIT_DISABLED). Grenen er ikke en attestering af serverens konkrete build:
https://raw.githubusercontent.com/python/cpython/3.12/Modules/_sqlite/connection.c

[E13] SQLite PRAGMA foreign_keys:
https://www.sqlite.org/pragma.html#pragma_foreign_keys
