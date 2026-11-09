"""Download the published metro network references. No full GTFS download required."""
from datetime import datetime, timezone
import hashlib
import json
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from app import ROOT, NETWORK, read_keys

BASE = 'https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/'
SHAPES = 'traces-des-lignes-de-transport-en-commun-idfm'
ASSOCIATIONS = 'arrets-lignes'
COVERAGE = 'perimetre-des-donnees-tr-disponibles-plateforme-idfm'


def metro_codes(shapes):
    codes = []
    for row in shapes:
        if row.get('route_type') != 'Subway' or not re.fullmatch(r'IDFM:C\d+', row['route_id']):
            raise ValueError('Expected a published metro route')
        codes.append(row['route_id'].split(':')[-1])
    if not codes or len(codes) > 32 or len(set(codes)) != len(codes):
        raise ValueError('Missing, duplicate or unexpectedly many metro routes')
    return codes


def line_query(field, codes, prefix, suffix=''):
    return field + ' in (' + ','.join('"' + prefix + code + suffix + '"' for code in codes) + ')'


def records(dataset, where, key):
    rows, page_hashes, expected_total = [], [], None
    for offset in range(0, 3000, 100):
        # Stable IDs limit changes between pages; preparation is still not an atomic source snapshot.
        order = 'id,stop_id' if dataset == 'arrets-lignes' else ('line,ns2_stoppointref' if dataset.startswith('perimetre') else 'route_id')
        url = BASE + dataset + '/records?' + urlencode({'where': where, 'limit': 100, 'offset': offset, 'order_by': order})
        headers = {'User-Agent': 'ParisMobilityIntelligence/0.1', 'Accept-Encoding': 'identity'}
        if key:
            headers['Authorization'] = 'apikey ' + key
        request = Request(url, headers=headers)
        with urlopen(request, timeout=20) as response:
            raw = response.read(3_000_001)
            if len(raw) > 3_000_000:
                raise ValueError('Source response too large')
        payload = json.loads(raw)
        if expected_total is None:
            expected_total = payload['total_count']
        if payload['total_count'] != expected_total or (not payload['results'] and expected_total):
            raise ValueError('Source changed or pagination stopped early')
        rows.extend(payload['results'])
        page_hashes.append(hashlib.sha256(raw).hexdigest())
        if len(rows) >= payload['total_count']:
            if len(rows) != payload['total_count']:
                raise ValueError('Source changed during pagination; retry preparation')
            return rows, {'dataset': dataset, 'retrieved_at': datetime.now(timezone.utc).isoformat(),
                          'records': len(rows), 'page_sha256': page_hashes, 'where': where,
                          'url': 'https://prim.iledefrance-mobilites.fr/fr/jeux-de-donnees/' + dataset}
    raise ValueError('Unexpected metro subset size; refusing unbounded download')


def build_network(associations, shapes, coverage, sources):
    codes = metro_codes(shapes)
    covered = {(r['line'], r['ns2_stoppointref']): r for r in coverage}
    if len(covered) != len(coverage):
        raise ValueError('Duplicate coverage pairs')
    stops, seen = [], set()
    for row in associations:
        match = re.fullmatch(r'IDFM:(\d+)', row['stop_id'])
        if not match or row['id'] not in {'IDFM:' + line for line in codes}:
            raise ValueError('Unexpected stop or route identifier')
        lat, lon = float(row['stop_lat']), float(row['stop_lon'])
        if not (48 <= lat <= 49.5 and 1.5 <= lon <= 3.5):
            raise ValueError('Coordinate outside the expected regional bounds')
        line = 'STIF:Line::' + row['id'].split(':')[-1] + ':'
        ref = 'STIF:StopPoint:Q:' + match[1] + ':'
        pair = line, ref
        if pair in seen:
            raise ValueError('Duplicate line/stop association')
        seen.add(pair)
        stops.append({'id': row['stop_id'], 'line_id': line, 'monitoring_ref': ref,
                      'name': row['stop_name'], 'lat': lat, 'lon': lon,
                      'commune': row.get('nom_commune', ''), 'live_supported': pair in covered})
    routes = []
    for row in shapes:
        code = row['route_id'].split(':')[-1]
        if code not in codes:
            raise ValueError('Unexpected route geometry')
        geometry = row['shape']['geometry']
        if geometry['type'] not in ('LineString', 'MultiLineString'):
            raise ValueError('Expected route line geometry')
        parts = [geometry['coordinates']] if geometry['type'] == 'LineString' else geometry['coordinates']
        if not parts or any(not part for part in parts):
            raise ValueError('Empty route geometry')
        for part in parts:
            for lon, lat, *_ in part:
                if not (48 <= lat <= 49.5 and 1.5 <= lon <= 3.5):
                    raise ValueError('Route coordinates outside region')
        routes.append({'id': 'STIF:Line::' + code + ':', 'name': {'3B': '3bis', '7B': '7bis'}.get(row['route_short_name'], row['route_short_name']),
                       'source_name': row['route_short_name'],
                       'mode': 'Métro',
                       'color': '#' + row['route_color'], 'geometry': geometry})
    if len(routes) != len(codes) or {r['id'] for r in routes} != {'STIF:Line::' + c + ':' for c in codes}:
        raise ValueError('All distinct metro routes are required')
    if any(not any(s['line_id'] == r['id'] for s in stops) for r in routes):
        raise ValueError('Missing route stops')
    omitted = [{'line_id': line, 'monitoring_ref': ref, 'name': row['ns2_stopname']}
               for (line, ref), row in covered.items() if (line, ref) not in seen]
    return {'prepared_at': datetime.now(timezone.utc).isoformat(), 'scope': 'metro', 'routes': sorted(routes, key=lambda r: (int(re.match(r'\d+', r['name'])[0]), 'bis' in r['name'])),
            'stops': sorted(stops, key=lambda s: (s['name'], s['line_id'], s['id'])),
            'unmapped': omitted, 'sources': sources}


def main():
    key = read_keys().get('PRIM_STATIC_TOKEN')
    if not key:
        raise SystemExit('Add PRIM_STATIC_TOKEN to .env first.')
    rows, sources = {}, []
    try:
        rows[SHAPES], source = records(SHAPES, 'route_type="Subway"', key)
        sources.append(source)
        codes = metro_codes(rows[SHAPES])
        queries = {ASSOCIATIONS: line_query('id', codes, 'IDFM:'),
                   COVERAGE: line_query('line', codes, 'STIF:Line::', ':')}
        for dataset, query in queries.items():
            rows[dataset], source = records(dataset, query, key)
            sources.append(source)
        network = build_network(rows[ASSOCIATIONS], rows[SHAPES], rows[COVERAGE], sources)
    except Exception as error:
        raise SystemExit('Preparation failed (' + type(error).__name__ + '). Existing network was preserved; check access and source schema.') from None
    NETWORK.parent.mkdir(parents=True, exist_ok=True)
    temporary = NETWORK.with_suffix('.tmp')
    temporary.write_text(json.dumps(network, ensure_ascii=False), encoding='utf-8')
    temporary.replace(NETWORK)
    print(f"Prepared {len(network['routes'])} routes and {len(network['stops'])} boarding points; {len(network['unmapped'])} coverage points remain unmapped.")


if __name__ == '__main__':
    main()
