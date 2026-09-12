# Aureum V3: database-admission architecture

Status: DRAFT for samlet admission-arkitektur. Målprofilen i afsnit 9.2 og
service-/procesmodellen i afsnit 10.2 er APPROVED_ARCHITECTURE_ONLY; øvrige
åbne valg og deployment er ikke godkendt. D006 forbliver uændret.
Dato: 2026-09-11.
Kodebaseline: `153b45bcaf32dd6c46f2c479c383d100deeea185`.
Autoritativ kilde: `docs/aureum_v3_blueprint.md`, SHA-256
`fc4f6fd2561169d393603eff9badc9e6d9e3e6342d40fbe5cd3eadbe0f27c8da`.

Notatet adskiller eksisterende D006-krav, ekstern dokumentation [S1-S5]
og foreslåede integrationsvalg. Det implementerer eller aktiverer intet.
D006 forbliver autoritativ; nye krav eller afvigelser kræver en eksplicit
beslutning. En godkendt observation er ikke fuld database-admission.

## 1. Eksisterende byggesten og deres grænser

`opportunity_database_config.py` resolver den konfigurerede path.
`opportunity_sqlite_runtime_guard.py` kontrollerer en afgrænset
WAL-reset-release-policy i den kaldende proces, ikke en samlet kontrol af
bibliotekets oprindelse og sikkerhedsrettelser.
`opportunity_database_connection_contract.py` validerer leverede settings og
en eksplicit schema-version-policy. `opportunity_database_permission_contract.py`
validerer leverede permission-modes og flags for bekræftet sidecar-fravær.

De fire moduler beviser ikke tilsammen, at observationerne tilhører samme
faktiske database og connection. De etablerer heller ikke schema-capabilities,
migrationshistorik, migrationsbarriere eller beskyttelse mod path-udskiftning.
De allerede committede moduler ændres ikke som del af dette notat.

## 2. Krav fra den låste D006

D006.1 (2590-2655) kræver separat V3-database, eksplicit absolut override uden
fallback, private DB/WAL/SHM-permissions, WAL samt normale connection-settings.
Initialisering/migration etablerer WAL; normal runtime verificerer den.

D006.5 (4161-4225) kræver afgrænset connection-ejerskab, ingen ubeskyttet
deling, foreign keys, timeout, write-durability og ingen dirty reads.
Correctness-kritiske read-modify-write flows bruger `BEGIN IMMEDIATE`.
Provider-, AI- og delivery-kald samt backoff må ikke ligge i write-transactionen.
Retries er begrænsede; et ukendt commit-resultat kræver reconciliation.

D006.6 (4546-4723) kræver versionerede migrations, eksplicit read/write-
kompatibilitet, capabilities og migrationschecksums. Almindelig runtime må
ikke bootstrappe eller migrere. Normal canonical write skal respektere
`schema_migration_control`: committed `QUIESCED` blokerer normale writers;
`MIGRATING` frigives ikke før gyldig verification og fenced writer-release.
Et manglende control-head må ikke fortolkes som `NORMAL`.

## 3. Foreslået kontrolleret adgangsvej

Adgangslaget ejer hele unit of work: konfiguration, runtime-guard,
filesystem-observation, åbning, connection-opsætning, validering,
transaction og lukning. Observationerne indsamles af laget, ikke af callerens
business-kode. Der returneres ikke et ubundet, permanent `approved=True`.

Foreslået sekvens:

1. Resolver path og adgangstype; kør runtime-guarden før SQLite-åbning.
2. Verificer filesystem-forudsætninger efter en eksplicit platformspolitik.
   Permission denied, I/O-fejl og ukendt tilstand er fejl, ikke fravær.
3. Åbn eksisterende database: `mode=ro` for læsning, `mode=rw` for writes.
   Ingen `mode=rwc`, automatisk fallback, DDL eller permission-reparation.
   URI bygges fra en korrekt escaped path, ikke fra callerens URI-parametre. [S2]
4. Anvend og læs connection-lokale settings tilbage på samme connection.
   `foreign_keys` indstilles før transaction-start; ukendte PRAGMA'er kan
   ignoreres af SQLite, så manglende eller uventet returværdi er fejl. [S3]
