import http.client
from http.server import ThreadingHTTPServer
import json
import threading
import unittest
from unittest.mock import patch

from public_live import PublicLive
from preview_server import preview_handler


NETWORK = {'routes': [{'id': 'STIF:Line::C1:'}],
           'stops': [{'line_id': 'STIF:Line::C1:', 'id': 'IDFM:123'}]}


class Budget:
    def __init__(self):
        self.calls = 0

    def get(self, identifier, loader):
        self.calls += 1
        return loader()


class PublicLiveTests(unittest.TestCase):
    def test_whitelist_and_unconfigured_fail_closed(self):
        budget = Budget()
        live = PublicLive(NETWORK, 'example-key', budget)
        with self.assertRaises(ValueError):
            live.lookup('departures', 'STIF:Line::C1:', 'unpublished')
        self.assertEqual(budget.calls, 0)
        with self.assertRaises(RuntimeError):
            PublicLive(NETWORK, 'example-key', None).lookup('traffic', 'STIF:Line::C1:')
        with patch('public_live.fetch_departures', return_value={'departures': []}) as fetch:
            result = live.lookup('departures', 'STIF:Line::C1:', 'STIF:StopPoint:Q:123:')
        self.assertEqual(result, {'departures': []})
        self.assertEqual(budget.calls, 1)
        fetch.assert_called_once()

    def test_upstream_errors_do_not_leak_secrets(self):
        live = PublicLive(NETWORK, 'example-key', Budget())
        server = ThreadingHTTPServer(('127.0.0.1', 0), preview_handler(NETWORK, live))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with patch('public_live.fetch_reports', side_effect=Exception('secret example-key')):
                connection = http.client.HTTPConnection('127.0.0.1', server.server_port)
                connection.request('GET', '/api/traffic?line=STIF%3ALine%3A%3AC1%3A')
                response = connection.getresponse()
                body = response.read()
                self.assertEqual(response.status, 502)
                self.assertNotIn(b'example-key', body)
                self.assertIn('error', json.loads(body))
                connection.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
