"""Small PostgreSQL-backed rolling request budget for the public preview."""
import threading
import time


class PublicBudget:
    def __init__(self, connect, limit=100):
        self.connect, self.limit = connect, limit
        self.lock, self.cache = threading.Lock(), {}

    def get(self, identifier, loader):
        kind = identifier[0]
        if kind not in ('traffic', 'departures'):
            raise ValueError('Unsupported request type')
        with self.lock:
            now = time.monotonic()
            previous = self.cache.get(identifier)
            ttl = 60 if len(identifier) > 1 and identifier[1] == 'journey' else (300 if kind == 'traffic' else 120)
            if previous and now - previous[0] < ttl:
                return {**previous[1], 'cached': True}
            # Reserve before calling PRIM; errors count. A database failure fails closed.
            with self.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute('SELECT pg_advisory_xact_lock(%s)', (7246101,))
                    cur.execute("DELETE FROM pmi_private.public_request_budget WHERE reserved_at < now() - interval '24 hours'")
                    cur.execute("SELECT count(*) FILTER (WHERE kind = %s), count(*) FILTER (WHERE reserved_at > now() - interval '1 second') FROM pmi_private.public_request_budget", (kind,))
                    used, recent = cur.fetchone()
                    if used >= self.limit or recent:
                        raise RuntimeError('Public request limit reached; try later.')
                    cur.execute('INSERT INTO pmi_private.public_request_budget (kind) VALUES (%s)', (kind,))
            result = loader()
            self.cache[identifier] = time.monotonic(), result
            return {**result, 'cached': False}