5. Valider faktisk schema, migrationshistorik og capabilities på den connection,
   der bruges til arbejdet. Læsekontrol og data bindes til samme snapshot. [S1]
6. For writes: kontroller den aktuelle barriere og kompatibilitet inden for
   write-transactionen, før business-writes. Brug `BEGIN IMMEDIATE` i den
   første fælles write-wrapper; dette er et integrationsforslag, ikke en
   omskrivning af D006s undtagelse for simple immutable inserts.
7. Commit eller rollback efter eksplicit transaction-policy; luk altid connection.
   Pythons `with connection:` lukker ikke connection automatisk. [S5]

Fejl ved opsætning eller validering frigiver aldrig business-adgang.
Cleanup-fejl må ikke skjule primærfejl eller et ukendt commit-resultat.
API'et skal styre tilladte operationer; en wrapper omkring vilkårlig SQL eller
caller-styret `COMMIT`/PRAGMA er ikke i sig selv en sikker adgangsgrænse.

## 4. Read-only er ikke automatisk filsystemmæssigt skrivefrit

Read-only canonical data og nul filsystemændringer er forskellige garantier.
SQLite kan åbne en read-only WAL-database, når sidecars findes og er læsbare,
eller når de kan oprettes. `query_only=ON` er supplerende beskyttelse, ikke
bevis for nul sideeffekter. Åbning, brug og lukning skal derfor testes. [S1, S3]

Foreslag: behold preflights uden SQLite-åbning. Normal read-session kan kun
indføres med en dokumenteret sidecar-livscyklus. Bekræftet fravær i
permission-kontrakten er ikke tilladelse til uobserveret sidecar-oprettelse.
Ingen `immutable=1` eller `nolock=1` som genvej på den aktive database. [S2]
Ingen manuel sletning af aktive sidecars eller tvunget checkpoint som admission-
reparation; D006.5 (4509-4524) behandler checkpointing som maintenance.

## 5. Filesystem-identitet og hardening: implementering udestår

Målprofilen i afsnit 9.2 er godkendt som separat arkitekturbeslutning.
Den fastlægger målkrav til identitet, placering, directories, filer, ACL og
oprettelse, men ikke den konkrete deployment. Identitetsmekanisme,
sidecar-livscyklus, konto-/procesmodel og deploymentplan skal stadig
afgrænses og testes. Målprofilens ekstra regler tilskrives ikke D006.

Den eksisterende permission-kontrakt accepterer også private modes med
owner-execute/special-bits. Det er ikke en production-hardening-godkendelse.
En ny platformspolitik må ikke indføres ved stiltiende at ændre kontrakten.

En observation før/efter åbning er ikke alene bevis mod udskiftning mellem
kontrol og brug. Designet skal afgrænse, hvem der kan ændre path/directories,
og bevise at samme database bruges. Filer kan skifte identitet under restore;
sidecars kan legitimt ændre sig under normal SQLite-drift. Den konkrete
identitetsmekanisme er endnu ikke valgt. Intet `application_id` indføres her.

Observeren må ikke lave rå headerlæsning via separat open/read/close af en
aktiv database i processen: SQLite dokumenterer risiko for POSIX-lock-tab.
Flere navne til samme database kan desuden give journal-/WAL-problemer. [S4]

## 6. Schema og migrationsbarriere

Et korrekt `user_version` alene er utilstrækkeligt. Den fremtidige verifier
skal sammenholde appens eksplicitte manifest med databaseobservationer af
schema, migrations-ID'er/checksums og krævede capabilities (D006.6).
Ingen test-versioner eller opdigtede checksums bliver production-defaults.

For læsning skal kompatibilitet og data ses i samme konsistente transaction.
For write skal barrieren genkontrolleres under writer-serialization; en
connection åbnet før `QUIESCED` får ikke varig skrivetilladelse.
Read-policy under migration, konkrete capability-checks og manifestets format
skal beskrives separat. Ingen automatisk write-to-read-fallback.
Database-admission erstatter ikke bruger-authorization, budget- eller business-gates.

## 7. Testkrav før runtime-godkendelse

