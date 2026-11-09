"""Small offline tests: synthetic responses only, no API calls or real credentials."""
from datetime import datetime, timezone
import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from http.server import ThreadingHTTPServer
from app import RequestCache, handler_class, normalize_departures, timestamp, read_keys
from prepare_data import build_network, metro_codes, line_query

LINE = 'STIF:Line::C01374:'
STOP = 'STIF:StopPoint:Q:1:'
NOW = datetime(2026, 11, 5, 12, tzinfo=timezone.utc)


class SecretConfigurationTests(unittest.TestCase):
    def test_host_environment_overrides_local_file_without_exposing_other_variables(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / '.env'
            path.write_text('PRIM_API_KEY=local\nPRIM_STATIC_TOKEN=local-static\n', encoding='utf-8')
            with patch.dict('os.environ', {'PRIM_API_KEY':'hosted', 'UNRELATED_SECRET':'private'}, clear=True):
                keys = read_keys(path)
            self.assertEqual(keys['PRIM_API_KEY'],'hosted')
            self.assertEqual(keys['PRIM_STATIC_TOKEN'],'local-static')
            self.assertNotIn('UNRELATED_SECRET',keys)

    def test_missing_file_uses_environment(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict('os.environ', {'PRIM_STATIC_TOKEN':'hosted-static'}, clear=True):
            self.assertEqual(read_keys(Path(directory)/'missing'), {'PRIM_STATIC_TOKEN':'hosted-static'})


def visit(line=LINE, expected='2026-11-05T12:05:00Z', **call_fields):
    return {'RecordedAtTime': '2026-11-05T11:58:00Z', 'MonitoredVehicleJourney': {
        'LineRef': {'value': line}, 'DestinationName': [{'value': 'Test destination'}],
        'MonitoredCall': {'ExpectedDepartureTime': expected, **call_fields}}}


def payload(*visits, status='true'):
    return {'Siri': {'ServiceDelivery': {'ResponseTimestamp': NOW.isoformat(),
            'StopMonitoringDelivery': [{'Status': status, 'MonitoredStopVisit': list(visits)}]}}}


class DepartureTests(unittest.TestCase):
    def test_filters_other_lines(self):
        result = normalize_departures(payload(visit(), visit(line='other')), LINE, NOW)
        self.assertEqual(len(result['departures']), 1)
        self.assertNotIn('actual_arrival', result['departures'][0])

    def test_past_and_invalid_times_are_not_presented_as_arrivals(self):
        result = normalize_departures(payload(visit(expected='2026-11-05T11:59:00Z'), visit(expected='invalid')), LINE, NOW)
        self.assertEqual(result['departures'], [])
        self.assertEqual((result['excluded_past'], result['excluded_invalid']), (1, 1))

    def test_naive_timestamp_rejected(self):
        self.assertIsNone(timestamp('2026-11-05T12:00:00'))

    def test_reported_cancellation_without_time_is_retained(self):
        result = normalize_departures(payload(visit(expected=None, DepartureStatus='cancelled')), LINE, NOW)
        self.assertTrue(result['departures'][0]['cancelled'])

    def test_false_service_status_is_not_empty_service(self):
        with self.assertRaises(ValueError):
            normalize_departures(payload(status='false'), LINE, NOW)

    def test_duplicate_item_and_arrival_fallback(self):
        row = visit(expected=None, ExpectedArrivalTime='2026-11-05T12:05:00Z')
        row['ItemIdentifier'] = 'same'
        result = normalize_departures(payload(row, row), LINE, NOW)
        self.assertEqual(len(result['departures']), 1)
        self.assertEqual(result['departures'][0]['kind'], 'arrival')


class CacheTests(unittest.TestCase):
    def test_cache_and_persistent_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'budget.json'
            cache = RequestCache(path, limit=1)
            calls = []
            def loader():
                calls.append(1)
                return {'departures': []}
            self.assertFalse(cache.get('a', loader)['cached'])
            self.assertTrue(cache.get('a', loader)['cached'])
            self.assertEqual(len(calls), 1)
            with self.assertRaises(RuntimeError):
                RequestCache(path, limit=1).get('b', loader)

    def test_failed_calls_consume_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = RequestCache(Path(directory) / 'budget.json', limit=1)
            def failure():
                raise ValueError('failure')
            with self.assertRaises(ValueError):
                cache.get('a', failure)
            with self.assertRaises(RuntimeError):
                cache.get('a', lambda: {})


class NetworkTests(unittest.TestCase):
    def test_metro_selection_excludes_bus_and_duplicates(self):
        _, routes = self.examples()
        self.assertEqual(metro_codes(routes), ['C01374', 'C01384'])
        routes[1]['route_type'] = 'Bus'
        with self.assertRaises(ValueError): metro_codes(routes)
        with self.assertRaises(ValueError): metro_codes([routes[0], routes[0]])
        with self.assertRaises(ValueError): metro_codes([])

    def test_bis_labels_and_numeric_sort(self):
        stops, routes = self.examples()
        routes[0]['route_short_name'] = '14'
        routes[1]['route_short_name'] = '3B'
        result = build_network(stops, routes, [], [])
        self.assertEqual([r['name'] for r in result['routes']], ['3bis', '14'])
        self.assertEqual(result['routes'][0]['source_name'], '3B')
        self.assertEqual(result['scope'], 'metro')
        self.assertTrue(all(r['mode'] == 'Métro' for r in result['routes']))

    def test_queries_use_complete_identifiers(self):
        self.assertEqual(line_query('line', ['C01374', 'C01384'], 'STIF:Line::', ':'),
                         'line in ("STIF:Line::C01374:","STIF:Line::C01384:")')

    def test_each_route_requires_stops(self):
        stops, routes = self.examples()
        with self.assertRaises(ValueError): build_network(stops[:1], routes, [], [])

    def examples(self):
        stops, routes = [], []
        for i, code in enumerate(('C01374', 'C01384')):
            stops.append({'id': 'IDFM:' + code, 'stop_id': f'IDFM:{i+1}', 'stop_lat': '48.85', 'stop_lon': '2.35', 'stop_name': 'Example'})
            routes.append({'route_id': 'IDFM:' + code, 'route_short_name': str(i+1), 'route_type': 'Subway', 'route_color': '123456',
                           'shape': {'geometry': {'type': 'LineString', 'coordinates': [[2.35,48.85],[2.36,48.86]]}}})
        return stops, routes

    def test_unknown_coverage_point_not_guessed(self):
        stops, routes = self.examples()
        network = build_network(stops, routes, [{'line': LINE, 'ns2_stoppointref': 'STIF:StopPoint:Q:999:', 'ns2_stopname': 'Unknown'}], [])
        self.assertEqual(len(network['unmapped']), 1)
        self.assertFalse(any(s['live_supported'] for s in network['stops']))

    def test_projected_coordinates_rejected(self):
        stops, routes = self.examples()
        stops[0]['stop_lat'] = '6863737'
        with self.assertRaises(ValueError):
            build_network(stops, routes, [], [])


class HTTPTests(unittest.TestCase):
    def test_secret_paths_and_bad_stop_never_reach_provider(self):
        with tempfile.TemporaryDirectory() as directory:
            network = {'stops': [{'line_id': LINE, 'monitoring_ref': STOP, 'live_supported': True}]}
            server = ThreadingHTTPServer(('127.0.0.1', 0), handler_class(network, 'synthetic-secret', RequestCache(Path(directory) / 'budget.json')))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                with patch('app.fetch_departures') as upstream:
                    for path, expected in [('/.env',404),('/data/pilot-network.json',404),('/api/departures?line=bad&stop=bad',400),('/api/traffic?line=STIF:Line::C01083:',400),('/api/network',200)]:
                        connection = http.client.HTTPConnection('127.0.0.1', server.server_port)
                        connection.request('GET', path)
                        response = connection.getresponse()
                        self.assertEqual(response.status, expected)
                        self.assertNotIn(b'synthetic-secret', response.read())
                        connection.close()
                    upstream.assert_not_called()
            finally:
                server.shutdown()
                server.server_close()
                thread.join()


if __name__ == '__main__':
    unittest.main()
