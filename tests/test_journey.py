import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1] / "src"))
import unittest
from unittest.mock import patch
from journey import normalize_journeys, safe_geometry
from public_live import PublicLive


def section(line='line:IDFM:C2', mode='Métro'):
    return {'type': 'public_transport', 'from': {'name': 'A'}, 'to': {'name': 'B'},
            'display_informations': {'commercial_mode': mode, 'code': '2', 'direction': 'B'},
            'links': [{'type': 'line', 'id': line}], 'data_freshness': 'base_schedule'}


class Budget:
    def get(self, identifier, loader):
        return loader()


class JourneyTests(unittest.TestCase):
    def test_publisher_geometry_is_bounded_and_optional(self):
        line = {'type': 'LineString', 'coordinates': [[2.3, 48.8], [2.4, 48.9]]}
        self.assertEqual(safe_geometry(line), line)
        self.assertIsNone(safe_geometry({'type': 'LineString', 'coordinates': [[2.3, 48.8], [50, 50]]}))
        self.assertIsNone(safe_geometry({'type': 'Point', 'coordinates': [2.3, 48.8]}))
        self.assertIsNone(safe_geometry(None))
    def test_preserves_legs_and_freshness(self):
        payload = {'journeys': [{'duration': 600, 'sections': [section()]}]}
        result = normalize_journeys(payload, 'line:IDFM:C1')
        self.assertEqual(result['journeys'][0]['sections'][0]['freshness'], 'base_schedule')
        self.assertEqual(result['journeys'][0]['sections'][0]['line'], '2')
        self.assertEqual(result['journeys'][0]['sections'][0]['line_id'], 'line:IDFM:C2')

    def test_rejects_avoided_line_and_other_modes(self):
        for leg in (section('line:IDFM:C1'), section(mode='Bus')):
            with self.assertRaises(ValueError):
                normalize_journeys({'journeys': [{'duration': 600, 'sections': [leg]}]}, 'line:IDFM:C1')

    def test_validates_station_and_line_before_provider_call(self):
        network = {'routes': [{'id': 'STIF:Line::C1:'}], 'stops': [
            {'id': 'IDFM:1', 'line_id': 'STIF:Line::C1:', 'lat': 48.8, 'lon': 2.3},
            {'id': 'IDFM:2', 'line_id': 'STIF:Line::C1:', 'lat': 48.9, 'lon': 2.4}]}
        live = PublicLive(network, 'test-key', Budget())
        with patch('public_live.fetch_journeys', return_value={'journeys': []}) as fetch:
            a, b = 'IDFM:1|STIF:Line::C1:', 'IDFM:2|STIF:Line::C1:'
            for args in [(a, a, ''), ('-1', b, ''), (a, 'unknown', ''), (a, b, 'unknown')]:
                with self.assertRaises(ValueError): live.journeys(*args)
            fetch.assert_not_called()
            self.assertEqual(live.journeys(a, b, 'STIF:Line::C1:'), {'journeys': []})
            fetch.assert_called_once()
