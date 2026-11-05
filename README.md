# Paris Mobility Intelligence

A planned research platform for understanding transport reliability, network connectivity, disruptions, and neighbourhood access in Paris.

**Status: planning and M0 feasibility review. No application, collector, research results, or hosted service has been implemented.**

## Four projects, one map

| Project | Intended outcome | Evidence requirement |
| --- | --- | --- |
| 1. Transport Reliability Index | Explainable line, route, and stop comparisons over time | Separate predictions from confirmed service; publish coverage and uncertainty |
| 2. Public Transport Digital Twin | A network map with current information and closure scenarios | Distinguish reported conditions from modeled effects |
| 8. Disruption Early-Warning System | Incident monitoring, recurrence analysis, and eventually validated warnings | Predictive claims require signals preceding events and chronological evaluation |
| 10. Neighbourhood Mobility Score | Compare access to transport, services, and jobs where defensible | Match geographic vintages; disclose routing assumptions and job-location limits |

**Pilot:** selected metro and bus lines in Paris, chosen after auditing coverage. Surrounding network data may be needed for journeys crossing the study boundary.

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
