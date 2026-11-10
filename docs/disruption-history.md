# Disruption Intelligence: métro publication history

**Current scope:** all published métro lines, checked locally every 30 minutes. Earlier sections below describe the original line-4 pilot; the current instructions are in the latest section.

## Purpose and owner decisions

The owner chose incident history, métro line 4 initially, and collection only while the computer and collector are running. We archive **published notices**, not independently verified incidents. A notice ID is not necessarily a unique physical incident.

## Use it

Start **launchers/Start Explorer.cmd**, then **launchers/Start Notice History.cmd**. Keep both windows open. The notice collector checks every five minutes; Ctrl+C stops it. There is no scheduled task or automatic restart. The prediction collector is separate and optional.

```powershell
python src/disruption_history.py --once
python src/disruption_history.py --report
python src/disruption_history.py --history
python src/disruption_history.py --search "travaux"
```

`--once` makes at most one check. Report/history/search read the saved database without contacting PRIM. Search matches message text or notice ID, case-insensitively. The website history view is available at http://127.0.0.1:8765/history while the explorer runs. It shows saved versions, search and collection-quality counts; the command-line JSON remains available. Use `--port` if the explorer runs on a different port.

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

Next: accumulate history and inspect actual notice changes in the website history view. No collector was left running after the bounded validation. Implementation and tests are AI-assisted; the owner selected direction and scope.

Understanding checkpoint: why must we distinguish a notice's reported end date from the last time our collector saw it?

## Website history view — 9 November 2026

Purpose: inspect saved publications without command-line work. The `/api/notice-history` endpoint opens SQLite with `mode=ro` in a consistent read transaction; it neither creates a missing archive nor contacts PRIM. Search matches notice IDs/message text. The UI shows up to 200 matching versions ordered newest-first by first collection time, with reported status, effect, message, application periods, provider update and collection timestamps. Identical content can recur; this version view is not a complete sequence of change events or an incident-duration chart.

Observed input: the existing archive contains one empty successful check. Output: zero notice IDs/versions, one empty check, and an explicit warning against assuming normal service. Browser search and refresh preserved this state without upstream requests. All 29 Python and six JavaScript tests pass; a new test confirms missing-file handling, filtered populated versions and byte-for-byte database preservation after reading. Populated cards were not verified against a live notice in this increment.

Implementation is AI-assisted. Next: gather real notices and review their version history; physical incident boundaries remain unverified.

## All-métro integrated explorer — 9 November 2026

**Purpose:** the owner expanded the local disruption history to all métro lines and requested one integrated tool. The map, line departures and saved notice history now link to each other; history cards link to the corresponding filtered map line. Historical status is explicitly labelled at collection, not current status.

**Run:** double-click `launchers/Start Platform.cmd`. It starts or reuses the local explorer, starts the all-métro notice collector and starts the existing two-point line-4 prediction collector. Keep the terminal open; Ctrl+C stops processes started by this launcher, not a pre-existing explorer. Alternatively `python src/run_platform.py` starts only notice collection; pass `--with-predictions` for both. Do not run duplicate explorer processes sharing the same budget file. The collector is not installed as a background service.

**Sampling:** the 16 published lines are discovered from the local reference snapshot. Each line is checked sequentially every 30 minutes while running: at most 16 × 48 = 768 upstream traffic requests per 24 hours before caching, below the explorer's shared rolling limit of 900. This assumes one collector and a stable 16-line network; on-demand requests share that budget, and other PRIM clients are outside it. The interval grows with route count. A check skipped because it was recent is not duplicated. Previous line-4 checks are migrated and a local pre-migration SQLite backup is made. Per-line timestamps and gaps remain separate.

**Code:** `SELECT MAX(started_at) FROM checks WHERE line_id=?` finds the previous check for the same line, so a recent check of one line cannot suppress another.

**Observed input:** one bounded collection cycle using the current reference: 15 new line checks and the recent line-4 check retained. **Output:** 16 lines with saved checks; 4 checks returned 13 distinct notice IDs, 12 were empty, none failed. This is one observation window, not a measure of incidents or current service. The browser showed populated line-6 notices; its map link selected métro 6 and displayed 56 mapped line-point records. Notice content is kept local and not reproduced here.

**Validation:** 32 Python and six JavaScript tests passed. New tests cover independent line histories, restart throttling, old line-4 migration with backup, and platform launcher process ownership. Browser checks covered populated history, line filtering and map navigation. The Windows launcher was not separately double-click tested.

**Data quality:** the first sample includes multiple similar notices under separate IDs and some reported application periods of about one second. We do not merge these records or interpret reported periods as measured durations. We must inspect these anomalies, station-only notice coverage and changes across real repeated observations before estimating recurrence or severity. Current history cards are content versions, not a full event timeline or a validated incident count.

**Next:** use the launcher to collect while the computer is on; examine real changes and gaps. Cloud hosting and publication of data need a separate deployment design and source-terms review. Code and checks are AI-assisted.
