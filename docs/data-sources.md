# Data sources and access

Reviewed: 2026-11-05. This is a documented-source inventory, not a completed empirical data audit.

**Evidence labels:** documented = described by a primary publisher; account-reported = quota/account information supplied by the project owner; empirically checked = successfully retrieved and inspected by this project. Access checks and a [bounded GTFS/coverage/live audit](audits/2026-11-05-smoke-audit.md) are complete. Full-feed and longitudinal validation remain outstanding. The audit found unresolved trip matching, an unmatched stop, source-record age variation, and no actual/aimed times in its target live sample.

## Transport sources

**Current application inputs (6 November 2026):** `arrets-lignes` for stop/line associations; `traces-des-lignes-de-transport-en-commun-idfm` for GTFS-derived geometry; the coverage reference below; individual stop-monitoring predictions; and targeted [Messages Info Trafic v2 line reports](https://prim.iledefrance-mobilites.fr/fr/aide-et-contact/documentation/prise-en-main-des-api/api-information-trafic-travaux/api-calculateur-ile-de-france-mobilites-messages-info-trafic-v2). These were retrieved and inspected. Full GTFS and regional bulk disruptions remain broader research sources, not runtime inputs. See [traffic source selection and matching limits](traffic-notices.md).

| Input | Primary source | Intended use | Remaining check |
| --- | --- | --- | --- |
| Planned service | [IDFM GTFS Datahub](https://prim.iledefrance-mobilites.fr/jeux-de-donnees/offre-horaires-tc-gtfs-idfm) | Routes, stops, trips, schedules, transfer inputs | Download; inspect calendars, shapes, frequencies, identifiers, completeness |
| Arrival predictions | [PRIM global](https://prim.iledefrance-mobilites.fr/fr/apis/idfm-ivtr-requete_globale), [individual](https://prim.iledefrance-mobilites.fr/fr/apis/idfm-ivtr-requete_unitaire) | Live information and supported reliability signals | Token access, field population, freshness, event identity, GTFS joins, actual-event fields |
| Real-time coverage | [PRIM coverage reference](https://prim.iledefrance-mobilites.fr/fr/jeux-de-donnees/perimetre-des-donnees-tr-disponibles-plateforme-idfm) | Stop/line coverage matrix and pilot selection | Listed coverage versus observed continuity |
| Network references | [Stops](https://prim.iledefrance-mobilites.fr/fr/jeux-de-donnees/arrets), [object relations](https://prim.iledefrance-mobilites.fr/fr/jeux-de-donnees/relations), [lines](https://prim.iledefrance-mobilites.fr/fr/jeux-de-donnees/referentiel-des-lignes) | Shared network model and identifier crosswalk | Platforms, directions, transfers, validity periods, unmatched objects |
| Disruption reports | [PRIM global disruption feed](https://prim.iledefrance-mobilites.fr/jeux-de-donnees/idfm-disruptions_bulk), [schema mapping](https://prim.iledefrance-mobilites.fr/fr/aide-et-contact/documentation/prise-en-main-des-api/api-information-trafic-travaux/api-messages-info-trafic-requete-globale) | Incident monitor and longitudinal message archive | Access, update semantics, affected objects, completeness, available history |

The GTFS publisher describes a rolling 30-day offer and three daily refreshes. Archive relevant versions after collection is authorised; today's download is not a historical timetable archive.

PRIM's [next-passage precautions](https://prim.iledefrance-mobilites.fr/fr/aide-et-contact/documentation/prise-en-main-des-api/prise-en-main-des-api-prochains-passages/focus-sur-les-requetes-globale-et-unitaire) explain that planned times may be returned before a journey begins. Inspect status and timestamp semantics before interpreting a field as real time. A disappearing prediction establishes neither arrival nor cancellation.

## Geographic and opportunity data

| Input | Primary source | Documented resolution/vintage | Remaining check |
| --- | --- | --- | --- |
| Neighbourhood boundaries | [IGN/INSEE Contours IRIS](https://www.data.gouv.fr/datasets/contours-iris-r-2), [IGN catalogue](https://cartes.gouv.fr/rechercher-une-donnee/dataset/IGNF_CONTOURS-IRIS) | IRIS boundaries; choose an edition matching the statistics | Geometry, IDs, coordinate reference system, boundary changes |
| Population | [INSEE population 2023 at IRIS](https://www.insee.fr/fr/statistiques/9054332) | 2023 reference data, 2025 geography | Download and validate weights, spatial distribution, joins |
| Services | [INSEE BPE 2025, geolocated facilities](https://www.insee.fr/fr/statistiques/8217525) | Facilities with coordinates; 2025 geography | Selected categories, missing/anonymised coordinates, current release |
| Workplace jobs | [INSEE employment at workplace 2023](https://www.insee.fr/fr/statistiques/9004561) | Communes and Paris municipal arrondissements; 2026 geography | Fine destination geography unresolved; allocation would require assumptions |
| Walking links | [OpenStreetMap pedestrian guidance](https://wiki.openstreetmap.org/wiki/Guidelines_for_pedestrian_navigation) | Paths, sidewalks, crossings, entrances, access restrictions | Obtain a versioned extract; inspect connectivity and station access |
| Wheelchair attributes | [OpenStreetMap wheelchair guidance](https://wiki.openstreetmap.org/wiki/Key:wheelchair) | Explicit access tags where mapped | Missing tags mean unknown; transport accessibility sources also required |

Residents in employment, establishments, and jobs located at workplaces are different quantities. Do not substitute one for another. Facility presence does not establish service capacity, quality, or opening hours. Walking distances must follow traversable paths; straight-line buffers are not travel times.

## Account access and quotas

Both credentials are saved locally in the ignored `.env`; `.env.example` contains blank variable names only. On 2026-11-05 at approximately 22:28 UTC, the API credential returned HTTP 200 and one line from the generic Navitia endpoint; the static credential returned HTTP 200 and one record from the restricted GTFS catalogue. The same requests without credentials returned 401 and 403 respectively. These checks establish access to those endpoints, not GTFS archive integrity or next-passage/disruption coverage.

PRIM's [static authentication instructions](https://prim.iledefrance-mobilites.fr/fr/aide-et-contact/documentation/donnees-disponibles/jeux-de-donnees/generer-un-jeton-pour-acceder-aux-jeux-de-donnees-restreints) specify an Authorization header containing the apikey scheme and static token. The dynamic request used the apiKey header. Neither credential appears in the published evidence.

Relevant limits copied from the owner's dashboard on 2026-11-05:

| Service | Assigned quota |
| --- | ---: |
| Next passages: global / line / individual | 1,000 per day each |
| Global disruption messages | 1,000 per day |
| Messages displayed on screens | 1,000 per day |
| Journey calculator: traffic messages v2 | 4,000 per day |
| Journey calculator: general access v2 | 1,000 per day |
| Stop reference ICAR | 100 per day |
| Line reference ILICO / theoretical offer IBOO | 10 per day each |
| Isochrones v2 | 10 per month |

The [published quota schedule](https://prim.iledefrance-mobilites.fr/fr/notre-offre) agrees with these relevant limits and describes possible increases. One request every 120 seconds is 720 per day per endpoint; this is an illustration, not an approved collection plan. Response size, latency, freshness, retries, and retention also matter.

## Licence register: preliminary publisher labels

- GTFS, coverage, and global disruptions are labelled Licence Mobilité.
- Global next passages has inconsistent labels: Licence Mobilité in metadata and ODbL in its description. Resolve the applicable terms before redistribution.
- Stop/relations references show Etalab v2.0; the line reference shows ODbL.
- IGN Contours IRIS is listed under Licence Ouverte 2.0. [INSEE reuse guidance](https://www.insee.fr/fr/information/2008466?page=copyright.htm) specifies Licence Ouverte 2.0 unless an exception applies.
- [OpenStreetMap](https://www.openstreetmap.org/copyright) uses ODbL with attribution and applicable share-alike conditions. Tile hosting is a separate service decision.

Capture each selected release's actual terms, attribution, storage, and redistribution conditions. BPE releases can change for privacy-related withdrawals; raw public archives require particular care. A software licence does not relicense third-party data.

## What we cannot yet claim

- Complete independent actual arrivals, cancellations, vehicle positions, or passenger loads.
- Continuous real-time coverage of every metro/bus stop.
- A complete historical arrival or disruption archive.
- Precise neighbourhood-level workplace job locations or complete wheelchair routing.
- Validated prediction of incidents or actual operational responses to simulated closures.

These are M0 research questions. Their absence may narrow the first release without preventing a useful tool.
