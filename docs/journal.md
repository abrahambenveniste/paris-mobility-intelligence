# Project journal

Use one dated entry per meaningful step. Link evidence and decisions; keep conversational transcripts and credentials out of the repository.

## 2026-11-05 — Planning repository and source review

**Purpose:** establish a usable research-tool direction before implementation.

**Evidence:** owner reported a created PRIM account, saved API credential, and the quotas recorded in [data sources](data-sources.md). Official catalogues/documentation identify candidate transport, geographic, population, and services data. No authenticated transport requests or dataset downloads have been checked.

**Decisions:** preserve the four original projects; use a public repository; target researchers; plan local and hosted delivery. The owner selected a pilot of metro and bus lines in Paris, with lines chosen after the data audit. See [decision log](decisions.md).

**Changes:** created the repository and its brief, source register, research standards, roadmap, decision log, contribution guidance, and secret/data ignore rules.

**Limitations:** ground truth, API field quality, historical availability, static-download access, job geography, and some licence terms remain unresolved. No collector, model, dashboard, or website is implemented.

**Next:** settle the first research workflow, then inspect access and representative data against the [M0 checklist](roadmap.md).

## 2026-11-05 — Reliability direction and readiness

**Decision:** the owner chose a balanced view of passenger waiting experience and timetable punctuality. Components and weights remain to be defined from evidence; 50/50 weighting is not assumed.

**Working preference:** conserve session usage through brief replies, compact documentation commits, and fewer redundant tool calls.

**Evidence and limits:** the existing source inventory remains the baseline. Authentication, representative data downloads, actual-event evidence, cancellations, history, and fine job geography have not been empirically verified. No application or collector has been built.

**Next:** confirm static-data credentials, then check API and static samples before choosing supported reliability measures. Implementation still requires the owner's explicit green light.

## 2026-11-05 — Both credentials obtained

**Evidence:** the owner confirmed possession of API and static-data tokens; no values are recorded here.

**Change:** prepared an ignored local `.env` and published a blank `.env.example` for reproducible setup.

**Next:** the owner fills the local credential file, then access and sample content can be checked. Token validity and dataset quality remain unverified; no application or collector is implemented.

## 2026-11-05 — Credential access verified

**Purpose:** verify the saved credentials without exposing their values.

**Evidence:** both local variables are populated and `.env` is ignored by Git. At approximately 22:28 UTC, GET `https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia/lines?count=1` returned HTTP 200 and one line with the API credential; without it, HTTP 401. GET `https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/offre-horaires-tc-gtfs-idfm/records?limit=1` returned HTTP 200 and one catalogue record with the static credential; without it, HTTP 403. Four one-off requests; no scheduled collector or application created.

**Decision:** access to the two tested endpoints is confirmed. Credentials and response bodies remain outside Git.

**Limit:** catalogue metadata access does not validate the GTFS archive. Next-passage/disruption endpoints, pilot coverage, and field quality remain untested.

**Next:** inspect the coverage reference, GTFS contents, and representative live responses during M0.

## 2026-11-05 — Bounded quality audit and tests

**Purpose and authorisation:** the owner requested data-quality checks and tests before development, while conserving usage.

**Evidence:** ten data-service requests; four single-stop live responses; 119 candidate coverage pairs; an 80 MiB archive prefix; and 31 passing offline structural assertions. See the [dated report](audits/2026-11-05-smoke-audit.md) for counts, timestamps, selection bias, resource bounds, and reproduction details.

**Findings:** no aimed/actual passage times in 12 target-line visits; no exact live-to-GTFS trip-ID matches; one unmatched stop; multiple lines in some responses; source-record ages up to about 14 minutes; projected-coordinate interpretation unresolved. A local encoding issue was corrected before final analysis. The archive remains incomplete and the stop-time sample contains no bus-38 rows.

**Decision:** access and basic structure are usable. These results do not support operational punctuality scores or reliability rankings yet. No application or scheduled collector was built.

