"""Offline M0 checks of ignored local samples; no network access or credentials.

Run from the repository root: python audit/check_samples.py
This checks a bounded sample, not the complete regional feed.
"""
import collections
import csv
import datetime as dt
import hashlib
import io
import itertools
import json
from pathlib import Path
import re
import zlib

ROOT = Path('artifacts/m0')
REPORT = {'checks': [], 'scope': 'One snapshot per stop; 5000 stop-time rows; partial ZIP'}


def load(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))


def check(name, condition, detail):
    REPORT['checks'].append({'name': name, 'passed': bool(condition), 'detail': detail})


INDEX = {entry['name']: entry for entry in load('partial-zip-index.json')}


def table(name, sample=False):
    entry = INDEX[name]
    if not entry['complete'] or entry['method'] != 8:
        raise ValueError('Required member unavailable or unsupported: ' + name)
    with (ROOT / 'gtfs.zip').open('rb') as handle:
        handle.seek(entry['offset'])
        if sample:
            # Bound decompression as well as input; complete CSV lines only.
            decoder = zlib.decompressobj(-15)
            data = decoder.decompress(handle.read(min(entry['compressed'], 2_000_000)), 2_000_000)
            data = data[:data.rfind(b'\n') + 1]
        else:
            data = zlib.decompress(handle.read(entry['compressed']), -15)
            check(name + ': CRC and length', zlib.crc32(data) == entry['crc'] and len(data) == entry['uncompressed'], len(data))
    return csv.DictReader(io.StringIO(data.decode('utf-8-sig')))


def seconds(value):
    if not value:
        return None
    if not re.fullmatch(r'\d+:\d{2}:\d{2}', value):
        raise ValueError('Invalid GTFS time')
    h, m, s = map(int, value.split(':'))
    if m > 59 or s > 59:
        raise ValueError('Invalid GTFS time')
    return h * 3600 + m * 60 + s


routes = list(table('routes.txt'))
stops = list(table('stops.txt'))
cal = list(table('calendar.txt'))
exceptions = list(table('calendar_dates.txt'))
route_ids = {r['route_id'] for r in routes}
stop_ids = {r['stop_id'] for r in stops}
service_ids = {r['service_id'] for r in cal + exceptions}
check('unique nonempty route IDs', len(route_ids) == len(routes) and '' not in route_ids, len(routes))
check('unique nonempty stop IDs', len(stop_ids) == len(stops) and '' not in stop_ids, len(stops))
bad_coords = 0
for row in stops:
    try:
        if row.get('stop_lat') and row.get('stop_lon'):
            bad_coords += not (-90 <= float(row['stop_lat']) <= 90 and -180 <= float(row['stop_lon']) <= 180)
    except ValueError:
        bad_coords += 1
check('provided GTFS coordinates in valid degree ranges', bad_coords == 0, bad_coords)
times = list(itertools.islice(table('stop_times.txt', sample=True), 5000))
check('stop-time sample reached planned size', len(times) == 5000, len(times))
needed = {r['trip_id'] for r in times}
missing_trips = set(needed)
bad_route = bad_service = trip_count = 0
pilot_trips = collections.Counter()
pilot_examples = {}
sample_trip_routes = {}
service_day = '20261105'
active_services = {r['service_id'] for r in cal if r['start_date'] <= service_day <= r['end_date'] and r['thursday'] == '1'}
for row in exceptions:
    if row['date'] == service_day:
        if row['exception_type'] == '1':
            active_services.add(row['service_id'])
        elif row['exception_type'] == '2':
            active_services.discard(row['service_id'])
pilot_active_trips = collections.Counter()
live_ids = set()
for meta in load('live-manifest.json'):
    obj = load(meta['file'])
    for delivery in obj['Siri']['ServiceDelivery']['StopMonitoringDelivery']:
        for visit in delivery.get('MonitoredStopVisit', []):
            live_ids.add(visit['MonitoredVehicleJourney'].get('FramedVehicleJourneyRef', {}).get('DatedVehicleJourneyRef'))
exact_live_matches = 0
for row in table('trips.txt'):
    trip_count += 1
    missing_trips.discard(row['trip_id'])
    if row['trip_id'] in needed:
        sample_trip_routes[row['trip_id']] = row['route_id']
    bad_route += row['route_id'] not in route_ids
    bad_service += row['service_id'] not in service_ids
    exact_live_matches += row['trip_id'] in live_ids
    if row['route_id'] in ('IDFM:C01374', 'IDFM:C01083'):
        pilot_trips[row['route_id']] += 1
        pilot_examples.setdefault(row['route_id'], row['trip_id'])
        if row['service_id'] in active_services:
            pilot_active_trips[row['route_id']] += 1
