"""Prepare deterministic local notice batches; this module sends no data."""
import argparse
from contextlib import closing
import hashlib
import json
import sqlite3
from uuid import UUID

from disruption_history import DATABASE


def prepare_batch(db, archive_id, after_check=0, limit=100):
    """Return normalized checks and sightings for a future idempotent sync."""
    archive_id = str(UUID(archive_id))
    if after_check < 0 or not 1 <= limit <= 100:
        raise ValueError('Invalid cursor or batch size')
    db.execute('BEGIN')  # All records in the batch come from the same snapshot.
    try:
        checks = db.execute('''SELECT id,line_id,started_at,observed_at,gap_seconds,
                            status,response_json,error_kind FROM checks
                            WHERE id>? ORDER BY id LIMIT ?''', (after_check, limit)).fetchall()
        batch = []
        for check_id,line,started,observed,gap,status,response,error in checks:
            if status not in ('ok','empty','error'):
                raise ValueError('Unexpected check status')
            payload = json.loads(response) if response else None
            if (status == 'error') != (payload is None):
                raise ValueError('Response does not match check status')
            rows = db.execute('''SELECT v.notice_id,v.fingerprint,v.content_json
                                 FROM sightings s JOIN versions v ON v.id=s.version_id
                                 WHERE s.check_id=? ORDER BY v.notice_id,v.fingerprint''', (check_id,)).fetchall()
            if status == 'empty' and rows or status == 'error' and rows:
                raise ValueError('Unexpected sightings for an empty or failed check')
            notices = [{'notice_id':nid,'fingerprint':fp,'content':json.loads(content)}
                       for nid,fp,content in rows]
            if payload is not None:
                reports = payload.get('reports')
                if payload.get('line_id') != line or not isinstance(reports, list):
                    raise ValueError('Response line or reports are invalid')
                expected = []
                for report in reports:
                    canonical=json.dumps(report,sort_keys=True,ensure_ascii=False,separators=(',',':'))
                    expected.append((report['id'],hashlib.sha256(canonical.encode('utf-8')).hexdigest()))
                if sorted(expected) != [(notice['notice_id'],notice['fingerprint']) for notice in notices]:
                    raise ValueError('Response and saved sightings disagree')
                if (status == 'ok') != bool(notices):
                    raise ValueError('Check status does not match its notices')
            batch.append({'check_id':check_id,'line_id':line,'started_at':started,
                          'observed_at':observed,'gap_seconds':gap,'status':status,
                          'fetched_at':payload.get('fetched_at') if payload else None,
                          'cached':payload.get('cached') if payload else None,
                          'excluded_unlinked':payload.get('excluded_unlinked') if payload else None,
                          'error_kind':error,'notices':notices})
        return {'archive_id':archive_id,'after_check':after_check,
                'next_check':checks[-1][0] if checks else after_check,'checks':batch}
    finally:
        db.rollback()  # Read-only transaction; no checkpoint is advanced here.


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive-id',required=True,help='UUID identifying the local archive')
    parser.add_argument('--after',type=int,default=0)
    args=parser.parse_args()
    if not DATABASE.exists():
        raise SystemExit('No local notice archive exists yet; run the notice collector first.')
    with closing(sqlite3.connect(DATABASE.resolve().as_uri()+'?mode=ro',uri=True)) as db:
        batch=prepare_batch(db,args.archive_id,args.after)
    # Do not print notice content: the online publishing terms are still being reviewed.
    print(json.dumps({'checks':len(batch['checks']),'next_check':batch['next_check'],
                      'notice_sightings':sum(len(check['notices']) for check in batch['checks']),
                      'sent':False,'note':'Local preview only; no data transferred.'}))


if __name__ == '__main__':
    main()
