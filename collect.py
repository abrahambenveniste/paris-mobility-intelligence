"""Local project-1 pilot: retain normalized predictions, never inferred arrivals."""
import argparse
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import time
from urllib.parse import urlencode
from urllib.request import urlopen

from app import NETWORK, ROOT

LINE = 'STIF:Line::C01374:'
INTERVAL = 300
DATABASE = ROOT / 'data' / 'reliability.sqlite'


def pilot_points(network):
    points = [s for s in network['stops'] if s['line_id'] == LINE
              and s['name'] == 'Châtelet' and s['commune'] == 'Paris'
              and s['live_supported']]
    if len(points) != 2 or len({s['monitoring_ref'] for s in points}) != 2:
        raise ValueError('Expected two distinct covered Châtelet line-4 points; review the reference snapshot.')
    return points


def connect(path=DATABASE):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=20)
    db.executescript('''
      CREATE TABLE IF NOT EXISTS cycles (
        id INTEGER PRIMARY KEY, started_at REAL NOT NULL,
        gap_seconds REAL NOT NULL, snapshot_sha256 TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS samples (
        id INTEGER PRIMARY KEY, cycle_id INTEGER NOT NULL,
        point_id TEXT NOT NULL, line_id TEXT NOT NULL, requested_at TEXT NOT NULL,
        completed_at TEXT NOT NULL, status TEXT NOT NULL,
        response_json TEXT, error_kind TEXT,
        UNIQUE(cycle_id, point_id));
    ''')
    return db


def fetch(point, port):
    query = urlencode({'line': LINE, 'stop': point['monitoring_ref']})
    with urlopen(f'http://127.0.0.1:{port}/api/departures?{query}', timeout=25) as response:
        result = json.load(response)
    if not isinstance(result.get('departures'), list) or not result.get('fetched_at'):
        raise ValueError('Unexpected normalized response')
    return result


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def collect_cycle(db, points, snapshot_hash, loader, now=None):
    now = time.time() if now is None else now
    # Serializes collectors sharing this database; no duplicate cycle after restart.
    db.execute('BEGIN IMMEDIATE')
    try:
        previous = db.execute('SELECT MAX(started_at) FROM cycles').fetchone()[0]
        if previous is not None and now - previous < INTERVAL:
            db.rollback()
            return False
        gap = max(0, now - previous - INTERVAL) if previous is not None else 0
        cycle = db.execute('INSERT INTO cycles(started_at,gap_seconds,snapshot_sha256) VALUES(?,?,?)',
                           (now, gap, snapshot_hash)).lastrowid
        for point in points:
            requested = utc_now()
            try:
                payload = loader(point)
                status = 'ok' if payload['departures'] else 'empty'
                encoded, error = json.dumps(payload, ensure_ascii=False), None
            except Exception as exc:
                # Persist the error class only: exception strings can contain URLs/secrets.
                status, encoded, error = 'error', None, type(exc).__name__
            db.execute('''INSERT INTO samples(cycle_id,point_id,line_id,requested_at,
                       completed_at,status,response_json,error_kind) VALUES(?,?,?,?,?,?,?,?)''',
                       (cycle, point['id'], LINE, requested, utc_now(), status, encoded, error))
        db.commit()
        return True
    except BaseException:
        db.rollback()
        raise


def summary(db):
    counts = dict(db.execute('SELECT status,COUNT(*) FROM samples GROUP BY status'))
    cycles, gap = db.execute('SELECT COUNT(*),COALESCE(SUM(gap_seconds),0) FROM cycles').fetchone()
    return {'cycles': cycles, 'point_responses': counts,
            'excess_seconds_between_cycles': round(gap),
            'meaning': 'Collection quality only; not punctuality or cancellations.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--once', action='store_true', help='Collect at most one cycle and exit')
    parser.add_argument('--report', action='store_true', help='Show saved collection quality; no network calls')
    parser.add_argument('--port', type=int, default=8765, help='Port of the running local explorer')
    args = parser.parse_args()
    with closing(connect()) as db:
        if args.report:
            print(json.dumps(summary(db), indent=2))
            return
        raw = NETWORK.read_bytes()
        points = pilot_points(json.loads(raw))
        digest = hashlib.sha256(raw).hexdigest()
        print('Collecting Châtelet / métro 4: two points every five minutes. Ctrl+C stops.\n'
              'Keep the local explorer running. Database: data/reliability.sqlite', flush=True)
        try:
            while True:
                collected = collect_cycle(db, points, digest, lambda p: fetch(p, args.port))
                print(json.dumps(summary(db)) if collected else 'Recent cycle already saved; waiting.', flush=True)
                if args.once:
                    break
                # No catch-up burst after sleep, shutdown or an interrupted session.
                time.sleep(INTERVAL)
        except KeyboardInterrupt:
            print('\nCollector stopped. Completed cycles are saved.')


if __name__ == '__main__':
    main()
