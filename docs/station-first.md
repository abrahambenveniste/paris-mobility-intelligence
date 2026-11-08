# Station-first browsing

## Purpose and owner choices

The owner chose usability improvements, then station-first navigation, and approved keeping differently named places separate. The flow is now: search a station name → select it → choose a line → read that line's reported destinations and estimates. Optional line filtering remains available, and a button opens traffic notices for the selected line.

## Group records without inventing connections

Actual code from [web/stations.js](../web/stations.js):

```javascript
const id = JSON.stringify([stop.name, stop.commune]);
```

This creates a grouping key from two values: the exact source name and commune. Records with the same pair share one display entry. Search ignores accents, but grouping does not merge similar spellings, nearby names or different communes. These are display groups, not verified station complexes or transfer links.

**Observed input:** the saved snapshot contains ten Châtelet/Paris boarding-point records across lines 1, 4, 7, 11 and 14, and two Les Halles/Paris records on line 4.

**Derived output:** one Châtelet entry with five line choices; a separate Les Halles entry with line 4. All 803 underlying records remain available, arranged into 327 exact name/commune groups. This is not a newly measured station count.

**Synthetic test input:** two platforms named Châtelet in Paris on line A, a third on line B, one Les Halles record, and one Châtelet record in another commune. Output: three separate name/commune groups; selecting line A within Châtelet/Paris retains its two platform records, including an uncovered one.

## Predictions, requests and errors

Searching or selecting a station makes no PRIM request. Choosing a line requests its covered boarding points; the button displays how many source points it contains. Unsupported points remain visible with an explanation, without an API call. Existing two-minute caching and the shared departure budget still apply.

Estimates are grouped under exact reported destination names, then sorted by estimated timestamp. Each estimate retains its source-point ID and record age. Source response times and omitted-entry counts are available in an expandable section, which opens automatically for failed, uncovered or empty responses. Destination names come from the provider; we do not infer a platform direction from coordinates or names. Records from different points are not deduplicated into supposed train journeys. No independent confirmed passage observations have been added.

`Promise.allSettled` lets one failed point coexist with successful results. Each failed or uncovered point is shown explicitly. A request sequence number prevents results from an old selection appearing under a new station. Changing search text or the optional line filter clears the selection. Traffic notices remain explicitly line-level, not necessarily station-specific.

## Validation and limits

Four offline JavaScript tests and 22 Python tests pass. The new tests check exact grouping, separate names/communes, line isolation, empty input and preservation of covered/uncovered points. JavaScript syntax also passes.

Browser checks confirmed accent-insensitive Châtelet search, five line choices, two line-4 point requests, cached refresh, and a separate Les Halles search result. The two live responses returned no future estimates at the late-night check; that state was shown without inferring no service. Populated destination rendering was not verified against a fresh non-empty live response in this increment. No new reference download was needed.

Remaining limitations: exact names can split spelling variants; identical name/commune pairs can group objects without proving physical connectivity. A direction selector based on verified topology would require more data. No routing or closure simulation is implied.

## Destination grouping — 8 November 2026

**Purpose:** make the destination easier to find without hiding data provenance. The owner approved this recommended increment; implementation and checks are AI-assisted.

Actual code in `web/stations.js`:

```javascript
const destination = observation.destination || 'Unknown destination';
if (!groups.has(destination)) groups.set(destination, []);
groups.get(destination).push(observation);
```

A JavaScript `Map` keeps a list for each destination. Adding a record to a list changes its presentation, not its meaning. Sorting uses parsed timestamps, so UTC and Paris offsets are compared as actual instants. Missing destinations get an explicit label; reported cancellations without times remain visible at the end of their group. All returned normalised observations are shown, replacing the earlier six-per-point display limit.

**Synthetic input:** Bagneux estimates from A at 09:08+01:00, B at 08:03Z and C at 08:03Z; a Clignancourt estimate from D.

**Test output:** Bagneux contains B, C, A in that order; Clignancourt remains separate. B and C both remain, even with identical times. The input is unchanged.

**Empirically inspected UI:** Châtelet / métro 4 returned eight estimates across two successful point responses: four towards Bagneux - Lucie Aubrac (point 22092), four towards Porte de Clignancourt (point 463158). The browser showed both groups and source ages, including older-record warnings. Opening source details showed fetch times and omitted-entry counts. Refresh reused both cached responses. This bounded check made two upstream departure requests, with no reference refresh or traffic call.

**Validation:** 22 Python tests and six JavaScript tests pass; JavaScript syntax and Git whitespace checks pass. New tests cover grouping, duplicate preservation, time-zone sorting, unchanged input, unknown destinations, untimed cancellations and empty input. Browser inspection confirmed populated rendering and cached refresh; failed responses were not induced against PRIM.

**Limitations:** destination spelling variants remain separate. Multiple observations are not necessarily distinct trains. A source record can be old even when freshly fetched. Countdown labels update on refresh; a cached estimate whose time passed remains explicitly labelled “Time passed”. These are predictions, not observed passages.

**Next:** owner review of the destination view before another feature. Understanding question: why is a freshly fetched response not necessarily a fresh prediction?

Selected-line notices can now be checked alongside departures: [implementation and limits](inline-notices.md).
