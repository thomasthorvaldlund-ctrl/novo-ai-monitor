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
