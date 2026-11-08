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
