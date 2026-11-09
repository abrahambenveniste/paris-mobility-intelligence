# Public release: preparation and unresolved work

## Owner decisions

The owner wants a website accessible to everyone. Disruption collection should continue only while the owner's computer is running. A public website may remain online with older saved data, but it must show the last successful synchronization and collection gaps. No cloud-side periodic collector is authorized by this choice.

## What exists today

The GitHub repository is public. The map, departure queries, local SQLite archive and collectors run on the owner's computer. `127.0.0.1` is a loopback address: it cannot be used by other people's devices as a public site. There is no deployed public website or public sync service yet. The owner reported creating a Render account and chose a free tier; no deployment has been made.

## First hosting-preparation increment

**Purpose:** enable a host to provide PRIM credentials without checking them into Git. Actual code in `app.py`:

```python
if os.environ.get(name):
    values[name] = os.environ[name]
```

**Synthetic input:** a local `.env` value and a non-empty hosted environment value for the same PRIM key. **Output:** the hosted value takes precedence; if no hosted value is set, the local file remains available. Only the two named PRIM variables are read from the environment; unrelated environment secrets are not copied into this configuration. The tests use fake values, not real keys.

**Evidence:** 34 Python and six JavaScript tests pass. The new offline tests cover hosted precedence and operation without a local `.env` file. No real secrets or network requests were needed for the tests.

**Limit:** this does not make the app deployable. The server is still bound to localhost, and public request handling, persistent shared quotas, secure history synchronization and source-data terms remain unfinished. Do not expose the current local-only server directly or deploy this increment alone as a working public service.

## Proposed deployment design — not yet implemented

1. Host the web interface and a compatible backend on a managed service; do not expose the development server or local files to the internet.
2. Keep PRIM credentials server-side, use a shared cache and enforce request limits across all visitors and local collection. Never put API keys in browser code, source control or public logs.
3. Continue collecting notices locally only while the computer is on. Add an authenticated, encrypted, resumable synchronization process to a durable cloud database; public users get read-only access. Decide which historical fields can be published after source-terms review. Keep private credentials and raw responses out of Git.
4. Show last collection and synchronization times, failed/empty checks, coverage and gaps. A stalled local collector must not look like live data. Do not infer incident endings, independent incident counts or actual punctuality.
5. Test public access, credential isolation, shared quotas, duplicate writes, interrupted synchronization, stale data and costs before publishing. Retain the existing local-only mode.

The local implementation uses Python's `http.server`, a local SQLite file and filesystem-backed budgets. It cannot simply be uploaded as a static site: those server and storage features must be adapted to the chosen host. No host or operating budget has been committed yet.

## Source terms to resolve before public data release

- The [PRIM Navitia traffic-data catalogue](https://prim.iledefrance-mobilites.fr/fr/jeux-de-donnees/idfm-navitia-line_reports-v2) identifies Licence Mobilité and links both the licence and platform terms.
- The [unit next-passages API catalogue](https://prim.iledefrance-mobilites.fr/apis/idfm-ivtr-requete_unitaire) displays Licence Mobilité in its metadata but references ODbL in its terms section. Determine the applicable terms before releasing that feed publicly; do not assume the labels are interchangeable.
- PRIM's [terms](https://prim.iledefrance-mobilites.fr/fr/conditions-utilisation) say re-use must respect the applicable licence and any particular conditions. The [Licence Mobilités text published by IDFM](https://www.iledefrance-mobilites.fr/medias/portail-idfm/4dc136f7-df23-449b-9670-24bc5254a706_RAA138.pdf) contains attribution and, in specified cases, sharing requirements. Assess the relevant provisions and provenance for each source and public output; the repository's software licence is a separate unresolved matter.
- The local collector currently retains normalized traffic data; some inspected feed metadata has `private` labels. Do not assume those labels grant or prohibit redistribution without clarifying their meaning and the applicable licence.

These are preliminary source findings, not a legal conclusion. No notice data, tokens or account details were added to Git in this work.

## Next action

Complete the source-by-source terms and attribution register, implement/test the secure local-to-cloud sync and compatible hosted backend, then publish the actual working application to the chosen host. Do not report a public URL before deployment and external-access verification.
