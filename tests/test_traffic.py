"""Synthetic cases: never use live traffic reports as stable test fixtures."""
import copy
from datetime import datetime, timezone
import unittest
from traffic import normalize_reports

LINE = 'STIF:Line::C01384:'
TARGET = 'line:IDFM:C01384'
NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def sample():
    return {'context': {'timezone': 'Europe/Paris', 'current_datetime': '20260101T010000'},
            'pagination': {'start_page': 0, 'total_result': 1, 'items_on_page': 1},
            'line_reports': [{'line': {'id': TARGET, 'links': [{'type': 'disruption', 'id': 'demo'}]}}],
            'disruptions': [{'id': 'demo', 'status': 'active',
                             'messages': [{'text': '<p>Example <b>stop</b> closed.</p>', 'channel': {'types': ['web']}}],
                             'updated_at': '20260101T005900',
                             'application_periods': [{'begin': '20260101T010000', 'end': '20260101T030000'}],
                             'severity': {'effect': 'NO_SERVICE'}}]}


class TrafficTests(unittest.TestCase):
    def test_direct_link_and_plain_text(self):
        result = normalize_reports(sample(), LINE, NOW)
        self.assertEqual(result['reports'][0]['text'], 'Example stop closed.')
        self.assertEqual(result['reports'][0]['periods_local'][0]['begin'], '2026-01-01T01:00:00')
        self.assertEqual(result['timezone'], 'Europe/Paris')

    def test_related_station_report_is_not_line_interruption(self):
        payload = sample()
        related = copy.deepcopy(payload['disruptions'][0]); related['id'] = 'station-only'
        related['impacted_objects'] = [{'pt_object': {'id': 'stop_area:IDFM:DEMO'}}]
        payload['disruptions'].append(related)
        result = normalize_reports(payload, LINE, NOW)
        self.assertEqual(len(result['reports']), 1)
        self.assertEqual(result['excluded_unlinked'], 1)

    def test_direct_impacted_object_and_duplicate(self):
        payload = sample(); payload['line_reports'][0]['line']['links'] = []
        payload['disruptions'][0]['impacted_objects'] = [{'pt_object': {'id': TARGET}}]
        payload['disruptions'].append(copy.deepcopy(payload['disruptions'][0]))
        self.assertEqual(len(normalize_reports(payload, LINE, NOW)['reports']), 1)

    def test_incomplete_page_is_error_not_empty(self):
        payload = sample(); payload['pagination']['total_result'] = 2
        with self.assertRaises(ValueError): normalize_reports(payload, LINE, NOW)

    def test_missing_linked_report_is_error(self):
        payload = sample(); payload['disruptions'] = []
        with self.assertRaises(ValueError): normalize_reports(payload, LINE, NOW)

    def test_wrong_line_or_timezone_is_error(self):
        for key, value in [('line', 'line:IDFM:OTHER'), ('timezone', 'UTC')]:
            payload = sample()
            if key == 'line': payload['line_reports'][0]['line']['id'] = value
            else: payload['context']['timezone'] = value
            with self.assertRaises(ValueError): normalize_reports(payload, LINE, NOW)

    def test_empty_success_and_invalid_date(self):
        payload = sample(); payload['line_reports'][0]['line']['links'] = []; payload['disruptions'] = []
        self.assertEqual(normalize_reports(payload, LINE, NOW)['reports'], [])
        payload = sample(); payload['disruptions'][0]['updated_at'] = 'bad-date'
        with self.assertRaises(ValueError): normalize_reports(payload, LINE, NOW)
