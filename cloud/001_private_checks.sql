-- Version 1: private normalized notice checks; no public API or data publication.
BEGIN;

CREATE SCHEMA IF NOT EXISTS pmi_private;
REVOKE ALL ON SCHEMA pmi_private FROM PUBLIC, anon, authenticated;

CREATE TABLE IF NOT EXISTS pmi_private.notice_checks (
    archive_id uuid NOT NULL,
    check_id bigint NOT NULL CHECK (check_id > 0),
    line_id text NOT NULL CHECK (length(line_id) BETWEEN 1 AND 100),
    started_at double precision NOT NULL CHECK (started_at >= 0),
    observed_at timestamptz NOT NULL,
    gap_seconds double precision NOT NULL CHECK (gap_seconds >= 0),
    status text NOT NULL CHECK (status IN ('ok', 'empty', 'error')),
    fetched_at timestamptz,
    cached boolean,
    excluded_unlinked integer CHECK (excluded_unlinked >= 0),
    error_kind text,
    notices jsonb NOT NULL CHECK (jsonb_typeof(notices) = 'array'),
    synced_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (archive_id, check_id),
    CHECK ((status = 'ok' AND jsonb_array_length(notices) > 0 AND fetched_at IS NOT NULL)
        OR (status = 'empty' AND jsonb_array_length(notices) = 0 AND fetched_at IS NOT NULL)
        OR (status = 'error' AND jsonb_array_length(notices) = 0 AND fetched_at IS NULL))
);

CREATE INDEX IF NOT EXISTS notice_checks_line_time
    ON pmi_private.notice_checks (line_id, observed_at DESC);
ALTER TABLE pmi_private.notice_checks ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE pmi_private.notice_checks FROM PUBLIC, anon, authenticated;

COMMIT;
