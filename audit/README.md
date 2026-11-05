# Offline M0 checks

This directory contains audit tooling only. It neither requests data nor reads credentials, and it does not implement a collector or application.

Run from the repository root with standard-library Python:

```text
python audit/check_samples.py
```

The checker requires the ignored local files under `artifacts/m0/`:

- `gtfs.zip`: the bounded ZIP prefix retained by the audit.
- `partial-zip-index.json`: local-header member inventory with name, data offset, compressed/uncompressed sizes, compression method, flags, CRC, and completeness.
- `coverage-pilot.json` and `coverage-pilot-page2.json`: both pages of the filtered coverage response.
- `live-manifest.json` and `live-0.json` through `live-3.json`: request metadata and responses.

It creates `quality-summary.json` locally. Successful assertions exit 0; failed assertions exit 1. Missing or malformed inputs raise an error. The service date is fixed to 2026-11-05 for this audit; change it and its weekday selection together when adapting the checks.

## How the inputs were obtained

Static requests used the restricted Opendatasoft v2.1 catalogue at `data.iledefrance-mobilites.fr` with the static authentication header. The GTFS file URL came from the catalogue record, not a hard-coded archive location.

Coverage dataset: `perimetre-des-donnees-tr-disponibles-plateforme-idfm`. Filter: `name_line in ("4","38") and search(operatorname,"RATP")`; limit 100, offsets 0 and 100. Pagination had no explicit ordering, so total-count and pair-uniqueness checks were used; this does not guarantee atomic consistency if the source updates between pages.

From the first page, the first two distinct stop IDs per candidate line were chosen. Each received one `stop-monitoring?MonitoringRef=...` request at `prim.iledefrance-mobilites.fr/marketplace/` using the API credential. The manifest retains the exact parameters and receipt timestamps.

The ZIP index was read sequentially from local file headers: signature `PK\x03\x04`, member name and extra fields, compressed size, uncompressed size, CRC, and compression method. ZIP64 size fields were resolved where present. Indexing stopped at the first incomplete member. The checker only reads complete deflate members; it validates CRC/length for full members and explicitly samples stop times with a two-megabyte decompression cap.

Exact replay requires these same snapshots. Raw data is not distributed while reuse terms remain under review; a clean clone alone cannot rerun the empirical checks. New live downloads will produce different results. See the [dated report](../docs/audits/2026-11-05-smoke-audit.md) for scope, findings, and unresolved work.
