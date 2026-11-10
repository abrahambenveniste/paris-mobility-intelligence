import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1] / "src"))
from contextlib import closing
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
import run_platform
from disruption_history import connect


class PlatformTests(unittest.TestCase):
    def test_existing_server_is_reused_and_owned_collectors_stop(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'db'
            children=[Mock(),Mock()]
            for child in children:
                child.poll.return_value=None
            with patch('sys.argv',['run_platform.py','--with-predictions']), \
                 patch('disruption_history.connect',side_effect=lambda:connect(path)), \
                 patch.object(run_platform,'ready',return_value=True), \
                 patch.object(run_platform.subprocess,'Popen',side_effect=children) as launch, \
                 patch.object(run_platform.webbrowser,'open'), \
                 patch.object(run_platform.time,'sleep',side_effect=KeyboardInterrupt):
                run_platform.main()
            self.assertEqual(launch.call_count,2)
            self.assertTrue(launch.call_args_list[0].args[0][1].endswith('disruption_history.py'))
            for child in children:
                child.terminate.assert_called_once()
                child.wait.assert_called_once()
