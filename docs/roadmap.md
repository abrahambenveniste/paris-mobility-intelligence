# Roadmap

Scope update, 6 November 2026: project 2 now covers all published métro lines; buses are excluded. The [métro expansion](metro-expansion.md) supersedes the two-line scope mentioned in earlier milestones. Network modelling and closure scenarios remain future work.

Updated: 2026-11-05. Project 2 now comes first, explicitly authorised for local delivery. The original stage table below describes the broader backlog; its former reliability-first sequence is superseded by D013.

**Delivered increment:** [local network explorer](network-explorer.md), métro 4 and bus 38, official geometries and on-demand estimates. Connected transfer topology, disruptions and closure scenarios remain future project-2 work. Full M0 readiness is module-specific: the map can proceed while reliability evidence remains incomplete.

| Stage | Deliverable | Completion evidence |
| --- | --- | --- |
| M0: specification and feasibility | Scope, source/access audit, pilot coverage, methods, cost and architecture proposal | Explicit findings and unresolved risks; user green light before implementation |
| M1: shared data foundation | Minimal ingestion, history, provenance, identifiers, validation, monitoring | Successful sample collection and documented quality/retention behavior |
| M2: project 1, reliability | Supported indicators, historical views, first shared map | Transparent definitions, uncertainty, coverage rules, reproducible examples |
| M3: project 2, digital twin | Connected network model, live overlays, closure scenarios | Inspected topology and transfers; scenarios clearly labelled and checked |
| M4: project 8, disruptions | Monitor, event history, recurrence analysis; warnings only if justified | Event semantics documented; predictive claims pass chronological evaluation |
| M5: project 10, mobility | Neighbourhood access measures and geographic comparisons | Defensible opportunities, origins, routing, vintages, and sensitivity analysis |
| M6: integrated release | Hosted website, local setup, API/exports, complete research documentation | Another user can reproduce the example and understand the limits |

After collection is approved, archive arrival and disruption streams during M1 so later modules can use accumulated history. Module development remains sequential. This does not authorise collection now.

## M0 checklist

- [x] Agree that reliability balances waiting experience and timetable punctuality; precise measures and weights remain open.
- [x] Confirm the original four projects and research audience.
- [x] Confirm public GitHub and local plus hosted delivery.
- [x] Create the planning repository.
- [x] Choose a Paris pilot with selected metro and bus lines.
- [x] Record owner-reported API account quotas.
- [x] Identify primary sources and document preliminary evidence gaps.
- [ ] Clarify the first research use case and pilot selection criteria.
- [x] Verify API authentication and restricted static-catalogue access; full GTFS download and real-time endpoint checks remain pending.
- [x] Inspect a bounded convenience sample of GTFS, coverage, and live data; [31 structural assertions passed](audits/2026-11-05-smoke-audit.md). Representative pilot and longitudinal validation remain open.
- [ ] Build a coverage/identifier/freshness assessment from evidence.
- [ ] Establish which actual-event and cancellation fields are usable.
- [ ] Investigate available histories and disruption time semantics.
- [ ] Resolve dataset licences, retention, attribution, and redistribution.
- [ ] Decide uptime, budget, collection cadence, storage, and operating responsibilities.
- [ ] Define initial metrics, validation criteria, and architecture.
- [x] Obtain explicit approval to implement the proposed pilot: project 2, métro 4 and bus 38, local first.

## Documentation at each step

Current readiness: the local project-2 explorer is implemented and tested. Full reliability calculations remain conditional on usable event evidence. Actual arrivals, cancellation completeness, historical availability, fine job locations, and accessibility coverage remain unresolved. Scheduled collection and hosting are not yet approved.

Record purpose → evidence → decision → limitation → next action. Keep a short journal entry with links to the relevant change. Use commit history for exact edits and decision records for why choices were made.

Avoid speculative completion dates. Engineering progress and the time required to accumulate representative observations are different constraints.
