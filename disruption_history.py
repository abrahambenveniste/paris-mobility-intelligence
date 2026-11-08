"""User-operated line-4 notice archive. Disappearance is not resolution."""
import argparse
from contextlib import closing
import hashlib
import json
import sqlite3
import time
from urllib.parse import urlencode
from urllib.request import urlopen

from app import ROOT
from collect import LINE, INTERVAL, utc_now

DATABASE = ROOT / 'data' / 'disruptions.sqlite'


def connect(path=DATABASE):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=30)
    db.executescript('''
      CREATE TABLE IF NOT EXISTS checks (
        id INTEGER PRIMARY KEY, started_at REAL NOT NULL, observed_at TEXT NOT NULL,
        gap_seconds REAL NOT NULL, status TEXT NOT NULL, response_json TEXT,
        error_kind TEXT);
      CREATE TABLE IF NOT EXISTS versions (
        id INTEGER PRIMARY KEY, notice_id TEXT NOT NULL, fingerprint TEXT NOT NULL,
        content_json TEXT NOT NULL, UNIQUE(notice_id,fingerprint));
      CREATE TABLE IF NOT EXISTS sightings (
        check_id INTEGER NOT NULL, version_id INTEGER NOT NULL,
        PRIMARY KEY(check_id,version_id));
    ''')
    return db


def fetch(port):
    with urlopen(f'http://127.0.0.1:{port}/api/traffic?'+urlencode({'line':LINE}), timeout=25) as r:
        return json.load(r)


def validate(payload):
    if payload.get('line_id') != LINE or payload.get('timezone') != 'Europe/Paris':
        raise ValueError('Wrong line or timezone')
    if not isinstance(payload.get('reports'), list) or not payload.get('fetched_at'):
        raise ValueError('Incomplete response')
    ids = []
    for report in payload['reports']:
        if not isinstance(report.get('id'), str) or not report['id'] or not isinstance(report.get('text'), str):
            raise ValueError('Missing notice identity or text')
        ids.append(report['id'])
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate notice identifiers')


def collect_check(db, loader, now=None):
    now = time.time() if now is None else now
    db.execute('BEGIN IMMEDIATE')
    try:
        previous = db.execute('SELECT MAX(started_at) FROM checks').fetchone()[0]
        if previous is not None and now - previous < INTERVAL:
            db.rollback()
            return False
        gap = max(0, now - previous - INTERVAL) if previous is not None else 0
        try:
            payload = loader()
            validate(payload)
            status, error = ('ok' if payload['reports'] else 'empty'), None
        except Exception as exc:
            payload, status, error = None, 'error', type(exc).__name__
        check = db.execute('''INSERT INTO checks(started_at,observed_at,gap_seconds,status,
                            response_json,error_kind) VALUES(?,?,?,?,?,?)''',
                           (now, utc_now(), gap, status,
                            json.dumps(payload, ensure_ascii=False) if payload is not None else None, error)).lastrowid
        for report in payload['reports'] if payload is not None else []:
            content = json.dumps(report, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
            fingerprint = hashlib.sha256(content.encode('utf-8')).hexdigest()
            db.execute('INSERT OR IGNORE INTO versions(notice_id,fingerprint,content_json) VALUES(?,?,?)',
                       (report['id'], fingerprint, content))
            version = db.execute('SELECT id FROM versions WHERE notice_id=? AND fingerprint=?',
                                 (report['id'], fingerprint)).fetchone()[0]
            db.execute('INSERT INTO sightings VALUES(?,?)', (check, version))
        db.commit()
        return True
    except BaseException:
        db.rollback()
        raise


def summary(db):
    return {'checks_by_status':dict(db.execute('SELECT status,COUNT(*) FROM checks GROUP BY status')),
            'notice_ids':db.execute('SELECT COUNT(DISTINCT notice_id) FROM versions').fetchone()[0],
            'content_versions':db.execute('SELECT COUNT(*) FROM versions').fetchone()[0],
            'excess_seconds_between_checks':round(db.execute('SELECT COALESCE(SUM(gap_seconds),0) FROM checks').fetchone()[0]),
            'meaning':'Observed publications, not confirmed incident starts or ends.'}


def history(db, search=''):
    rows = db.execute('''SELECT v.notice_id,v.fingerprint,v.content_json,
                        MIN(c.observed_at),MAX(c.observed_at),COUNT(*)
                        FROM versions v JOIN sightings s ON s.version_id=v.id
                        JOIN checks c ON c.id=s.check_id GROUP BY v.id ORDER BY MIN(c.started_at),v.id''')
    return [{'notice_id':identity,'version':fingerprint,'first_collected_at':first,
             'last_collected_at':last,'sample_count':count,'report':json.loads(content)}
            for identity,fingerprint,content,first,last,count in rows
            if search.casefold() in (identity+' '+json.loads(content)['text']).casefold()]


def saved_history(path=DATABASE, search=''):
    if not path.exists():
        return {'available':False,'versions':[],'summary':{},'latest_check':None}
    with closing(sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True,timeout=5)) as db:
        db.execute('BEGIN')  # One consistent snapshot while the collector may write.
        rows=history(db,search)
        latest=db.execute('SELECT observed_at,status FROM checks ORDER BY id DESC LIMIT 1').fetchone()
        return {'available':True,'versions':rows[-200:][::-1], 'matched_versions':len(rows),
                'summary':summary(db),'latest_check':dict(zip(('observed_at','status'),latest)) if latest else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--once',action='store_true')
    parser.add_argument('--report',action='store_true',help='Saved collection-quality summary; no API calls')
    parser.add_argument('--history',action='store_true',help='Show saved versions; no API calls')
    parser.add_argument('--search',default='',help='Filter saved notice IDs or message text; implies --history')
    parser.add_argument('--port',type=int,default=8765)
    args=parser.parse_args()
    with closing(connect()) as db:
        if args.history or args.search:
            print(json.dumps(history(db,args.search),ensure_ascii=True,indent=2))
            return
        if args.report:
            print(json.dumps(summary(db),indent=2))
            return
        print('Line 4 notice history: every five minutes while this window stays open.\n'
              'Keep the local explorer running. Ctrl+C stops; completed checks are saved.',flush=True)
        try:
            while True:
                saved=collect_check(db,lambda:fetch(args.port))
                print(json.dumps(summary(db)) if saved else 'Recent check already saved; skipped.',flush=True)
                if args.once:
                    break
                time.sleep(INTERVAL)
        except KeyboardInterrupt:
            print('\nNotice collector stopped.')


if __name__ == '__main__':
    main()
