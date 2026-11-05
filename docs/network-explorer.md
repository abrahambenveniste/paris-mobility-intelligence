# Local network explorer

> Scope update, 6 November 2026: the app now covers all 16 published métro lines and excludes buses. See [current selection, coverage and tests](metro-expansion.md). The two-line counts and examples below document the earlier implementation; they are historical, not current coverage. Traffic uses a line selector; the original two-line query has been replaced by mode-based discovery.


## Purpose and scope

Project 2 begins with an inspectable map of métro 4 and bus 38. Search or select a boarding point, inspect its identifier, and request provider estimates. This is the first network-view increment, not a validated simulation of transport operations.

Update, 6 November 2026: [on-demand traffic notices](traffic-notices.md) now accompany the map. The initial eleven tests described below are supplemented by seven traffic tests, for eighteen total.

## Data and transformations

| Input | Use | Validation |
| --- | --- | --- |
| IDFM `arrets-lignes` | Boarding-point names, line membership and WGS84 coordinates | Exact line/stop IDs; coordinate bounds; duplicate rejection |
| IDFM `traces-des-lignes-de-transport-en-commun-idfm` | Published route geometry | Both pilot routes present; line geometry and coordinates checked |
| IDFM `perimetre-des-donnees-tr-disponibles-plateforme-idfm` | Real-time coverage | Exact line and monitoring-reference matching |
| PRIM stop-monitoring | On-demand SIRI predictions | Delivery status, target-line filtering, timezone-aware timestamps |

Static sources are queried through the [IDFM catalogue](https://data.iledefrance-mobilites.fr/). `prepare_data.py` records dataset IDs, query URLs, retrieval timestamps, counts and page hashes in local `data/pilot-network.json`. Retrieval time is not publisher update time. Queries use C01374 (métro 4) and C01083 (bus 38), not ambiguous line names.

The inspected snapshot contains 118 mapped boarding points and 119 coverage pairs. Coverage point 483279 has no matching boarding-point coordinate record and remains explicitly omitted. Boarding points are directional/platform records, not unique stations. Published route geometry can contain branches and does not establish ordered trips or transfer topology.

For live data, use `ExpectedDepartureTime`, falling back to `ExpectedArrivalTime` with the correct label. Exclude invalid timestamps and expired non-cancelled predictions; expose exclusion counts in the local response. Deduplicate only explicit identical item IDs. Preserve explicit cancellation status, but never infer cancellation from absence. Distinct records can legitimately show similar times.

Show record age separately from request time. The two-minute “older record” threshold is a display heuristic, not an accuracy guarantee. Estimated times and countdowns are not observed passages; countdowns update on refresh. No punctuality or reliability score is computed.

## Setup and operation

1. Install Python 3.10+; no additional Python dependencies.
2. Copy `.env.example` to `.env`; enter `PRIM_API_KEY` and `PRIM_STATIC_TOKEN` locally.
3. Run `python prepare_data.py` (five bounded catalogue requests for the inspected snapshot).
4. Run `python app.py` and open http://127.0.0.1:8765. An alternative port can be supplied with `--port`.
5. Select a boarding point or use Refresh. Stop with Ctrl+C.

The server binds only to loopback and serves an explicit file allowlist. Credentials stay server-side. No scheduled polling, database, account system, or live-data archive is implemented. Run one server instance: the persistent rolling budget is not designed for concurrent processes.

Responses are cached per line/point for 120 seconds. A local rolling limit of 900 outgoing requests per 24 hours leaves headroom under the owner's reported 1,000/day quota; failed requests count. Other clients sharing the key are outside this budget. API failures produce an error, not fabricated empty service. The budget is stored in ignored `artifacts/`; reference data in ignored `data/`.

Leaflet 1.9.4 loads from jsDelivr with integrity checks. Basemap tiles come directly from OpenStreetMap with attribution and normal browser caching; internet access is required. See [Leaflet installation](https://leafletjs.com/download.html) and [OSM tile policy](https://operations.osmfoundation.org/policies/tiles/). No bulk tile download or geolocation is used. Hosting requires a separate operational review.

## Evidence and limits

Eleven lightweight offline tests cover timestamps, line filtering, explicit cancellations, duplicate handling, coordinate rejection, missing joins, caching, persistent budget enforcement, failed calls, and HTTP credential/file isolation. Run `python -m unittest discover -s tests -v`. Optional JavaScript syntax check: `node --check web/app.js`.

Browser verification confirmed search, selection, a live Cité response, and cached refresh without another API call. This does not validate all stops or prove prediction accuracy. The earlier [bounded audit](audits/2026-11-05-smoke-audit.md) remains relevant to actual-event and trip-matching limitations.

Raw inputs and generated data are excluded from Git. Source dataset terms and software licensing remain separate; do not redistribute the local snapshot before completing the licence register. Route geometry is published under ODbL; retain IDFM and OSM attribution. A public repository is not itself an open-source licence.

Next: review the local experience, resolve the unmapped identifier, then define the next network analysis before adding simulation or additional infrastructure.
