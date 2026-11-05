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