Testplanen skal omfatte manglende DB uden oprettelse; observationsfejl uden
falsk fravær; usikre modes/links og path-udskiftning; måling af WAL/SHM-
sideeffekter; forkert DB med korrekt versionsnummer; afvigende migrations-
checksums/capabilities; connection åbnet før committed `QUIESCED`; manglende
control-head; fail-closed ved opsætningsfejl; rollback/lukning og ukendt commit.

Der skal være uafhængige negative tests af den samlede adgangsvej, ikke kun
mockede boolske PASS-værdier. Testdatabaser, runtime-build og isolation skal
godkendes i et senere separat trin. Der køres ingen DB-tests nu.

## 8. Scope og næste trin

Dette notat registrerer målprofilen i afsnit 9.2 som en godkendt, separat
arkitekturbeslutning. Den samlede admission-arkitektur er fortsat DRAFT.
Godkendelsen ændrer ikke D006 eller eksisterende kontraktkode og godkender
ikke en SQLite-build, konkret implementation, integration, initialisering,
migration, deploy eller restart. Dette dokumentationstrin foretager heller
ikke staging, commit eller push.

Målprofilens godkendelsesregistrering er reviewet og gemt. Service-/procesmodellen
i afsnit 10.2 registreres nu som næste separate arkitekturbeslutning. Derefter
kan entrypoint-/service-boundary afgrænses read-only før implementation. De
resterende åbne valg skal stadig afklares før integration og deployment. Den
låste blueprint ændres ikke stiltiende.

## 9. Observeret platform og godkendt målprofil

Status: TARGET_PROFILE_APPROVED_ARCHITECTURE_ONLY.
Brugeren godkendte målprofilen i afsnit 9.2 den 2026-09-11 som en separat
arkitekturbeslutning efter den eksplicitte afgrænsning i samtalen.
Godkendelsesgrundlaget var det gennemgåede DRAFT-notat med SHA-256
`9ba9f5185d2dc1742f6c4afc34989ae1582c90d4f29fa2e16f9088d97a3e3c37`.
Målkravene i tabellen nedenfor er indholdsmæssigt uændrede.
Godkendelsen ændrer ikke D006 og giver ingen tilladelse til at ændre den
kørende server eller aktivere V3. Afgrænsningen i afsnit 9.3 gælder fortsat.

### 9.1 Observeret i brugerens terminaloutput 2026-09-11

`aureum-ai.service` var active/running med MainPID `648351`. Konfigureret
User var root; hovedprocessens real/effective/saved/filesystem UID/GID var
alle 0. Både systemd og processen rapporterede umask `0022`.
`NoNewPrivileges`, `ProtectSystem` og `ProtectHome` var ikke aktiveret.
StateDirectory var ikke konfigureret. De observerede mount-/user-namespaces
var de samme for hovedprocessen og review-processen.

De observerede directories var root-ejede: `/` med `0755`, `/root` med
`0700` og `/root/aureum-ai-platform` med `0755`. ACL-kontrollen blev IKKE
udført, fordi getfacl ikke var tilgængelig. Det beviser ikke ACL-fravær.
Serviceprocessens faktiske V3-path-override blev ikke læst eller resolveret.
Kun repo-defaultens DB/WAL/SHM blev kontrolleret og konstateret fraværende.
Observationen omfatter ikke alle workers, cronjobs eller en fremtidig V3-proces.
PID og metadata er et historisk observationspunkt, ikke permanente guards.

Umask `0022` er ikke en garanti for `0600`: uden default ACL bliver en
oprettelse med requested mode `0666` til `0644`, mens requested `0600`
fortsat bliver `0600`. Det er derfor ikke bevis for forkert mode på nogen
konkret database. Default ACL kan påvirke oprettelsen og skal kontrolleres
særskilt; en mere restriktiv umask erstatter ikke mode-/ACL-verifikation. [S6, S7]

### 9.2 Godkendt målprofil - kun arkitekturbeslutning

