"""Upload normalized checks privately; no schedule and no public-read access."""
import argparse
from contextlib import closing
import json
import os
import sqlite3

from disruption_history import DATABASE
from sync_preview import prepare_batch

INSERT = '''INSERT INTO pmi_private.notice_checks
    (archive_id,check_id,line_id,started_at,observed_at,gap_seconds,status,
     fetched_at,cached,excluded_unlinked,error_kind,notices)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
    ON CONFLICT (archive_id,check_id) DO NOTHING RETURNING check_id'''

MATCH = '''SELECT (line_id,started_at,observed_at,gap_seconds,status,
    fetched_at,cached,excluded_unlinked,error_kind,notices)
    IS NOT DISTINCT FROM (%s,%s,%s::timestamptz,%s,%s,%s::timestamptz,%s,%s,%s,%s::jsonb)
    FROM pmi_private.notice_checks WHERE archive_id=%s AND check_id=%s'''


def write_batch(connection, batch):
    """Insert a whole batch atomically; a changed duplicate aborts everything."""
    inserted = repeated = 0
    with connection.transaction():
        for item in batch['checks']:
            notices=json.dumps(item['notices'],sort_keys=True,ensure_ascii=False,separators=(',',':'))
            content=(item['line_id'],item['started_at'],item['observed_at'],
                     item['gap_seconds'],item['status'],item['fetched_at'],item['cached'],
                     item['excluded_unlinked'],item['error_kind'],notices)
            identity=(batch['archive_id'],item['check_id'])
            result=connection.execute(INSERT,identity+content).fetchone()
            if result:
                inserted+=1
            else:
                existing=connection.execute(MATCH,content+identity).fetchone()
                if not existing or not existing[0]:
                    raise ValueError('Existing check conflicts with this archive')
                repeated+=1
    return {'inserted':inserted,'repeated':repeated,'next_check':batch['next_check']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--after',type=int,default=0,help='Replay from this local check ID (default: replay all)')
    args=parser.parse_args()
    required=('PMI_DATABASE_URL','PMI_DATABASE_CA','PMI_ARCHIVE_ID')
    if any(not os.environ.get(name) for name in required):
        raise SystemExit('Missing private sync configuration. See docs/public-release.md; no connection made.')
    if not DATABASE.exists():
        raise SystemExit('No local archive exists. No connection made.')
    try:
        import psycopg
    except ImportError:
        raise SystemExit('Install the optional hosting dependency first; no connection made.') from None
    try:
        with closing(sqlite3.connect(DATABASE.resolve().as_uri()+'?mode=ro',uri=True)) as source:
            cursor=args.after
            batch=prepare_batch(source,os.environ['PMI_ARCHIVE_ID'],cursor)
            if not batch['checks']:
                print('No local checks to synchronize. No connection made.')
                return
            with psycopg.connect(os.environ['PMI_DATABASE_URL'],sslmode='verify-full',
                                 sslrootcert=os.environ['PMI_DATABASE_CA'],connect_timeout=10,
                                 prepare_threshold=None) as destination:
                while batch['checks']:
                    result=write_batch(destination,batch)
                    cursor=result['next_check']  # Only after the transaction commits.
                    print(json.dumps(result),flush=True)
                    batch=prepare_batch(source,os.environ['PMI_ARCHIVE_ID'],cursor)
        print('Private sync complete. No public website has been published.')
    except Exception as error:
        # Exception strings may contain secret connection details; never display them.
        raise SystemExit(f'Private sync failed ({type(error).__name__}); inspect configuration and retry.') from None


if __name__ == '__main__':
    main()
