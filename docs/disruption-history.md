# Disruption Intelligence: line-4 publication history

## Purpose and owner decisions

The owner chose incident history, métro line 4 initially, and collection only while the computer and collector are running. We archive **published notices**, not independently verified incidents. A notice ID is not necessarily a unique physical incident.

## Use it

Start **Start Explorer.cmd**, then **Start Notice History.cmd**. Keep both windows open. The notice collector checks every five minutes; Ctrl+C stops it. There is no scheduled task or automatic restart. The prediction collector is separate and optional.

```powershell
python disruption_history.py --once
python disruption_history.py --report
python disruption_history.py --history
python disruption_history.py --search "travaux"
```

`--once` makes at most one check. Report/history/search read the saved database without contacting PRIM. Search matches message text or notice ID, case-insensitively. The first interface is command-line JSON; a website history view is not yet implemented. Use `--port` if the explorer runs on a different port.

## Storage and method

Python's built-in SQLite stores `data/disruptions.sqlite`, excluded from Git. Three tables separate collection checks, distinct notice versions and sightings linking a version to a check. Every check saves its start/completion observation time, excess interval, success/empty/error status and the normalized response, including source fetch time, cache flag and excluded-record count. Provider-local dates retain their Europe/Paris meaning.

Actual code:

```python
fingerprint = hashlib.sha256(content.encode('utf-8')).hexdigest()
```

The fingerprint identifies the exact normalized notice content: text, status, effect, provider update time and reported application periods. An identical notice ID/content pair reuses its stored version; a changed pair adds a new version. Every successful check still retains its sightings, including a return to an earlier version. Fetch-time/cache changes alone do not create a new content version. The complete normalized response is retained for each successful check; raw upstream payloads are not archived.

**Synthetic input:** notice A, unchanged A, changed A, an empty response, original A again.

**Test output:** five checks, one notice ID, two content versions, four sightings. The empty check never sets an incident end time. First/last collected times mean when this collector saw that version, not actual incident boundaries. Cached sightings are retained and labelled in the check response, not treated as independent publisher updates.

## Validation — 9 November 2026

**Observed live input:** one successful line-4 response containing zero directly linked notices.

**Saved output:** `checks_by_status: {empty: 1}`, `notice_ids: 0`, `content_versions: 0`. History returned `[]`; immediate restart skipped a duplicate check. No populated live notice was available in this bounded check, so version changes were validated with synthetic data.

All 28 Python and six JavaScript tests pass. New tests cover changed/repeated/reappearing notices, disappearance, search, wrong-line rejection, failure recording, restart throttling, collection gaps and interruption rollback. Testing caught and fixed a search issue where JSON field names, rather than message text alone, matched a query.

## Limits and next action

- Existing direct-line filtering can exclude station-only/accessibility reports. The archive is not a complete operational incident log and does not infer station-level locations from prose.
- Five-minute checks can miss short-lived publications. Closed-computer periods create sampling bias; gaps become visible when checks resume. Excess interval includes request overhead, not just downtime. No catch-up requests are sent.
- One running collector checks at most 288 times per day before caching; it shares the explorer's five-minute traffic cache and 900-request rolling traffic budget. Other clients using the PRIM account are outside this local budget. Run only one explorer instance per budget file.
- Failed checks and empty successful checks remain different. No notice disappearance, reported end date or last-collected time proves incident resolution. We do not calculate actual disruption duration or severity scores.
- Notice text and databases remain local. Dataset redistribution terms remain unresolved and separate from repository licensing.

Next: accumulate history, inspect actual notice changes, then add a visual timeline. No collector was left running after the bounded validation. Implementation and tests are AI-assisted; the owner selected direction and scope.

Understanding checkpoint: why must we distinguish a notice's reported end date from the last time our collector saw it?
