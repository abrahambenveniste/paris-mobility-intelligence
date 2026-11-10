# Project 1: local collection pilot

## Purpose and scope

The owner approved starting project 1 on line 4, collecting only while their computer and collector are running. The implementation starts with the two previously inspected Châtelet boarding points, not all line-4 stations. This is a data-quality pilot, not yet a reliability score.

## Run

1. Start the explorer with **launchers/Start Explorer.cmd**.
2. Open **launchers/Start Collector.cmd**. Keep both windows open.
3. Stop the collector with Ctrl+C. Completed cycles remain saved.

Equivalent commands: `python app.py` and, in another terminal, `python collect.py`. Use `python collect.py --once` for one bounded cycle or `python collect.py --report` for a saved-data summary without network requests. If the explorer uses a different port, pass it to the collector with `--port`.

The database is `data/reliability.sqlite`, ignored by Git. SQLite is included with Python: it provides transactions and restart-safe local storage without installing a database server. No scheduled task, cloud service or automatic startup is installed.

## What is saved

Every completed cycle records its start time, the reference snapshot's SHA-256 fingerprint and excess elapsed time since the preceding cycle. Each point sample retains request/completion times, point and line IDs, success/empty/error status, and the explorer's normalized JSON. That JSON includes prediction times, source-record times, fetch time, cache flag and excluded-entry counts. Error classes are saved without potentially sensitive exception messages.

Actual code:

```python
status = 'ok' if payload['departures'] else 'empty'
```

**Input:** a successful response with `departures: []`. **Output:** `empty`, never “cancelled”. A failed request is recorded separately as `error`.

The collector reuses the running explorer's cache and persistent request budget. Two points every 300 seconds implies at most 576 point requests per 24 hours from one collector/database before caching. The explorer's shared 900-request rolling budget includes its own departure requests; other apps using the same PRIM account remain outside that local limit. Do not run multiple explorer instances against the same budget file.

Cycles are committed together. An interrupted cycle rolls back; restart skips a cycle if the last completed cycle began less than five minutes ago. There is no catch-up burst. Collection gaps are excess time beyond the nominal five-minute interval between saved cycles; this includes request overhead and is not an exact uptime measure. A final shutdown gap becomes measurable only when collection resumes. A backwards system clock pauses sampling until the interval catches up.

## Evidence — 8 November 2026

One live cycle saved two successful point responses. An immediate restart skipped duplication. The report returned `cycles: 1`, `point_responses: {ok: 2}` and zero excess seconds. This proves a bounded collection path, not ongoing coverage.

All 25 Python and six JavaScript tests pass. New synthetic checks cover empty versus failed responses, cache metadata preservation, restart deduplication, gap calculation, interrupted-cycle rollback and changed/duplicate reference selection. Testing exposed a Windows SQLite handle cleanup issue, corrected by explicitly closing connections.

## Scientific limits and next action

These are normalized snapshots, not raw SIRI payloads. The current explorer strips journey identifiers and past entries; this archive therefore cannot yet reliably match the same train across snapshots, measure forecast accuracy or infer actual headways. Five-minute sampling can miss intervening trains or changes. Châtelet alone does not represent line 4; user-operated collection also creates time-of-day selection bias.

Next: inspect accumulated response availability, source ages and gaps. Before prediction-stability analysis, retain and validate stable journey identifiers in a dedicated research representation. Before actual punctuality analysis, establish suitable scheduled and confirmed observed timestamps. Do not build a composite reliability ranking from these initial records.

Understanding checkpoint: why is an empty prediction response different from evidence of a cancelled train? The owner chose scope; implementation and checks are AI-assisted.