**Next:** investigate stop/trip matching, targeted timetable semantics, and actual-event evidence within M0 before approving collection and analytical design.

## 2026-11-05 — Simplicity and explainability

**Decision:** the owner prioritised a simple, effective project they can explain to experts. Keep the four-module vision, but start with one metro line and one bus route and transparent measures.

**Implication:** use the completed checks to distinguish usable schedules/predictions from unproven actual-performance measures. No further network calls or computation were needed for this clarification. Publish the bounded audit and its limits before expanding scope; implementation still awaits approval.

## 2026-11-05 — First local project-2 increment

**Purpose:** turn the inspected pilot into a simple usable network explorer. The owner authorised building project 2, selected métro 4 and bus 38, and chose local-first delivery.

**Evidence:** bounded official reference queries produced two route geometries and 118 boarding points; one of 119 coverage pairs remains unmapped. WGS84 stop coordinates avoid relying on the unresolved projected coverage coordinates. Eleven offline tests passed; JavaScript syntax passed. Browser checks confirmed search, live Cité estimates, and cached refresh without a second live request.

**Decision:** use Python's standard library, plain JavaScript and Leaflet. Fetch estimates on demand with a two-minute cache and persistent rolling request budget. No scheduled collector or database. Keep credentials and generated data outside Git.

**Limit:** boarding-point coverage is not station coverage; estimates are not actual passages. Transfer topology, disruptions, closure simulation and hosting remain unimplemented. Tests establish handling of defined cases, not network-wide source accuracy.

**Next:** owner review of the local interface, then resolve the unmatched stop and specify the next network-analysis increment. See [setup and methods](network-explorer.md).

## 2026-11-05 — Explain the implementation and make learning visible

**Purpose:** the owner requested beginner-friendly code explanations, data samples, basic tool-choice rationales and guidance on asking useful questions.

**Evidence:** reviewed the walkthrough against the implementation and ran `python examples/explain_prediction.py` successfully. The synthetic input produced one expected departure at 12:05 UTC, with zero invalid or past entries. No external requests or credentials were needed.

**Decision:** foreground the learning walkthrough in the README, explain Python, browser JavaScript, map layers, identifier joins and validation, and keep a prompt guide with explicit learning checkpoints. Preserve the technical audit rather than replacing it with promotional claims.

**Limitation:** assistant-generated code and successful assistant-run checks do not establish the owner's independent understanding. Exercises remain uncompleted until the owner attempts them; samples are labelled synthetic, observed or derived.

**Next:** work through one small code example with the owner, ask one understanding question, and document their explanation or changes when completed. No application features were changed in this increment.

## 2026-11-06 — On-demand traffic notices for project 2

**Purpose:** extend the local network explorer with published conditions under the owner's instruction to continue project 2.

**Evidence:** targeted PRIM requests for both lines returned 21 disruption records each. Inspection showed shared-station and other-service notices, so endpoint filtering alone was insufficient. Explicit line links retained zero métro reports and one bus-38 report in that sample. Seven new offline tests and eleven existing tests passed; JavaScript syntax passed.

**Decision:** display only directly linked reports, source status, update time and application periods; show excluded counts and five-minute caching. An active report draws a dashed route with an explicit non-closure legend. Use a separate request budget and no automatic polling. See [method and teaching examples](traffic-notices.md).

**Limitation:** conservative matching omits station-only notices. Reported effects and periods are not measured service loss or incident duration. Redistribution terms remain unresolved, including upstream feed metadata labels; raw samples remain untracked.

**Next:** review the interface and explain the direct-link filter before choosing further network modelling. Implementation and validation were assistant-performed; no owner exercise completion is claimed.

## 2026-11-06 — Métro-only expansion

**Purpose:** the owner explicitly requested all métro lines and removal of buses from the active view.

**Evidence:** the route source uses `Subway`, not numeric `1`. Mode discovery returned 16 routes, including 3B and 7B. Preparation retrieved 803 mapped boarding-point records and 804 coverage pairs: 801 matched, two mapped records lacked coverage, three coverage records lacked map matches. See [per-line results and teaching example](metro-expansion.md).

