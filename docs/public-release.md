# Public release: preparation and unresolved work

## Owner decisions

The owner wants a website accessible to everyone. Disruption collection should continue only while the owner's computer is running. A public website may remain online with older saved data, but it must show the last successful synchronization and collection gaps. No cloud-side periodic collector is authorized by this choice.

## What exists today

The GitHub repository is public. The map, departure queries, local SQLite archive and collectors run on the owner's computer. `127.0.0.1` is a loopback address: it cannot be used by other people's devices as a public site. There is no deployed public website or public sync service yet. The owner reported creating a Render account and chose a free tier; no deployment has been made.

## Public map preview — preparation

The owner approved publishing a clearly labelled map-only preview first, while the full live application is completed separately. The preview uses the public [métro route shapes](https://data.iledefrance-mobilites.fr/explore/dataset/traces-des-lignes-de-transport-en-commun-idfm/) and [stop/line associations](https://data.iledefrance-mobilites.fr/explore/dataset/arrets-lignes/); the publisher's catalog metadata identifies both as ODbL. It does not require API credentials, transmit the private archive, or expose arrival/traffic endpoints. The restricted real-time coverage dataset is not used: its absence is not shown as zero coverage.

`python prepare_public.py` fetches and validates the published reference subset into ignored `data/public-network.json`. On Render use build command `python prepare_public.py` and start command `python preview_server.py --public`; local preview omits `--public` and listens only on localhost. The public server exposes only the map assets and the prepared network subset. Build output is generated on the host, not committed to Git. Render's free tier sleeps after inactivity; the reference data is refreshed on each build, not continuously.

**Observed validation:** anonymous source requests succeeded; a full local preparation produced 16 lines and 803 boarding-point records. Browser inspection confirmed the visible preview limitation, map, Châtelet search and five line choices. A focused HTTP test checked the map and network routes, and confirmed local secrets, database files and live endpoints return 404. JavaScript syntax passed. This is a single snapshot and does not validate network completeness or actual service.

**Limitations:** public live arrivals, traffic notices, collection history and the full analytics remain unavailable. The public preview is a separate read-only map experience and does not expose the local application. Hosting success and a public URL must be verified separately. The owner chose the free plan; no payment method or paid service is needed for this preview.

## First hosting-preparation increment

**Purpose:** enable a host to provide PRIM credentials without checking them into Git. Actual code in `app.py`:

```python
if os.environ.get(name):
    values[name] = os.environ[name]
```

**Synthetic input:** a local `.env` value and a non-empty hosted environment value for the same PRIM key. **Output:** the hosted value takes precedence; if no hosted value is set, the local file remains available. Only the two named PRIM variables are read from the environment; unrelated environment secrets are not copied into this configuration. The tests use fake values, not real keys.

**Evidence:** 34 Python and six JavaScript tests pass. The new offline tests cover hosted precedence and operation without a local `.env` file. No real secrets or network requests were needed for the tests.

**Limit:** this does not make the app deployable. The server is still bound to localhost, and public request handling, persistent shared quotas, secure history synchronization and source-data terms remain unfinished. Do not expose the current local-only server directly or deploy this increment alone as a working public service.

## Local sync preparation — 9 November 2026

**Purpose:** prepare resumable notice batches before connecting the new Supabase project. The owner reported creating a free project; no database connection or cloud write has been made.

`sync_preview.py` reads the local SQLite archive in a single read-only transaction. A caller supplies an archive UUID and a check cursor. Each batch contains at most 100 checks, their line and collection times, gaps, result status, selected response metadata and the exact saved notice versions. It never advances a stored cursor, writes a file, prints notice content or sends data. A future destination must commit a batch atomically and deduplicate using the archive UUID plus local check ID before any cursor is advanced; that destination is not implemented yet.

Actual code:

```python
WHERE id>? ORDER BY id LIMIT ?
```

**Synthetic input:** three checks: a notice, a changed version, then an empty response. **Output:** a first batch with two checks and distinct fingerprints; resuming at its cursor returns the empty check. Repeating the same request produces the same batch. Failed checks stay separate from empty checks. A response/sightings mismatch is rejected.

**Observed local input:** the current archive. **Output:** 16 checks and 13 notice sightings; `sent: false`. No notice text, raw data or credentials are committed or transmitted.

**Validation:** 37 Python tests and six JavaScript tests pass. Synthetic tests cover repeatable batches, cursor boundaries, changed notices, errors, malformed arguments and inconsistent records. No Supabase schema, policies or synchronization endpoint has been created or tested. The fixed example UUID used for the dry run is a test value and is not stored as the identity of the owner's archive.

**Next:** design and validate the private cloud schema and permissions, choose a persistent unique ID for the real archive, then implement authenticated atomic uploads and a read-only public view. Check source terms before any notice is published. No public website exists yet.

## Private cloud table — 9 November 2026

**Purpose:** give future synchronized checks a durable destination while keeping the database private. The owner created a free Supabase project and asked us to continue toward a public website.

**Implementation:** [`cloud/001_private_checks.sql`](../cloud/001_private_checks.sql) creates the `pmi_private.notice_checks` table. The two-part primary key `(archive_id, check_id)` identifies a check within a particular archive. Status, collection times, gaps, source metadata and normalized notice content have separate fields. The SQL enables row-level security and revokes schema/table access from PostgreSQL's `PUBLIC`, Supabase `anon` and `authenticated` roles. No public view, API, credentials or real notice data was added. A database owner or privileged backend can still access this table; RLS is not a substitute for protecting those credentials.

Actual code:

```sql
PRIMARY KEY (archive_id, check_id)
```

**Synthetic input:** two records with the same archive ID and check ID would represent the same local check. **Output:** PostgreSQL's primary key prevents both from being inserted as distinct rows. This is an identity constraint, not a complete upload/retry mechanism.

**Empirically tested in the owner's Supabase project:** a rolled-back transaction created the schema and accepted one synthetic empty check; `anon` and `authenticated` lacked schema access and row-level security was enabled. A separate intentionally inconsistent synthetic check was rejected by a check constraint. After creating the empty structure, a read-only query confirmed: anonymous read/write `false`; authenticated read/write `false`; RLS `true`; stored checks `0`. No real notice records were uploaded. These role checks do not constitute a full penetration test or a hosted-app test.

**Limit at this stage:** there was no uploader, backend read role, cloud API, public site, or durable shared API quota. Do not place an administrator connection string in browser code. The private schema and table are not a public application. Review the data terms before publishing notice content.

**Next:** implement and test authenticated synchronization and a separately controlled read path. Then adapt and deploy the web server, verify dataset terms, and test a real public URL. No background cloud collection is authorized.

## Private synchronization sender — 9 November 2026

**Purpose:** prepare a deliberate, local-to-cloud transfer that can be retried safely while the owner's computer is on. `sync_sender.py` reads the existing validated local batches. It is a manual one-off command: it is not scheduled or started by the platform launcher.

Actual code:

```python
with connection.transaction():
    # Insert checks; reject any conflicting previously saved identity.
```

Each batch commits as a unit. A matching `(archive_id, check_id)` is counted as a retry only after its stored content matches; different content raises an error and rolls back the batch. The cursor advances in memory after the transaction succeeds. By default, a later run replays from the beginning and checks existing records; an explicit `--after` can resume from a known committed check. It does not yet store a persistent checkpoint, so replay gets slower as the archive grows. The supplied archive UUID must remain stable and must be backed up with the local archive; restoring an older archive under a different UUID can create duplicate observations.

**Synthetic input:** upload checks 1 and 2; upload the identical batch again. **Test output:** first upload `inserted: 2`, second upload `repeated: 2`. If an existing check ID has changed content, the fake-connection test confirms the entire batch is rolled back. Tests use only synthetic content.

**Security design:** configuration is read only from `PMI_DATABASE_URL`, `PMI_DATABASE_CA` and `PMI_ARCHIVE_ID` environment variables, never command-line arguments. Connections require PostgreSQL `sslmode=verify-full` and a supplied CA certificate. Error output includes only the exception class, not connection strings or notice content. Supabase explains [certificate verification](https://supabase.com/docs/guides/database/connecting-to-postgres); the optional Psycopg dependency is pinned separately in `requirements-sync.txt`. The dependency has not been installed or used against the real project yet.

**Evidence:** 40 Python and six JavaScript tests pass. A fake database connection tested transaction rollback, idempotent retry, TLS configuration and avoiding secret output. Separately, a rolled-back synthetic SQL transaction in the actual Supabase database returned `retry_deduplicated=true`, `identical_matches=true`, and `changed_matches=false`. These checks did not execute the Python sender end-to-end against Supabase. No real notice data was uploaded.

**Remaining:** create a narrowly scoped writer credential without using an administrator credential in the application, provision a stable archive UUID and trusted CA, then run a bounded end-to-end integration test. The sender has no public read API, hosted server, automatic upload loop or shared cross-client PRIM budget. Public release and source-terms review remain unfinished.

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
