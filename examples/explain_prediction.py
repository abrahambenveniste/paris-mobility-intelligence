"""Print a synthetic input/output example using the app's real transformation.

Run from the project folder: python examples/explain_prediction.py
No network requests, credentials, or real transport observations.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import normalize_departures

line = 'STIF:Line::DEMO:'
reference_time = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
sample = {'Siri': {'ServiceDelivery': {
    'ResponseTimestamp': '2026-01-01T12:00:00Z',
    'StopMonitoringDelivery': [{'Status': True, 'MonitoredStopVisit': [{
        'RecordedAtTime': '2026-01-01T11:59:30Z',
        'MonitoredVehicleJourney': {
            'LineRef': {'value': line},
            'DestinationName': [{'value': 'Example terminus'}],
            'MonitoredCall': {'ExpectedDepartureTime': '2026-01-01T12:05:00Z'}
        }
    }]}]
}}}

print('SYNTHETIC TEACHING INPUT (not a real observation)')
print(json.dumps(sample, indent=2))
print('\nOUTPUT FROM normalize_departures (reference time: 12:00 UTC)')
print(json.dumps(normalize_departures(sample, line, reference_time), indent=2))