check('all trip route references resolve', bad_route == 0, bad_route)
check('all trip service references resolve', bad_service == 0, bad_service)
check('sample stop-time trip references resolve', not missing_trips, len(missing_trips))
check('sample stop-time stop references resolve', all(r['stop_id'] in stop_ids for r in times), len(times))
bad_time = bad_order = missing_times = 0
previous = {}
for row in times:
    try:
        arrival, departure = seconds(row['arrival_time']), seconds(row['departure_time'])
        sequence = int(row['stop_sequence'])
        missing_times += arrival is None or departure is None
        bad_time += arrival is not None and departure is not None and arrival > departure
        if row['trip_id'] in previous:
            seq, earlier = previous[row['trip_id']]
            bad_order += sequence <= seq or (arrival is not None and earlier is not None and arrival < earlier)
        previous[row['trip_id']] = sequence, departure
    except ValueError:
        bad_time += 1
check('sample valid times and arrival <= departure', bad_time == 0, bad_time)
check('sample increasing stop sequences and times', bad_order == 0, bad_order)
coverage = load('coverage-pilot.json')['results'] + load('coverage-pilot-page2.json')['results']
pairs = {(r['line'], r['ns2_stoppointref']) for r in coverage}
check('filtered coverage pagination complete', len(coverage) == load('coverage-pilot.json')['total_count'], len(coverage))
check('filtered coverage line-stop pairs unique', len(pairs) == len(coverage), len(coverage)-len(pairs))
check('coverage line IDs map to GTFS routes', all('IDFM:' + r['line'].split(':')[-2] in route_ids for r in coverage), len(coverage))
mapped_stops = sum('IDFM:' + r['ns2_stoppointref'].split(':')[-2] in stop_ids for r in coverage)
REPORT['coverage'] = {'rows': len(coverage), 'by_line': dict(collections.Counter(r['line'] for r in coverage)), 'simple_stop_id_matches': mapped_stops, 'crs_example': coverage[0]['ns2_location']}
REPORT['gtfs'] = {'routes': len(routes), 'stops': len(stops), 'trips': trip_count, 'sample_stop_times': len(times), 'sample_missing_times': missing_times, 'calendar_min_start': min(r['start_date'] for r in cal), 'calendar_max_end': max(r['end_date'] for r in cal), 'pilot_trips': dict(pilot_trips), 'pilot_trip_examples': pilot_examples, 'exact_live_trip_matches': exact_live_matches, 'live_journey_ids_checked': len(live_ids), 'complete_archive': False}
REPORT['gtfs'].update(service_day=service_day, pilot_active_trips=dict(pilot_active_trips), sampled_stop_times_by_route=dict(collections.Counter(sample_trip_routes.get(r['trip_id'], 'UNMATCHED') for r in times)))
REPORT['coverage']['unmatched_stops'] = [{'line': r['line'], 'stop': r['ns2_stoppointref'], 'name': r['ns2_stopname']} for r in coverage if 'IDFM:' + r['ns2_stoppointref'].split(':')[-2] not in stop_ids]
check('both candidate routes have active scheduled trips on audit date', all(pilot_active_trips[r] > 0 for r in ('IDFM:C01374', 'IDFM:C01083')), dict(pilot_active_trips))
REPORT['live'] = []
for meta in load('live-manifest.json'):
    raw = (ROOT / meta['file']).read_bytes()
    check(meta['file'] + ': cached response hash', hashlib.sha256(raw).hexdigest() == meta['sha256'], meta['sha256'])
    sd = json.loads(raw)['Siri']['ServiceDelivery']
    deliveries = sd['StopMonitoringDelivery']
    check(meta['file'] + ': service status true', all(str(d.get('Status')).lower() == 'true' for d in deliveries), [d.get('Status') for d in deliveries])
    visits = [v for d in deliveries for v in d.get('MonitoredStopVisit', [])]
    target = [v for v in visits if v['MonitoredVehicleJourney']['LineRef']['value'] == meta['line']]
    check(meta['file'] + ': target line present', bool(target), len(target))
    now = dt.datetime.fromisoformat(meta['received_utc'])
    ages = [(now-dt.datetime.fromisoformat(v['RecordedAtTime'].replace('Z', '+00:00'))).total_seconds() for v in target]
    calls = [v['MonitoredVehicleJourney']['MonitoredCall'] for v in target]
    keys = ('ExpectedArrivalTime', 'ExpectedDepartureTime', 'AimedArrivalTime', 'AimedDepartureTime', 'ActualArrivalTime', 'ActualDepartureTime')
    REPORT['live'].append({'file': meta['file'], 'stop': meta['stop'], 'line': meta['line'], 'total_visits': len(visits), 'target_visits': len(target), 'record_age_seconds_min': min(ages), 'record_age_seconds_max': max(ages), 'populated_fields': {k: sum(bool(c.get(k)) for c in calls) for k in keys}, 'departure_statuses': dict(collections.Counter(c.get('DepartureStatus') for c in calls)), 'response_utc': sd['ResponseTimestamp']})
REPORT['checks_passed'] = sum(c['passed'] for c in REPORT['checks'])
REPORT['checks_total'] = len(REPORT['checks'])
(ROOT / 'quality-summary.json').write_text(json.dumps(REPORT, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in REPORT.items() if k != 'checks'}, indent=2))
print('FAILED CHECKS:', json.dumps([c for c in REPORT['checks'] if not c['passed']]))
raise SystemExit(0 if REPORT['checks_passed'] == REPORT['checks_total'] else 1)
