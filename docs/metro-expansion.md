# From two lines to the métro network

## Purpose and decision

On 6 November 2026 the owner requested métro-only scope and all métro lines. Keep the same understandable explorer, with line filters, boarding points, on-demand predictions and traffic notices. No bus data is included in the current generated network. This does not authorise hosting or continuous collection.

## Select by mode, then join by identifiers

Actual code in [prepare_data.py](../src/prepare_data.py):

```python
rows[SHAPES], source = records(SHAPES, 'route_type="Subway"', key)
codes = metro_codes(rows[SHAPES])
```

In plain English: ask for métro routes, validate their identifiers, then use those identifiers to fetch the matching stop associations and real-time coverage. The catalogue exposes the mode as `Subway`, not GTFS's numeric `1`. An exploratory numeric-mode query returned no rows; inspection of line 4 established the actual field value before implementation. Names alone could select a bus with the same number.

**Observed input, selected fields:** `route_id=IDFM:C01386`, `route_short_name=3B`, `route_type=Subway`.

**Derived output, selected fields:** `id=STIF:Line::C01386:`, `name=3bis`, `source_name=3B`, `mode=Métro`. We preserve the source label and use the familiar name in the interface. Route order is numeric, with bis lines immediately after their parent number.

The source returned 16 routes: 1–14, 3B and 7B. This agrees with [IDFM's métro overview](https://www.iledefrance-mobilites.fr/le-reseau/services-de-mobilite/metro/presentation-plans-metro). We discover routes from the current published geometry dataset rather than silently adding planned lines from a broader reference catalogue. The mode query is rerun during preparation; unexpected duplicates, modes or route counts fail validation.

## Inspected coverage snapshot

| Line | Mapped boarding-point records | Matched real-time coverage | Coverage points without map match |
| --- | ---: | ---: | ---: |
| 1 | 50 | 50 | 0 |
| 2 | 50 | 50 | 0 |
| 3 | 50 | 50 | 0 |
| 3bis | 8 | 8 | 0 |
| 4 | 58 | 58 | 1 |
| 5 | 44 | 44 | 0 |
| 6 | 56 | 56 | 0 |
| 7 | 76 | 76 | 0 |
| 7bis | 13 | 13 | 1 |
| 8 | 76 | 76 | 0 |
| 9 | 74 | 74 | 0 |
| 10 | 41 | 40 | 0 |
| 11 | 38 | 38 | 0 |
| 12 | 62 | 62 | 0 |
| 13 | 65 | 64 | 1 |
| 14 | 42 | 42 | 0 |
| **Total** | **803** | **801** | **3** |

The three unmatched coverage records refer to Bagneux–Lucie Aubrac (4), Carrefour Pleyel (13), and Pré-Saint-Gervais (7bis). We do not guess replacement coordinates. Two mapped records on lines 10 and 13 are not listed in the coverage reference; their map positions remain available, but departure requests are disabled. Coverage counts are reference joins, not evidence of uninterrupted live data. Multiple records can represent one station or direction; do not report 803 stations.

## Keeping the implementation small

Preparation took 19 bounded catalogue requests: one geometry page, nine stop-association pages, nine coverage pages. Three preliminary source-inspection requests preceded the preparation. Pagination allows up to 3,000 records per dataset, checks stable totals and rejects unexpectedly empty pages. Counts and hashes are saved locally. Separate source pages are still not an atomic snapshot.

The existing file `data/pilot-network.json` is retained to avoid unnecessary migration. Its new `scope=metro` field prevents accidentally running an old bus-containing snapshot. Run `python src/prepare_data.py`, then `python src/app.py`.

Filters wrap across rows. A traffic dropdown lists the same routes as the map. The server allows traffic requests only for routes present in the métro snapshot; an arbitrary bus ID is rejected. Selecting a filter does not trigger a network request. Departure and traffic caches and request budgets are unchanged. No database or new package was needed.

## Validation and limits

Twenty-two offline tests pass, including rejection of bus routes, duplicate/empty route selection, numeric/bis ordering, exact identifier queries, missing stops and rejection of bus traffic requests. JavaScript syntax passes. The live snapshot passed coordinate, duplicate and per-route stop checks.

Browser validation confirmed all 16 filters, the 3bis subset (8 points), line 14 (42 points), a line-14 traffic response and a line-14 departure response. Two on-demand requests were used for those live checks; no all-stop polling was performed. Older departure records were visibly flagged. The map and filter layout were visually inspected.

All 16 reference routes are represented; we have not polled every stop or validated every line's live responses. Route geometry is not an ordered journey graph or verified transfer network. All earlier prediction, incident and licensing limitations still apply.

Next: inspect the expanded map and resolve reference mismatches before adding a closure model. Understanding check: why does a mapped boarding point without a real-time coverage match remain useful on the map?