| Område | Godkendt målkrav |
| --- | --- |
| Identitet | En fast, dedikeret ikke-root servicekonto. Forventet UID/GID kommer fra betroet deployment-konfiguration, aldrig fra filens ejer eller den interaktive shell. Ingen automatisk root-undtagelse. |
| Dataplacering | En privat, lokal datamappe uden for Git-repoet og `/root`, eksempelvis `/var/lib/aureum-v3/aureum_v3.sqlite3`, valgt gennem eksisterende `AUREUM_V3_DB_PATH`. Eksempelstien er ikke undersøgt eller oprettet. |
| Default-kontrakt | Bevar `state_path("aureum_v3.sqlite3")` og resolverens kode uændret. Ingen stiltiende ændring af default-path eller global `AUREUM_STATE_DIR`, som kan påvirke V2. |
| Directory | Database-directory med præcis `0700`, ejet af den valgte servicekonto. Forfædre skal være betroet ejede og må ikke være skrivbare for ubetroede identiteter via mode eller ACL. |
| DB/WAL/SHM | Eksisterende filer skal være almindelige filer med præcis `0600`, forventet UID/GID og ét hardlink. Ingen execute-/special-bits og ingen symlinks i den valgte path-kæde. |
| ACL | Ingen udvidet access ACL eller default ACL i den private database-directory, og ingen udvidet access ACL på DB/WAL/SHM. Forfædres effektive rettigheder skal kontrolleres. Ukendt/fejlet ACL-observation giver ingen godkendelse. |
| Oprettelse | Umask `0077` fra processtart for alle godkendte processer, der kan oprette runtime-filer. Ingen midlertidig ændring af proces-umask omkring enkeltrequests. Faktiske modes kontrolleres stadig. [S6, S8] |
| Normal adgang | Verificer eller afvis. Ingen automatisk chmod, chown, mkdir, schema-init eller skift til anden database for at få en kontrol til at bestå. |

Denne målprofil er godkendt som en separat platformbeslutning ud over den
rene permission-kontrakt. Den eksisterende kontrakts accept af special-bits
ændres ikke. En særskilt platformspolitik skal senere implementere og teste
den godkendte målprofil; implementation og runtime er ikke godkendt her.

### 9.3 Hvad dette IKKE godkender

Den nuværende root-service er ikke dermed migreret eller godkendt til
målprofilen. Valget mellem en kontrolleret migration af den eksisterende
service og en særskilt V3-proces står åbent. Kontonavn, numeriske UID/GID,
kodeplacering, adgang til eksisterende ressourcer og alle filoprettende
workers/jobs skal indgå i den senere deploymentplan. Vi åbner ikke `/root`
for andre brugere for at omgå denne plan.

Umask og systemd-hardening ændres ikke i denne slice. En ændring af den
eksisterende services umask kan påvirke V2-filer og skal regressionstestes.
NoNewPrivileges er ikke i sig selv fjernelse af eksisterende root-privilegier;
capabilities og serviceadgange kræver særskilt vurdering. [S8, S9]

POSIX-modes er ikke en sikkerhedsgrænse mod fuldt privilegeret root eller
kompromitteret kode under den godkendte ejer. [S9] Pre/post-metadata alene
løser ikke path-races; afsnit 5s identitetskrav og afsnit 4s WAL/SHM-livscyklus
skal stadig bevises. Ingen SQLite-build, ACL-status, faktisk service-path,
read-policy under migration eller samlet database-admission godkendes her.

## 10. V3 service-/procesmodel

Status: V3_SERVICE_PROCESS_MODEL_APPROVED_ARCHITECTURE_ONLY.
Beslutningen afgrænser V3 fra den eksisterende V2-drift; den implementerer,
installerer, starter eller aktiverer ingen ny service.

### 10.1 Observeret beslutningsgrundlag 2026-09-12

Den eksisterende `aureum-ai.service` blev observeret som en aktiv Gunicorn-
webservice under `root`, med `UMask=0022`, `WorkingDirectory=/root/aureum-ai-platform`
og et gthread-setup med én worker og to threads. Service-definitionen bruger
`/etc/aureum-ai.env`; miljøværdier og EnvironmentFile-indhold blev ikke læst.

Den eksisterende V2-drift omfatter desuden root-cronjobs, der starter separate
Python-processer fra samme repo til blandt andet risk/news checks, rapporter,
dashboard-cache, screener-cache og portfolio jobs. Disse jobs blev kun
inventorieret og ikke kørt eller ændret.