**Decision:** derive stop/coverage queries and UI choices from published métro routes. Retain readable bis labels, numeric sorting, on-demand requests, local-only delivery and separate caches. Reject an old two-line snapshot at startup rather than silently showing buses.

**Validation:** 22 offline tests and the JavaScript syntax check passed. No raw data or credentials are published.

**Limitation and next action:** reference coverage is not live availability, and boarding points are not unique stations. Inspect the expanded view and investigate the five unmatched records before further modelling. Assistant-performed implementation is distinct from owner-completed learning exercises.

## 2026-11-06 — Reference coverage inspector

**Purpose:** make input gaps visible inside project 2, before using the network for scenarios.

**Evidence:** the existing snapshot yields 803 mapped records, 801 matched coverage records and five mismatches across two directions. Browser checks confirmed global and line-13 totals plus gap details. Two JavaScript tests and 22 Python tests pass. No new PRIM requests were required.

**Decision:** add a line-filtered coverage panel and inspectable names/IDs, using a small pure JavaScript function. Explain association counts and distinguish lookup coverage from operational service. See [teaching notes](coverage-view.md).

**Limitation:** matching references does not prove fresh predictions or normal service. Carrefour Pleyel's differing identifiers remain unresolved; no automatic reconciliation was made.

**Next:** inspect authoritative relationships for unmatched IDs. Code and checks were assistant-performed; owner understanding remains to be demonstrated through the question and exercise.

## 2026-11-06 — Station-first usability

**Purpose:** implement the owner's station-first choice and approval to keep nearby, differently named stations separate.

**Evidence:** the existing 803 records form 327 exact name/commune display groups. Châtelet has ten records across five lines; Les Halles remains separate. Browser checks confirmed search, station/line selection, two empty successful live responses and cached refresh. Four JavaScript tests and 22 Python tests pass.

**Decision:** keep raw identifiers and coverage flags, show per-point estimates after line selection, preserve partial errors, and offer the selected line's traffic notices. Search and station selection alone make no live request.

**Limitation:** display grouping does not prove transfers or identify platform directions. The late-night responses supplied no future estimates; non-empty live rendering was not revalidated in this increment.

**Next:** owner review before choosing further changes. See [method and examples](station-first.md). Owner decisions are recorded separately from assistant-written code and checks.

## 2026-11-08 — Estimates grouped by reported destination

**Purpose:** complete the owner-approved destination-first presentation within the station-first flow.

**Evidence:** two Châtelet / métro-4 responses supplied eight estimates across two destinations. Browser checks confirmed source IDs, older-record warnings, source details and cached refresh. All 22 Python and six JavaScript tests passed; syntax and whitespace checks passed.

**Decision:** group exact reported destinations, sort estimated times, preserve all source observations, and open data-availability details for missing, failed or uncovered responses. No new dependency or background request loop.

**Limitation:** identical predictions do not establish train identity; freshly fetched data may contain old records. No new claim about actual arrivals, cancellations inferred from gaps, or verified platform directions.

