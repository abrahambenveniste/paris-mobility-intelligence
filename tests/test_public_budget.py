import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1] / "src"))
import unittest
from public_budget import PublicBudget


class Cursor:
    def __init__(self, used=0, recent=0):
        self.used, self.recent, self.commands = used, recent, []
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def execute(self, sql, args=None): self.commands.append(sql)
    def fetchone(self): return self.used, self.recent


class Connection:
    def __init__(self, cursor): self.cur = cursor
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def cursor(self): return self.cur


class BudgetTests(unittest.TestCase):
    def test_reserves_before_request_and_caches(self):
        cursor = Cursor()
        budget = PublicBudget(lambda: Connection(cursor))
        def loader():
            self.assertTrue(any('INSERT' in sql for sql in cursor.commands))
            return {'reports': []}
        first = budget.get(('traffic', 'line'), loader)
        second = budget.get(('traffic', 'line'), lambda: self.fail('cache missed'))
        self.assertFalse(first['cached'])
        self.assertTrue(second['cached'])

    def test_limit_and_database_failure_do_not_call_provider(self):
        for connect in (lambda: Connection(Cursor(used=100)), lambda: (_ for _ in ()).throw(OSError('offline'))):
            with self.assertRaises((RuntimeError, OSError)):
                PublicBudget(connect).get(('traffic', 'line'), lambda: self.fail('provider called'))