Kodeinventaret viste et bredt V2-web-/delivery-scope i `app.py` og relaterede
routes/services. De nuværende V3-databasebyggesten er ikke observeret som en
production-integreret databaseadgangsvej. Default V3 DB/WAL/SHM var fortsat
fraværende ved reviewet.

### 10.2 Godkendt service-/procesmodel - kun arkitekturbeslutning

- V3 skal have en særskilt, dedikeret ikke-root service-/procesgrænse i stedet
  for at migrere den eksisterende `aureum-ai.service` til V3-identiteten.
- Den eksisterende `aureum-ai.service` og den eksisterende root-crontab
  forbliver V2-drift og ændres ikke som følge af denne beslutning.
- Den fremtidige V3-proces skal bruge den godkendte platformmålprofil fra
  afsnit 9.2, herunder dedikeret ikke-root identitet, `UMask=0077`, privat
  dataplacering og eksplicit V3-path-konfiguration, når deployment senere
  godkendes.
- V3 får et smalt, eksplicit entrypoint. Hele `app.py` må ikke bruges som
  implicit V3-entrypoint; genbrug skal ske gennem afgrænsede moduler med
  dokumenterede sideeffekter og dependencies.
- Canonical V3 writers og senere V3 maintenance-jobs må kun flyttes til den
  nye procesmodel gennem særskilt review og deploymentbeslutning. Den
  eksisterende root-crontab er ikke godkendt som canonical V3 writer-path.
- Der er ingen automatisk root-fallback, ingen implicit åbning af `/root` for
  V3-servicekontoen og ingen stiltiende deling af V2-runtimefiler.
- En fremtidig V3-service bliver ikke LIVE eller offentligt eksponeret alene
  ved at eksistere. D004s aktiveringsgrænser og D006s databasekrav gælder
  fortsat uændret.

### 10.3 Hvad denne beslutning IKKE godkender

Beslutningen fastlægger ikke service-navn, kontonavn, numeriske UID/GID,
endelig data-/kodeplacering, konkrete systemd-hardening-direktiver, timers,
jobopdeling, resource-limits, dependency model eller den senere grænse mellem
V2-webreads og V3-data. Den godkender heller ikke installation, `daemon-reload`,
`enable`, `start`, restart, cronændringer, fil-/directory-oprettelse eller
ændringer i `/etc/aureum-ai.env`.

Den godkender ingen SQLite-build, databaseinitialisering, schema-bootstrap,
migration, databaseåbning, canonical write, LIVE-aktivering eller deployment.
D006 og den eksisterende permission-/connection-/runtime-guard-kode ændres ikke
af denne arkitekturbeslutning.

## Kilder

D006-henvisningerne er til den SHA-låste lokale blueprint ovenfor; linjerne
er læst i tidligere verificerede kontraktudtræk. Eksterne kilder er
kontrolleret 2026-09-11 og fastlægger mekanik, ikke nye Aureum-beslutninger.

- [S1] SQLite WAL, afsnit 4-6: https://www.sqlite.org/wal.html
- [S2] SQLite URI, afsnit 3.3: https://www.sqlite.org/uri.html
- [S3] SQLite PRAGMA, introduktion, foreign_keys og query_only: https://www.sqlite.org/pragma.html
- [S4] SQLite corruption hazards, afsnit 2.2, 2.5 og 2.6: https://www.sqlite.org/howtocorrupt.html
- [S5] Python 3.12 sqlite3, connection context manager: https://docs.python.org/3.12/library/sqlite3.html#how-to-use-the-connection-context-manager
- [S6] Linux umask(2), oprettelsesmask og processikkerhed: https://man7.org/linux/man-pages/man2/umask.2.html
- [S7] Linux acl(5), access/default ACL og filoprettelse: https://man7.org/linux/man-pages/man5/acl.5.html
- [S8] systemd.exec(5), UMask, User/Group og NoNewPrivileges: https://man7.org/linux/man-pages/man5/systemd.exec.5.html
- [S9] Linux capabilities(7), DAC-bypass og eksisterende privilegier: https://man7.org/linux/man-pages/man7/capabilities.7.html
