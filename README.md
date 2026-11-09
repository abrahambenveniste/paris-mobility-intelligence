# Paris Mobility Intelligence

A research platform for understanding transport reliability, network connectivity, disruptions, and neighbourhood access in Paris.

This is also a documented learning project: follow how public transport data becomes a usable map, why each tool was chosen, and what the results cannot tell us. Technical claims should be understandable and reproducible by someone new to programming.

**Start here:** [beginner walkthrough: data → Python → map](docs/learning-walkthrough.md). For working with an AI assistant, see [questions, prompts, and learning checkpoints](docs/working-and-learning.md).

Development is AI-assisted. The owner defines goals and approves scope; implementation and documentation have been produced with Codex assistance. The walkthrough includes exercises to establish personal understanding; these are not claimed as completed until the owner has done them.

**Status: local explorer for all 16 published Paris métro lines (1–14, 3bis and 7bis).** Search 803 boarding-point records, inspect official route shapes, request departure estimates, and check directly linked traffic notices. Bus 38 has been removed from the active scope. Closure simulation, historical analytics, and hosting are future work.

**Station-first navigation:** search a station name, select it, then choose a métro line. Estimates are grouped by reported destination and ordered by estimated time, with source points and record freshness visible. Châtelet and Les Halles remain separate. [Grouping rules, examples and validation](docs/station-first.md).

[Metro expansion: selection logic, coverage and validation](docs/metro-expansion.md). The inspected snapshot has 801 mapped points listed for real-time coverage, two without a coverage match, and three additional coverage points left unmapped. These are boarding-point records, not unique stations.

For traffic notices, click “Check notices for this line” beside the selected station’s departures. A separate line-level lookup remains below the map. Notices concern the line, not necessarily the selected station. Reports are cached for five minutes. A dashed route indicates a linked active notice, not a full-line closure. [How notices are filtered](docs/traffic-notices.md).

The **Reference coverage** panel follows your line filter and lets you inspect unmatched records. It uses the saved snapshot without additional PRIM calls. [Code, examples and validation](docs/coverage-view.md).

## Run locally

**Configured Windows computer:** double-click `Start Platform.cmd` for the explorer and local collectors, or `Start Explorer.cmd` for the explorer alone. [Quick usage guide and local v0.1 scope](docs/local-release.md). Keep its terminal open while using the tool.

Requires Python 3.10+ and internet access; no Python packages or database needed. Copy `.env.example` to `.env` and enter your own PRIM credentials. Keep this file private.

```powershell
python prepare_data.py
python app.py
```

Open http://127.0.0.1:8765. Preparation discovers published métro lines and downloads their reference subsets; rerun it when you want updated reference data, then restart the server. Stop the server with Ctrl+C. Selecting a station's line requests its covered boarding points; refreshing reuses a two-minute cache where available. Searching alone makes no live request.

[Setup, methodology, sources, and limits](docs/network-explorer.md). Run the lightweight offline tests with `python -m unittest discover -s tests -v`.

## Project 1: collection pilot

A local collector now saves prediction snapshots for two Châtelet / métro-4 points every five minutes while running. Start the explorer, then `Start Collector.cmd`. [Setup, data-quality evidence and scientific limits](docs/reliability-pilot.md). This is not yet a reliability index.

## Disruption Intelligence: notice history

Notices from all 16 métro lines can be archived locally with changed versions preserved. Double-click `Start Platform.cmd` to start the map and both approved local collectors; open [saved notice history](http://127.0.0.1:8765/history) to search saved versions, or use `python disruption_history.py --history`. [Instructions, examples and limits](docs/disruption-history.md). Disappearance from the feed is not treated as incident resolution.

## Four projects, one map

| Project | Intended outcome | Evidence requirement |
| --- | --- | --- |
| 1. Transport Reliability Index | Explainable line, route, and stop comparisons over time | Separate predictions from confirmed service; publish coverage and uncertainty |
| 2. Public Transport Digital Twin | A network map with current information and closure scenarios | Distinguish reported conditions from modeled effects |
| 8. Disruption Early-Warning System | Incident monitoring, recurrence analysis, and eventually validated warnings | Predictive claims require signals preceding events and chronological evaluation |
| 10. Neighbourhood Mobility Score | Compare access to transport, services, and jobs where defensible | Match geographic vintages; disclose routing assumptions and job-location limits |

**Current scope:** all métro routes published in the source, including termini outside Paris. The owner expanded the original métro-4/bus-38 pilot on 6 November 2026. Buses, RER and trams are excluded. Reference coverage does not guarantee continuous real-time availability.

**Audience:** researchers and data scientists. **Delivery goal:** local installation and a hosted website. The four modules will be developed sequentially on shared data infrastructure.

## Public website

The owner has selected a public audience; the application is **not yet hosted**. Disruption collection will remain user-operated on the owner’s computer. [Deployment preparation and source-term findings](docs/public-release.md).

## Read the project

- [Project brief and shared-map concept](docs/project-brief.md)
- [Data sources, access, and remaining gaps](docs/data-sources.md)
- [First bounded data-quality audit and test results](docs/audits/2026-11-05-smoke-audit.md)
- [Research standards](docs/research-standards.md)
- [Roadmap and M0 completion criteria](docs/roadmap.md)
- [Decisions and open questions](docs/decisions.md)
- [Project journal](docs/journal.md)
- [Contributing](CONTRIBUTING.md)

## Reproducibility and licensing

Every published indicator should be traceable to a source version, transformation, method, and observation window. Missing observations must remain visible.

The project is intended to become open source. A repository licence has not yet been selected. Public visibility alone does not grant an open-source licence. External datasets retain their own terms; their redistribution requires a separate review.

Do not commit credentials, raw data, or account screenshots.
