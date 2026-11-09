-- Private, restart-safe PRIM request reservations; no source response data.
BEGIN;
CREATE SCHEMA IF NOT EXISTS pmi_private;
REVOKE ALL ON SCHEMA pmi_private FROM PUBLIC, anon, authenticated;
CREATE TABLE IF NOT EXISTS pmi_private.public_request_budget (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    kind text NOT NULL CHECK (kind IN ('traffic', 'departures')),
    reserved_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS public_request_budget_time ON pmi_private.public_request_budget (reserved_at);
ALTER TABLE pmi_private.public_request_budget ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON pmi_private.public_request_budget FROM PUBLIC, anon, authenticated;
COMMIT;
