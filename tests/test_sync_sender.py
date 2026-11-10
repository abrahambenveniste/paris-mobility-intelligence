import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1] / "src"))
from contextlib import contextmanager
from contextlib import closing
import io
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch, Mock
from disruption_history import connect, collect_check, LINE
import sync_sender
from sync_sender import write_batch


class FakeResult:
    def __init__(self, value): self.value=value
    def fetchone(self): return self.value


class FakeConnection:
    def __init__(self, existing=None):
        self.rows=dict(existing or {})
        self.match_calls=0

    def __enter__(self): return self
    def __exit__(self, *args): return False

    @contextmanager
    def transaction(self):
        before=dict(self.rows)
        try: yield
        except BaseException:
            self.rows=before
            raise

    def execute(self, sql, args):
        if sql.startswith('INSERT'):
            identity=args[:2]
            if identity in self.rows: return FakeResult(None)
            self.rows[identity]=args[2:]
            return FakeResult((identity[1],))
        self.match_calls+=1
        return FakeResult((self.rows.get(args[-2:]) == args[:-2],))


def item(number, status='empty'):
    return {'check_id':number,'line_id':'line','started_at':number,
            'observed_at':'2026-11-09T12:00:00+00:00','gap_seconds':0,
            'status':status,'fetched_at':'2026-11-09T12:00:00+00:00',
            'cached':False,'excluded_unlinked':0,'error_kind':None,'notices':[]}


class SyncSenderTests(unittest.TestCase):
    def test_cli_enforces_verified_tls_and_does_not_print_secrets(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'db'
            with closing(connect(path)) as db:
                collect_check(db,lambda:{'line_id':LINE,'timezone':'Europe/Paris',
                    'fetched_at':'2026-11-09T12:00:00Z','cached':False,'reports':[]},now=1000)
            destination=FakeConnection()
            fake_connect=Mock(return_value=destination)
            env={'PMI_DATABASE_URL':'synthetic-secret','PMI_DATABASE_CA':'test-ca',
                 'PMI_ARCHIVE_ID':'12345678-1234-4234-8234-123456789abc'}
            output=io.StringIO()
            with patch.dict('sys.modules',{'psycopg':types.SimpleNamespace(connect=fake_connect)}), \
                 patch.dict('os.environ',env,clear=True), patch('sys.argv',['sync_sender.py']), \
                 patch.object(sync_sender,'DATABASE',path), patch('sys.stdout',output):
                sync_sender.main()
            self.assertEqual(fake_connect.call_args.kwargs['sslmode'],'verify-full')
            self.assertEqual(fake_connect.call_args.kwargs['sslrootcert'],'test-ca')
            self.assertEqual(len(destination.rows),1)
            self.assertNotIn('synthetic-secret',output.getvalue())

    def test_retry_is_idempotent(self):
        batch={'archive_id':'archive','checks':[item(1),item(2)],'next_check':2}
        connection=FakeConnection()
        self.assertEqual(write_batch(connection,batch),{'inserted':2,'repeated':0,'next_check':2})
        self.assertEqual(write_batch(connection,batch),{'inserted':0,'repeated':2,'next_check':2})
        self.assertEqual(len(connection.rows),2)

    def test_changed_duplicate_rolls_back_new_rows(self):
        original={'archive_id':'archive','checks':[item(2)],'next_check':2}
        connection=FakeConnection();write_batch(connection,original)
        changed=item(2);changed['line_id']='different'
        with self.assertRaises(ValueError):
            write_batch(connection,{'archive_id':'archive','checks':[item(1),changed],'next_check':2})
        self.assertNotIn(('archive',1),connection.rows)
        self.assertEqual(len(connection.rows),1)
