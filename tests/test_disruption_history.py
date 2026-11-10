import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1] / "src"))
from contextlib import closing
from pathlib import Path
import tempfile
import unittest
from disruption_history import connect, collect_check, summary, history, saved_history, LINE


def payload(text='Synthetic planned works', reports=True):
    return {'line_id':LINE,'timezone':'Europe/Paris','fetched_at':'2026-11-09T12:00:00Z',
            'cached':False,'reports':[{'id':'test-notice','text':text,'status':'future',
            'effect':'REDUCED_SERVICE','updated_at_local':'2026-11-09T12:00:00',
            'periods_local':[]}] if reports else []}


class NoticeHistoryTests(unittest.TestCase):
    def test_lines_have_independent_sampling_and_history(self):
        other='STIF:Line::C01371:'
        with tempfile.TemporaryDirectory() as folder, closing(connect(Path(folder)/'db')) as db:
            collect_check(db,payload,now=1000,line=LINE,interval=1800)
            second=payload(); second['line_id']=other
            self.assertTrue(collect_check(db,lambda:second,now=1000,line=other,interval=1800))
            self.assertFalse(collect_check(db,payload,now=1300,line=LINE,interval=1800))
            self.assertEqual(len(history(db)),2)
            self.assertEqual(history(db,line=other)[0]['line_id'],other)
            self.assertEqual(summary(db,other)['checks_by_status'],{'ok':1})
            self.assertEqual(summary(db,'uncollected')['checks_by_status'],{})

    def test_old_line4_checks_migrate_without_loss(self):
        import sqlite3
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'db'
            with closing(sqlite3.connect(path)) as old:
                old.execute('CREATE TABLE checks(id INTEGER PRIMARY KEY, started_at REAL, observed_at TEXT, gap_seconds REAL, status TEXT, response_json TEXT,error_kind TEXT)')
                old.execute("INSERT INTO checks VALUES(1,1000,'test',0,'empty',NULL,NULL)")
                old.commit()
            with closing(connect(path)) as db:
                self.assertEqual(db.execute('SELECT line_id,status FROM checks').fetchone(),(LINE,'empty'))
            self.assertTrue(path.with_suffix('.before-all-metro.sqlite').exists())

    def test_web_history_is_read_only_and_filters_versions(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'db'
            self.assertFalse(saved_history(path)['available'])
            self.assertFalse(path.exists())
            with closing(connect(path)) as db:
                collect_check(db,payload,now=1000)
                collect_check(db,lambda:payload('Changed message'),now=1300)
            before=path.read_bytes()
            result=saved_history(path,'CHANGED')
            self.assertEqual(result['matched_versions'],1)
            self.assertEqual(result['versions'][0]['report']['text'],'Changed message')
            self.assertEqual(result['summary']['content_versions'],2)
            self.assertEqual(path.read_bytes(),before)

    def test_repeat_change_disappearance_and_reappearance(self):
        with tempfile.TemporaryDirectory() as folder, closing(connect(Path(folder)/'db')) as db:
            for i,p in enumerate([payload(),payload(),payload('Synthetic updated works'),
                                  payload(reports=False),payload()]):
                self.assertTrue(collect_check(db,lambda:p,now=1000+i*300))
            result=summary(db)
            self.assertEqual(result['notice_ids'],1)
            self.assertEqual(result['content_versions'],2)
            self.assertEqual(result['checks_by_status'],{'ok':4,'empty':1})
            self.assertEqual(history(db)[0]['sample_count'],3)
            self.assertEqual(len(history(db,'UPDATED')),1)
            self.assertNotIn('resolved_at',history(db)[0])

    def test_restart_gap_failure_and_wrong_line(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'db'
            with closing(connect(path)) as db:
                collect_check(db,payload,now=1000)
            with closing(connect(path)) as db:
                self.assertFalse(collect_check(db,payload,now=1100))
                def failure():
                    raise RuntimeError('secret')
                collect_check(db,failure,now=1900)
                wrong=payload(); wrong['line_id']='other'
                collect_check(db,lambda:wrong,now=2200)
                self.assertEqual(summary(db)['checks_by_status'],{'ok':1,'error':2})
                self.assertEqual(summary(db)['excess_seconds_between_checks'],600)
                self.assertNotIn('secret',str(db.execute('SELECT * FROM checks').fetchall()))
                self.assertEqual(len(history(db)),1)

    def test_interruption_rolls_back(self):
        with tempfile.TemporaryDirectory() as folder, closing(connect(Path(folder)/'db')) as db:
            def stop():
                raise KeyboardInterrupt()
            with self.assertRaises(KeyboardInterrupt):
                collect_check(db,stop,now=1000)
            self.assertEqual(summary(db)['checks_by_status'],{})
