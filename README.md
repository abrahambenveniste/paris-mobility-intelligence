# Paris Mobility Intelligence

A research platform for understanding transport reliability, network connectivity, disruptions, and neighbourhood access in Paris.

**Status: first local network explorer implemented for métro 4 and bus 38.** Search 118 boarding points, inspect official route shapes, and request current departure estimates. One coverage point remains unmapped. Disruptions, closure simulation, historical analytics, and hosting are future work.

## Run locally

Requires Python 3.10+ and internet access; no Python packages or database needed. Copy `.env.example` to `.env` and enter your own PRIM credentials. Keep this file private.

```powershell
python prepare_data.py
python app.py
```

Open http://127.0.0.1:8765. Preparation downloads only the two-line reference subset; rerun it when you want updated reference data, then restart the server. Stop the server with Ctrl+C. Predictions are requested only when selecting a point or refreshing, with a two-minute cache.

[Setup, methodology, sources, and limits](docs/network-explorer.md). Run the lightweight offline tests with `python -m unittest discover -s tests -v`.

## Four projects, one map

| Project | Intended outcome | Evidence requirement |
| --- | --- | --- |
| 1. Transport Reliability Index | Explainable line, route, and stop comparisons over time | Separate predictions from confirmed service; publish coverage and uncertainty |
| 2. Public Transport Digital Twin | A network map with current information and closure scenarios | Distinguish reported conditions from modeled effects |
| 8. Disruption Early-Warning System | Incident monitoring, recurrence analysis, and eventually validated warnings | Predictive claims require signals preceding events and chronological evaluation |
| 10. Neighbourhood Mobility Score | Compare access to transport, services, and jobs where defensible | Match geographic vintages; disclose routing assumptions and job-location limits |

**Pilot:** métro 4 and bus 38, selected by the owner after bounded sampling. Include their surrounding termini; this convenience pilot is not representative of the entire network.

**Audience:** researchers and data scientists. **Delivery goal:** local installation and a hosted website. The four modules will be developed sequentially on shared data infrastructure.

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
