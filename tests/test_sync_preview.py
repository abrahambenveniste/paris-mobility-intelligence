from contextlib import closing
from pathlib import Path
import tempfile
import unittest

from disruption_history import connect, collect_check, LINE
from sync_preview import prepare_batch

ARCHIVE='12345678-1234-4234-8234-123456789abc'


def response(text='Synthetic notice'):
    return {'line_id':LINE,'timezone':'Europe/Paris','fetched_at':'2026-11-09T12:00:00Z',
            'cached':False,'excluded_unlinked':2,'reports':[{'id':'test', 'text':text}]}


class SyncPreviewTests(unittest.TestCase):
    def test_batched_replay_preserves_changed_versions_and_empty_checks(self):
        with tempfile.TemporaryDirectory() as folder, closing(connect(Path(folder)/'db')) as db:
            collect_check(db,response,now=1000)
            collect_check(db,lambda:response('Changed'),now=1300)
            collect_check(db,lambda:{**response(),'reports':[]},now=1600)
            first=prepare_batch(db,ARCHIVE,0,2)
            self.assertEqual([c['check_id'] for c in first['checks']],[1,2])
            self.assertNotEqual(first['checks'][0]['notices'][0]['fingerprint'],first['checks'][1]['notices'][0]['fingerprint'])
            self.assertEqual(first['checks'][0]['excluded_unlinked'],2)
            self.assertEqual(prepare_batch(db,ARCHIVE,0,2),first)
            second=prepare_batch(db,ARCHIVE,first['next_check'],2)
            self.assertEqual(second['checks'][0]['status'],'empty')
            self.assertEqual(second['checks'][0]['notices'],[])
            self.assertEqual(prepare_batch(db,ARCHIVE,3)['checks'],[])

    def test_failed_check_is_not_empty_and_invalid_input_rejected(self):
        with tempfile.TemporaryDirectory() as folder, closing(connect(Path(folder)/'db')) as db:
            def fail(): raise RuntimeError('secret')
            collect_check(db,fail,now=1000)
            item=prepare_batch(db,ARCHIVE)['checks'][0]
            self.assertEqual((item['status'],item['error_kind']),('error','RuntimeError'))
            self.assertNotIn('secret',str(item))
            with self.assertRaises(ValueError): prepare_batch(db,'invalid')
            with self.assertRaises(ValueError): prepare_batch(db,ARCHIVE,limit=101)

    def test_inconsistent_check_is_rejected_without_advancing(self):
        with tempfile.TemporaryDirectory() as folder, closing(connect(Path(folder)/'db')) as db:
            collect_check(db,response,now=1000)
            db.execute('DELETE FROM sightings'); db.commit()
            with self.assertRaises(ValueError): prepare_batch(db,ARCHIVE)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM checks').fetchone()[0],1)
