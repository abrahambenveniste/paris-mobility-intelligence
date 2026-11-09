# Decisions and open questions

Updated: 2026-11-09. Status distinguishes user decisions from proposals.

## Accepted

| ID | Decision | Reason / implication |
| --- | --- | --- |
| D001 | Public repository; research audience; local and hosted delivery | Methods and installation must be inspectable and reproducible |
| D002 | Original projects 1, 2, 8, and 10 | The digital twin remains in scope; arrival analysis supports reliability |
| D003 | Data quality is the first priority | Restrict claims and coverage to what the evidence supports |
| D004 | Implementation requires explicit green light | Original planning restriction; project 2 authorised under D013 |
| D005 | Develop the four modules one at a time | Reuse a common foundation and learn from each module |
| D006 | Pilot selected metro and bus lines in Paris | Select actual lines after the coverage audit; allow surrounding data to avoid boundary bias |
| D007 | Ask one unresolved question at a time | Explain choices and give the owner time to decide |
| D008 | Concise, detailed documentation at every step | Record purpose, evidence, decision, limitation, and next action |
| D009 | Reliability balances passenger waiting experience and timetable punctuality | Publish both dimensions; exact measures and weights await the data audit. Balanced does not automatically mean a 50/50 score |
| D010 | Conserve session usage | Keep replies brief, batch routine work, avoid repeated research and unnecessary tools, and document meaningful progress in compact commits |
| D011 | Run a bounded M0 data-quality audit and tests, documenting results | Owner explicitly authorised checks; application/collector development remains gated. Use limited samples, no continuous polling, and explicit coverage limits |
| D012 | Keep the project simple, useful, and explainable to experts | Start with understandable measures for one metro line and one bus route. Add complexity only to answer a defined question; the four-module vision remains the longer-term scope |
| D013 | Build project 2 first, using métro 4 and bus 38; local first | Explicit owner approval and two answered scope questions. First increment: reference network and on-demand predictions; no hosting or scheduled collection |
| D014 | Initial implementation: Python standard library, plain browser JavaScript, Leaflet | Implementation choice to minimise setup and make transformations inspectable. No database or framework needed for this increment |
| D015 | Make learning and explainability visible throughout the project | Owner requested beginner explanations, code and data examples, basic design rationales, and useful prompts. Document assisted development honestly; demonstrate understanding through owner-completed exercises and explanations |
| D016 | Next project-2 increment: on-demand directly linked traffic notices | Implementation choice under the owner's instruction to continue project 2. Use targeted line reports; exclude station-only associations from line status. No project-8 predictive model or background collection |
| D017 | Expand project 2 to all published métro lines; exclude buses | Explicit owner request on 6 November 2026, superseding the two-line scope in D006/D013. Discover métro routes by source mode, preserve on-demand calls and document coverage gaps |
| D018 | Expose reference matches and gaps per line before modelling closures | Implementation choice under continued project-2 authorisation. Use the saved snapshot; separate missing coverage from missing map matches. Counts are not reliability or service-availability scores |
| D019 | Prioritise station-first usability; keep differently named nearby stations separate | Explicit owner choices. Group identical source name/commune pairs for display, then choose a line and show source-point estimates. Do not infer transfers or directions |
| D020 | Group estimates by reported destination after station/line selection | Owner accepted the recommended usability increment. Preserve every source observation, sort by estimated timestamp, retain freshness and expose unsuccessful or empty point responses. No inferred direction or train identity |
| D021 | Show selected-line notices beside departure estimates | Explicit owner choice. Reuse the existing line report endpoint and five-minute cache; retain on-demand loading, line-level labels and independent departure results |
| D022 | Finish the current local explorer as v0.1; defer fine-tuning | Owner prioritised a usable tool and conserving usage. Add simple startup and handoff documentation; hosting, simulation and other modules remain separate |
| D023 | Improve small-screen usability and provide a working local link | Owner approved responsive layout work. Keep the map compact and visible, reduce empty list space and enlarge touch controls; no hosting implied |
| D024 | Begin project 1 on line 4, collecting only while the owner runs it locally | Explicit owner approval. Initial implementation samples two already-inspected Châtelet points every five minutes; this is not whole-line coverage. Save collection failures and gaps separately; scoring awaits suitable evidence |
| D025 | Begin Disruption Intelligence with local line-4 notice history | Owner chose history, line 4 and user-operated collection. Preserve versions and collection checks; no inferred incident boundaries or predictive claims |
| D026 | Add a read-only website view of line-4 notice history | Implementation under the owner’s instruction to continue. Search local versions and display collection quality without PRIM requests or inferred incident boundaries |
| D027 | Expand local disruption history to all published métro lines and integrate map navigation | Owner explicitly requested all lines and a combined tool. Use a 30-minute per-line interval, preserve line-4 history and show collection quality; local-only collection remains user-operated |
| D028 | Public audience for a future hosted version | Owner explicitly selected public access. Hosted infrastructure, data terms, secrets and operating costs must be addressed before a functional release |
| D029 | Public website, but disruption collection runs only while the owner’s computer is on | Explicit owner answer. A future hosted interface may show the most recently synchronized history and its gaps; no cloud-side scheduled collector |
| D030 | Prepare a private Supabase table for synchronized notice checks | Owner asked to continue toward a public tool. Use a private schema, restricted grants, RLS and an archive/check identity; public access and upload remain separate implementation steps |
| D031 | Publish a map-only public preview first | Owner explicitly selected an early preview; label live arrivals, traffic notices and history unavailable until the complete hosted backend is ready. Keep the local full explorer and collectors unchanged |
| D032 | Add public on-demand arrivals and line notices | Owner authorised implementation for a low-traffic demo. Keep local collection user-operated; no background cloud polling. Require safe quota accounting and review public data terms before enabling |
| D033 | Test on-demand alternatives for a reported métro disruption | Owner approved a bounded routing feasibility pilot. Inspect provider responses before deciding on a public interface; distinguish a manually avoided line from an automatically detected closed segment |
| D034 | Add a public métro-and-walking journey interface | Owner approved an origin, destination and optional line-to-avoid interface. Use PRIM's planner; do not claim automatic incident avoidance or guaranteed service |

## Proposed

| ID | Proposal | Decision needed |
| --- | --- | --- |
| P001 | One website with a persistent map and four analytical views | Confirm workflows and interaction details during specification |
| P002 | Collect arrivals and disruption reports from the shared foundation stage | Access, terms, operating budget, and explicit collection approval |
| P003 | Network twin starts with published state and closure/accessibility scenarios | Scope of simulation and validation |
| P004 | Disruption monitoring precedes predictive warnings | Target definition and historical evidence |
| P005 | English documentation initially | Final documentation and interface language |
| P006 | Technology chosen after M0 evidence | Earlier stack suggestions are candidates, not commitments |

## Next decisions, addressed individually

1. Review the traffic-notice increment; define any closure scenario before implementing simulation.
2. Study periods and representativeness for subsequent research; pilot lines are selected.
3. Always-on collection location, budget, time availability, and maintenance.
4. Geographic unit and destination categories for accessibility.
5. Reliability components, cancellation evidence, score weights, and ranking rules.
6. Simulation scope and disruption prediction target.
7. Interface language, exports, accessibility, and API users.
8. Software/documentation licence and source-data publication policy.

Record new decisions here with their evidence. Do not silently replace a selected project or treat an unverified source description as observed data.
