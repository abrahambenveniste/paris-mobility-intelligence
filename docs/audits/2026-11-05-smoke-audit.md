# M0 bounded data-quality audit — 2026-11-05

**Decision:** access and basic structural checks pass. Operational reliability scoring is not ready. Continue M0 on event identity, actual-passage evidence, and coordinate interpretation.

**Plain-language conclusion:** the inspected schedules and live predictions can support an initial explorer showing planned service and reported next departures. They do not yet support claims about actual delays, cancellations, or measured passenger waits. Keep the first milestone to one metro line and one bus route; show source age and missing data. The remaining practical checks are targeted bus timetable rows and how live records relate to scheduled service. A combined reliability score can wait.

## Scope and resource budget

- Four single-stop SIRI requests at approximately 22:34 UTC (23:34 Paris), without repeated polling.
- Provisional cases: metro 4 (C01374) and bus 38 (C01083). Convenience sample, not a representative pilot. One sampled metro terminus, Bagneux, is outside Paris.
- Ten data-service requests total: two catalogue samples, two filtered coverage pages, two archive attempts, and four live calls. Public documentation searches are separate.
- The server ignored the archive byte-range request; that attempt was stopped after 65,537 bytes. A subsequent streaming download was capped at 80 MiB and stopped at the cap after about six seconds.
- The saved archive is incomplete. Complete internal members were inspected using local ZIP headers and per-member CRC checks; shapes and the whole archive were not validated.
- Offline checks ran twice, about four seconds each. The second run added service-date and sample-composition checks. No application, scheduled collector, database, or model training was started.

## Results

| Check | Result | Interpretation |
| --- | --- | --- |
| Offline assertions | 31/31 passed | Parsing, selected CRCs, IDs, references, sampled time order, service availability, response hashes/statuses |
| Routes / stops / trips inspected | 2,027 / 53,405 / 400,653 | Full contents of these individual members; not full GTFS validation |
| Stop-time sample | First 5,000 rows; no missing times or invalid references/order detected | Includes 29 metro-4 rows and **no bus-38 rows**; regional convenience sample only |
| Calendar bounds | 2026-11-02 through 2026-12-04 | Broad bounds, not a promise of daily service on every route |
| Active scheduled trips on November 5 | Metro 4: 846; bus 38: 308 | Calendar plus date exceptions; scheduled counts, not observed vehicles |
| Filtered coverage inventory | 119 line/stop pairs: metro 4 = 59, bus 38 = 60 | Unique pairs; both pages retrieved; a list does not establish continuous coverage |
| Candidate stop-ID conversion | 118/119 matched GTFS stops | Prefix conversion is a hypothesis with an observed exception, not a finished crosswalk |
| Live endpoints | HTTP 200, service status true, target line present in 4/4 responses | 22 returned visits; only 12 belong to the requested candidate lines |
| Live trip IDs versus GTFS IDs | 0 exact matches for 22 distinct returned journey IDs | A validated crosswalk/matching method is needed before schedule comparisons |

## Findings that affect the design

1. **No ground truth in the sampled calls.** Among 12 target-line visits, expected departure was populated 12 times and expected arrival four times. Aimed arrival/departure and actual arrival/departure were populated zero times. All carried an `onTime` departure status; that label alone cannot establish measured punctuality.
2. **Response time and record time differ.** Target-record age at receipt ranged from 29.8 to 859.2 seconds. This measures time since `RecordedAtTime`, not vehicle delay or proven forecast error. Fresh HTTP responses can contain older source records.
3. **A stop response can contain multiple lines.** The two bus-stop responses contained 3 and 11 visits, but only two bus-38 visits each. Filter by returned line ID before calculating anything.
4. **One stop did not join by simple ID conversion.** `STIF:StopPoint:Q:483279:` (Bagneux - Lucie Aubrac) was listed and returned live data, but `IDFM:483279` was absent from the inspected GTFS stop IDs. Investigate stop hierarchy/validity; do not discard or match by name alone.
5. **Coverage coordinates need interpretation.** The inventory declares EPSG:2154 while using longitude/latitude field labels. An example has values around 6,863,737 and 652,856. These are not WGS84 degrees; axis order and transformation require verification against reference geometry.
6. **UTF-8 must be explicit.** An early local display used the Windows default text encoding and garbled an accented stop name. Re-reading the original bytes as UTF-8 corrected it. This was an audit-tool issue, not evidence of source corruption; the committed checker explicitly decodes UTF-8.

## Reproduction and limits

Run `python audit/check_samples.py` against the retained local samples; see [audit instructions](../../audit/README.md). Credentials and raw responses remain in ignored storage. The local manifest records request URLs, UTC receipt times, and live-response SHA-256 values. The checker writes a local JSON result and exits nonzero if an assertion fails.

Passing structural assertions does not validate fairness, prediction accuracy, actual arrivals, cancellation completeness, trip matching, or longitudinal stability. No disruption feed was sampled. Frequencies/exact timetable semantics, shapes, complete stop times, and the archive's central directory remain unchecked.

## Next action

Resolve the unmatched stop and trip-ID strategy; inspect targeted bus and metro timetable rows and exact/frequency semantics; investigate whether independent actual events exist. Only then choose defensible reliability measures and an approved collection design. The bounded audit is complete; M0 is not complete.

Sources: [GTFS catalogue](https://prim.iledefrance-mobilites.fr/jeux-de-donnees/offre-horaires-tc-gtfs-idfm), [coverage inventory](https://prim.iledefrance-mobilites.fr/fr/jeux-de-donnees/perimetre-des-donnees-tr-disponibles-plateforme-idfm), [next-passage parameters](https://prim.iledefrance-mobilites.fr/aide-et-contact/documentation/prise-en-main-des-api/prise-en-main-des-api-prochains-passages/structure-des-requetes-parametres-dappel). Empirical counts above come from this audit's local snapshots, not publisher guarantees.