**Next:** owner review and explanation of prediction freshness. See [code, labelled samples and validation](station-first.md#destination-grouping--8-november-2026). Implementation and checks were performed with Codex assistance.

## 2026-11-08 — Line notices beside departures

**Purpose:** implement the owner's chosen next step: read selected-line notices without leaving station departures.

**Evidence:** browser inspection of Châtelet / métro 4 showed zero directly linked reports, 21 excluded records, the completeness warning, preserved departures and cached notice reuse. Reselecting the line cleared the previous notice. The bounded check used two upstream departure requests and one traffic request; repeats reused caches. All 28 existing tests and JavaScript syntax checks passed.

**Decision:** share the existing renderer between both notice locations; preserve line-level scope, on-demand loading and five-minute caching. Guard each panel against outdated request results.

**Limitation:** this live check exercised an empty linked-report result, not a fresh populated notice. No claim of normal service or station-specific disruption follows from it.

**Next:** owner review. See [implementation, samples and limits](inline-notices.md). Code and checks are AI-assisted.

## 2026-11-08 — Local explorer v0.1 handoff

**Purpose:** finish a usable version now, as requested by the owner, and defer fine-tuning.

**Evidence:** all 28 offline tests and JavaScript syntax passed. Local HTTP checks served the page, script and 16-line/803-record snapshot. Browser-opening dispatch was checked with a mocked browser; no upstream PRIM calls were needed.

**Decision:** add a Windows double-click launcher, optional browser opening, friendly startup guidance and a concise usage/troubleshooting guide. No new dependency or hosted service.

**Limitation:** this completes the current local explorer scope, not closure simulation or the other research modules. Windows double-click interaction was not separately exercised; existing browser evidence is linked from the guide.

**Next:** owner use of the tool, then later refinements. See [local v0.1 guide](local-release.md). Implementation and checks are AI-assisted.

## 2026-11-08 — Compact responsive explorer

**Purpose:** reduce scrolling on smaller screens while keeping map context beside station information.

**Decision:** CSS makes the map sticky and height-limited; below 850px it uses a compact 180–260px height. Station results shrink to their contents, with a maximum scroll height. Small-screen inputs use 16px text and primary controls have at least 44px height. No data or request logic changed.

**Code:** `.map-panel{position:sticky;top:0}` keeps map context visible while the page scrolls; the small-screen media query changes presentation based on available width.

**Evidence:** browser inspection at 754 CSS pixels reported matching document and scroll widths (no horizontal overflow), a roughly 215px map, and successful Châtelet station/line selection. This is a zoomed desktop check, not physical-phone validation.

**Limitation:** narrower phones and touch gestures still need real-device review. Existing data limitations remain unchanged.

**Next:** owner review through the local link; keep the local server running while using it. Implementation and checks are AI-assisted.

## 2026-11-08 — Project 1 local collection foundation

**Purpose:** begin the owner-approved line-4 reliability project with inspectable history and collection-quality evidence.

**Evidence:** a bounded live cycle saved two successful Châtelet point responses; immediate restart skipped duplication. All 31 tests pass after fixing explicit SQLite connection cleanup on Windows.

**Decision:** use Python's built-in SQLite, five-minute sampling and the existing explorer's request cache/budget. Keep the process user-operated; save normalized responses, reference fingerprints, failures and collection gaps locally. Initial two-point coverage is an implementation pilot, not a claim of whole-line representativeness.

**Limitation:** the existing normalized responses lack stable journey identifiers and discard past entries. No punctuality, actual headway, cancellation-rate or forecast-accuracy claims follow. Background collection was not left running after the one-cycle check.

**Next:** accumulate and inspect data quality, then validate journey identification before prediction-stability analysis. See [pilot instructions and methodology](reliability-pilot.md). Code and validation are AI-assisted.

## 2026-11-09 — Line-4 notice history

**Purpose:** implement the owner's incident-history direction with local line-4 collection.

**Evidence:** one live check saved an empty successful response, zero notice IDs and zero versions; immediate restart skipped duplication. Synthetic tests verified repeated, changed, missing and reappearing notices. All 34 tests pass after correcting search to match message text/IDs rather than JSON field names.

**Decision:** store checks, content versions and sightings in local SQLite; reuse the explorer's targeted traffic endpoint/cache/budget. Provide a launcher, summary and searchable command-line history. Preserve normalized response metadata and distinguish collection time from reported periods.

**Limitation:** no populated live notice was available during validation. Publication history is not an actual incident log; no resolution or duration is inferred. A website timeline remains future work.

**Next:** owner-operated collection and review of actual notice changes. See [instructions and methodology](disruption-history.md). The collector was stopped after the bounded check; implementation and checks are AI-assisted.

## 2026-11-09 — Website notice-history view

**Purpose:** let the owner search and inspect the local archive through the explorer.

**Evidence:** browser checks showed the existing one-empty-check archive accurately, with search and refresh working. All 35 tests pass; a new test verifies filtered history and unchanged database bytes after read-only access. JavaScript syntax passes.

**Decision:** serve a separate `/history` page and read-only local API. Show up to 200 matching content versions, collection-quality counts, reported dates and fingerprints. No upstream calls are triggered by browsing.

**Limitation:** no live populated notices are available yet; populated data/search are tested synthetically. Version sightings are not incident counts, durations or a full chronological event sequence.

**Next:** run the local collector and review actual publication changes. See [history documentation](disruption-history.md). Implementation and validation are AI-assisted.

## 2026-11-09 — All-métro history and integrated launcher

**Purpose:** fulfil the owner's request for disruption history across all lines integrated with the existing map and prediction pilot.

**Evidence:** a bounded run covered 16 lines: 4 checks returned 13 distinct notice IDs, 12 checks were empty, 0 failed; the previous line-4 check was retained. Browser checks verified populated line-6 history, line filter and navigation to the line-6 map (56 mapped records). All 38 tests pass (32 Python, six JavaScript). Some similar notices have separate IDs and some source application periods are about one second; neither is treated as an established incident count or duration.

**Decision:** collect every 30 minutes per line, track each line independently, migrate the old local archive with backup, expose per-line status and link map/history. `Start Platform.cmd` launches the explorer plus both authorised local collectors; it reuses an existing server and stops only children it owns. The owner selected a public audience for a future hosted version.

**Limitation:** tests include synthetic line separation/migration and launcher process ownership; the Windows double-click action was not separately exercised. Only one live all-line observation window exists. Source terms, access credentials, shared quotas, storage and hosting design remain to be resolved before publishing live data.

**Next:** inspect real notice version changes and source-data anomalies; prepare a public hosting feasibility decision. See [methodology](disruption-history.md). Implementation and validation are AI-assisted.

## 2026-11-09 — Public release preparation

**Purpose:** respond to the owner's request to make the tool accessible to everyone.

**Evidence:** GitHub source is already public; the existing app serves only localhost and stores history in local SQLite. PRIM documents Licence Mobilité for its Navitia traffic feed and displays conflicting licence references for the unit arrival API.

**Decision:** the owner selected public website access, with disruption collection only while their computer is on. Prepare a compatible hosted backend and authenticated sync; do not implement scheduled cloud collection by default.

**Limitation:** a managed deployment, sync, complete source terms register, shared quota controls and cost verification are not yet implemented. No public application URL exists. Public GitHub visibility is not a software licence.

**Next:** complete [public-release preparation](public-release.md) and test the working deployment before publishing. This record does not add source data or credentials to Git.

## 2026-11-09 — Hosting secrets preparation

**Purpose:** begin preparing the app for a free public Render deployment, after the owner reported creating their account.

**Evidence:** 34 Python and six JavaScript tests pass. Synthetic tests confirm that named hosted environment secrets override local `.env` values and unrelated environment variables are not imported. No real credentials were displayed or committed.

**Decision:** retain `.env` for local use; accept `PRIM_API_KEY` and `PRIM_STATIC_TOKEN` from the hosting environment. No hosting account configuration or deployment was performed.

**Limitation:** the existing server is local-only; shared quota enforcement, cloud persistence, authenticated synchronization, public-server controls and source terms remain unfinished.

**Next:** prepare and validate those remaining pieces before connecting the repository to Render. See [public-release preparation](public-release.md). Implementation and checks are AI-assisted.

## 2026-11-09 — Local synchronization preview

**Purpose:** prepare the owner's local notice history for a future public website without prematurely uploading data.

**Evidence:** local dry run found 16 saved checks and 13 notice sightings, with no data sent. All 43 tests pass. Synthetic checks covered batching, repeatability, cursor continuation, changed versions, empty/errors and inconsistent records.

**Decision:** generate deterministic batches from a read-only SQLite snapshot and validate the response against stored notice fingerprints. Do not persist a sync cursor or transmit source data until the receiving transaction, access control and licence conditions are ready.

**Limitation:** the owner reported creating a Supabase project; we have not connected to it or created/tested a database schema. The sample UUID is synthetic and no archive identity is yet provisioned.

**Next:** implement and validate the private cloud schema and authenticated synchronization before public deployment. See [hosting preparation](public-release.md). Implementation and testing are AI-assisted.

## 2026-11-09 — Private cloud notice-check table

**Purpose:** prepare a secure destination for local notice history on the way to the owner-requested public website.

**Evidence:** the schema was tested in a rolled-back Supabase transaction with one synthetic empty check; an inconsistent synthetic check was rejected. After creation, SQL checks reported anonymous read/write false, authenticated read/write false, RLS enabled and zero stored checks. No real data was uploaded.

**Decision:** create `pmi_private.notice_checks` with archive/check primary key, status constraints, RLS and no grants to anonymous or authenticated roles. Record the reproducible SQL in GitHub. The owner selected a free Supabase project; no cloud scheduling was enabled.

**Limitation:** privileged database owners can still access the table. No uploader, narrowly scoped database role, public read API, shared API quota or hosted website exists yet; role checks are not a complete security audit. The app still runs locally.

**Next:** implement and verify authenticated atomic synchronization, then a controlled read path and hosted application, subject to applicable source terms. See [public release preparation](public-release.md). Implementation and validation are AI-assisted.

## 2026-11-09 — Private synchronization sender

**Purpose:** prepare secure, retry-safe local-to-cloud uploads while collection stays on the owner's computer.

**Evidence:** 46 offline tests pass. Synthetic fake-connection tests verified batch rollback, matching retries, conflict rejection, verified TLS options and secret-free output. A separate rolled-back SQL experiment in the owner's Supabase project returned true for retry deduplication and identical-content comparison, and false for changed-content comparison. No real notice data was uploaded.

**Decision:** implement a manual sender with transactional batches, a stable archive/check key, full-content conflict checks and verified TLS. Keep the PostgreSQL driver optional and separately pinned. Default to replaying the local archive rather than persisting an unverified checkpoint.

**Limitation:** no writer credential or trusted CA has been provisioned; Python-to-Supabase transfer has not been tested end to end. There is no automatic synchronization, public read API, hosted server or public website. Source terms still need review.

**Next:** provision a narrowly scoped writer connection and verify a bounded synthetic end-to-end upload before real synchronization; then develop the hosted read path and public deployment. See [public-release preparation](public-release.md). Implementation and checks are AI-assisted.

## 2026-11-09 — Public map preview

**Purpose:** provide a shareable first version quickly after the owner approved a clearly labelled map-only preview.

**Evidence:** two anonymous public reference datasets prepared 16 métro lines and 803 boarding-point records. Browser checks confirmed the preview label, map, Châtelet search and five line choices. A focused HTTP test checked public assets and network data, and denied secret, database and live API routes. JavaScript syntax passed.

**Decision:** use a separate read-only preview server and anonymous reference-data build; no PRIM credentials or historical database are exposed. The restricted live-coverage dataset is omitted and not interpreted as zero coverage. Display source and ODbL attribution.

**Limitation:** live arrivals, notices and history are unavailable in this public preview; the full local tool remains separate. A free host may sleep between visits; source snapshots refresh on rebuild.

**Next:** continue the complete hosted backend. See [public-release details](public-release.md). Implementation and checks are AI-assisted.

## 2026-11-09 — Public preview deployed

**Purpose:** make the map accessible to everyone quickly.

**Evidence:** Render built commit `0cc70f9`, reporting 16 lines and 803 boarding-point records. An anonymous request returned HTTP 200; a browser check confirmed the public preview label and Châtelet search.

**Decision:** deploy the read-only preview on the selected free Render service at https://paris-mobility-intelligence.onrender.com. No API credentials or local history were uploaded.

**Limitation:** this is a reference snapshot, not live service. Arrivals, notices and history are not public; the free service may sleep. Deployments from the public Git connection require a manual redeploy.

**Next:** separately complete the secure hosted features and source-term checks. Implementation and checks are AI-assisted.

## 2026-11-09 — On-demand public live data: first increment

**Purpose:** prepare visitor-triggered arrival estimates and line notices, without continuous collection.

**Decision:** reuse the existing response validation and constrain requests to published métro lines and boarding points. Keep the public API disabled until it has a persistent quota budget. No credential is sent to the browser.

**Code:** `budget.get(('traffic', line), lambda: fetch_reports(line, self.key))` reserves or reuses a request through the future budget before calling PRIM.

**Example:** a known line and boarding point can return `{"departures": []}`; this means the response contained no usable estimates, not that service stopped. An unknown point is rejected before any upstream request.

**Evidence:** three focused offline tests passed, covering the existing public map, invalid identifiers, disabled configuration and suppression of sensitive upstream error details. All test responses and credentials were synthetic.

**Limitations:** public endpoints are not connected to the running server or user interface. Persistent quota accounting, shared use with local collectors, public data terms and end-to-end hosting configuration remain unresolved. The derived stop reference does not establish real-time coverage.

**Next:** implement a restart-safe shared quota and cache, check the terms for the two feeds, connect the buttons and verify the deployment. Implementation and tests are AI-assisted.

## 2026-11-09 — Public live-data controls

**Purpose:** prepare a low-traffic public demo with a button per request and no background polling.

**Decision:** select one boarding point for an arrival lookup; use an atomic PostgreSQL reservation before a provider call, a 100-call rolling 24-hour cap per endpoint, one reservation per second across both endpoints, and short in-memory response caches. The budget is separate from the local collectors; their use and any other clients still count against the same PRIM account. Reserve sufficient headroom and monitor the account quota.

**Code:** `SELECT pg_advisory_xact_lock(%s)` serializes budget reservations so simultaneous requests cannot both take the last slot. The reservation is recorded before the API call, including when that call later fails.

**Synthetic example:** requesting an invalid boarding point makes zero PRIM calls; repeating a successful line lookup within five minutes can reuse the response. Five focused offline tests pass, including quota exhaustion and database failure. JavaScript syntax passes. No real database or upstream call was used for these tests.

**Limitations:** the new PostgreSQL table and live website are not configured or deployed; database permissions, concurrent transactions and Render integration have not been tested end to end. The budget controls this public service only, not local or other PRIM clients. The stop-to-monitoring-reference conversion does not establish real-time coverage. PRIM's unit-arrivals catalogue labels its licence both Licence Mobilité and ODbL; clarify applicable terms before public release. The Navitia line reports catalogue identifies Licence Mobilité. The public website remains map-only.

**Next:** resolve feed terms, provision a restricted database role and verified TLS, validate real database budget behavior, configure the hosting secrets, then test and deploy the buttons. Implementation and tests are AI-assisted.

## 2026-11-09 — Quota table provisioned

**Purpose:** prepare restart-safe limits for the requested public on-demand information.

**Evidence:** the Supabase SQL editor reported success when running `cloud/002_public_request_budget.sql`. The migration creates a private reservation table with row-level security and revokes public, anonymous and authenticated access.

**Decision:** store only request kind and reservation time, not source responses or API credentials. No background polling was added.

**Limitation:** no restricted application role or hosted connection has been verified. Table creation alone does not show that the Python budget works with real PostgreSQL, and does not account for calls from local collectors. The public live buttons are still disabled.

**Next:** provision and test a restricted database connection, resolve the published licence discrepancy and verify public hosting end to end. Implementation is AI-assisted.

## 2026-11-09 — Restricted quota connection verified

**Purpose:** connect the planned public buttons to a durable quota counter without granting access to archived notices.

**Evidence:** a restricted PostgreSQL login connected to the Supabase transaction pooler using the provider's downloaded CA and `verify-full`. Permission checks returned quota-table access true and notice-history read access false. A synthetic request successfully reserved a slot in the real database; its repeat used the in-process cache. No real notice data was transferred. Five focused offline tests also passed.

**Decision:** use a separate least-privilege role, row-level security policy for that role and Supabase's published certificate. No API or database passwords are committed.

**Limitation:** the public deployment and actual provider calls still need verification. The public and local collectors have separate counters and share the PRIM account. The arrivals catalogue contains conflicting licence labels; the publisher's broader [licensing guidance](https://prim.iledefrance-mobilites.fr/fr/licences) and [open-data FAQ](https://data.iledefrance-mobilites.fr/pages/contact/) identify Licence Mobilité for API data. The source-specific discrepancy remains documented.

**Next:** configure hosting secrets, deploy and verify the public site with bounded on-demand requests. Implementation and tests are AI-assisted.

## 2026-11-09 — On-demand public data deployed

**Purpose:** let a visitor inspect real-time information from the map, without running a continuous cloud collector.

**Evidence:** the public website returned a live-enabled status. A browser check selected Châtelet, line 4, and one boarding point; the arrivals button returned four estimated departures. The notices button returned no directly linked line notices. Both outputs included the request time and limitations.

**Decision:** enable the existing free Render service with a server-only PRIM key and restricted database connection. Keep request reservations in Supabase; serve cached successful responses for two minutes for arrivals and five for notices. Display the two results separately.

**Limitation:** a single successful request does not prove full network coverage or future availability. Local and hosted clients have separate budgets while sharing the PRIM account. Free Render sleeps after inactivity; the user's computer controls local historical collection. The PRIM unit-arrival catalogue's conflicting licence labels are documented in [public release](public-release.md).

**Next:** monitor provider quotas and source terms; improve historical research features separately. Implementation and verification are AI-assisted.

## 2026-11-09 — Show destinations instead of internal point IDs

**Purpose:** make the public station view understandable to passengers without claiming unverified platform names.

**Evidence:** our earlier line-4 Châtelet inspection returned different reported destinations for the two source points. The current reference snapshot has at most three points per station/line group. An ID identifies a source record, not necessarily a named platform or a permanent direction.

**Decision:** one click queries the station/line source points sequentially, then groups estimates by the destinations actually reported in each response. A short delay respects the public service's request throttle. IDs and per-point timestamps remain under source details. Failed points remain visible, and estimates are not deduplicated into trains.

**Limitation:** one click uses up to one API request per source point; cached responses may use fewer. Empty or partial responses do not prove a direction has no service. Destination labels are not verified physical platform names and may change.

**Validation:** the deployed public Châtelet line-4 view returned estimates under “Towards Bagneux - Lucie Aubrac” and “Towards Porte de Clignancourt” after checking two source points. Five focused offline Python tests and JavaScript syntax passed. This is one observation, not proof of coverage for every station.

**Next:** monitor quota use and partial-response handling. Implementation and checks are AI-assisted.

## 2026-11-09 — Alternative route feasibility

**Purpose:** investigate routing around reported métro incidents with a small number of requests.

**Evidence:** a normal Châtelet → Bastille request returned line 1; explicitly excluding line 1 produced alternatives using other métro lines. A separate future line-6 interruption test returned the same walking-plus-métro route in scheduled and realtime modes. The sampled public-transport sections reported `base_schedule`. See [the routing pilot](audits/2026-11-09-routing-pilot.md) for inputs, responses and limits.

**Decision:** use the PRIM journey planner as a candidate rather than infer routes from map geometry. Metro and walking were included in this test; no bus mode was requested. An excluded whole line is an explicit user scenario, not proof the line is closed.

**Limitation:** the sample does not establish that PRIM's planner incorporated the future closure. No public route planner, automated closure detection or live-routing guarantee was built. Data and availability can change.

**Next:** verify additional known disruption cases and design a bounded public interface with shared quotas and clear freshness labels. Investigation and documentation are AI-assisted.
