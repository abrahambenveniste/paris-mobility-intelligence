import json
from contextlib import closing
from pathlib import Path
import tempfile
import unittest
from collect import connect, collect_cycle, summary, pilot_points, LINE


class CollectorTests(unittest.TestCase):
    def test_empty_error_restart_and_gap_remain_distinct(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'samples.sqlite'
            points = [{'id':'A'}, {'id':'B'}]
            def loader(point):
                if point['id'] == 'B':
                    raise RuntimeError('secret must not be saved')
                return {'departures': [], 'cached': True, 'fetched_at':'2026-11-08T12:00:00Z'}
            with closing(connect(path)) as db:
                self.assertTrue(collect_cycle(db, points, 'hash', loader, now=1000))
            with closing(connect(path)) as db:
                self.assertFalse(collect_cycle(db, points, 'hash', loader, now=1100))
                self.assertTrue(collect_cycle(db, points, 'hash', loader, now=1900))
                result=summary(db)
                self.assertEqual(result['point_responses'], {'empty':2,'error':2})
                self.assertEqual(result['excess_seconds_between_cycles'],600)
                rows=db.execute('SELECT response_json,error_kind FROM samples').fetchall()
                self.assertNotIn('secret',str(rows))
                self.assertTrue(json.loads(rows[0][0])['cached'])

    def test_interrupted_cycle_rolls_back(self):
        with tempfile.TemporaryDirectory() as folder, closing(connect(Path(folder)/'db')) as db:
            def interrupted(point):
                raise KeyboardInterrupt()
            with self.assertRaises(KeyboardInterrupt):
                collect_cycle(db,[{'id':'A'}],'hash',interrupted,now=1000)
            self.assertEqual(summary(db)['cycles'],0)

    def test_selection_rejects_changed_or_duplicate_reference_points(self):
        point={'line_id':LINE,'name':'Châtelet','commune':'Paris','live_supported':True,'monitoring_ref':'same'}
        with self.assertRaises(ValueError):
            pilot_points({'stops':[point,point]})
        with self.assertRaises(ValueError):
            pilot_points({'stops':[]})
