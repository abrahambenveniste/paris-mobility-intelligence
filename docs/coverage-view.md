# Making reference coverage visible

## Purpose

Before building a closure scenario, users need to see where our input references match and where they do not. The Reference coverage panel follows the selected métro line. Search text filters the boarding-point list only; it does not silently change the coverage totals.

## Method and actual code

The prepared snapshot already contains mapped records with a `live_supported` flag and a separate `unmapped` list. [web/quality.js](../web/quality.js) summarises these existing records without requesting new data:

```javascript
const missingCoverage = mapped.filter(stop => !stop.live_supported);
```

`filter` keeps records satisfying a condition; `!` means “not”. This selects mapped points absent from the real-time coverage reference. It does not identify stopped service, cancelled trains or inaccurate predictions.

**Synthetic input:** three mapped line/point records, two flagged `true`, one flagged `false`; a separate coverage record has no map match.

**Derived output:** three mapped, two matched, one missing coverage, one missing map position. The two mismatch directions are separate. A point shared by two lines counts twice because the unit is a line/boarding-point association, not a unique station.

## Observed snapshot and browser validation

The existing 6 November 2026 snapshot gives 803 mapped records, 801 listed for coverage, two mapped without coverage and three coverage-listed without map matches. Line 13 gives 65, 64, one and one respectively.

The line-13 gap view shows Carrefour Pleyel under `IDFM:495051` in the map reference and `STIF:StopPoint:Q:22239:` in coverage. A shared name is not proof these records represent the same boarding point. No identifier replacement or coordinate guess was made.

Browser checks verified all-line totals, line-13 totals, the expanded gap list and independence from search text. Two offline JavaScript tests verify counts, line filtering, empty subsets and association-level counting. All 22 existing Python tests also pass. Run:

```powershell
node --test tests/quality.test.js
python -m unittest discover -s tests -q
```

Node is needed only for JavaScript tests, not to run the app. No PRIM calls or new dataset downloads were needed for this increment.

## Limit and next action

These are reference matches, not live-service measurements or a general quality score. The panel displays download time separately from publisher update time. Closing the reference gaps requires checking authoritative identifier relationships, not deleting inconvenient records.

Next: investigate whether the mismatched identifiers have an authoritative replacement or relationship. Owner understanding check: does absence from the coverage reference prove a station has no trains?
