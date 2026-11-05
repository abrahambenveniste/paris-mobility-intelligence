"""Download only the two-line pilot references. No full GTFS download required."""
from datetime import datetime, timezone
import hashlib
import json
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from app import ROOT, NETWORK, read_keys

BASE = 'https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/'
LINES = ('C01374', 'C01083')
QUERIES = {
    'arrets-lignes': 'id in ("IDFM:C01374","IDFM:C01083")',
    'traces-des-lignes-de-transport-en-commun-idfm': 'route_id in ("IDFM:C01374","IDFM:C01083")',
    'perimetre-des-donnees-tr-disponibles-plateforme-idfm': 'line in ("STIF:Line::C01374:","STIF:Line::C01083:")',
}


def records(dataset, where, key):
    rows, page_hashes = [], []
    for offset in range(0, 500, 100):
        # Stable IDs limit changes between pages; preparation is still not an atomic source snapshot.
        order = 'stop_id' if dataset == 'arrets-lignes' else ('line,ns2_stoppointref' if dataset.startswith('perimetre') else 'route_id')
        url = BASE + dataset + '/records?' + urlencode({'where': where, 'limit': 100, 'offset': offset, 'order_by': order})
        request = Request(url, headers={'Authorization': 'apikey ' + key, 'User-Agent': 'ParisMobilityIntelligence/0.1'})
        with urlopen(request, timeout=20) as response:
            raw = response.read(3_000_001)
            if len(raw) > 3_000_000:
                raise ValueError('Source response too large')
        payload = json.loads(raw)
        rows.extend(payload['results'])
        page_hashes.append(hashlib.sha256(raw).hexdigest())
        if len(rows) >= payload['total_count']:
            if len(rows) != payload['total_count']:
                raise ValueError('Source changed during pagination; retry preparation')
            return rows, {'dataset': dataset, 'retrieved_at': datetime.now(timezone.utc).isoformat(),
                          'records': len(rows), 'page_sha256': page_hashes,
                          'url': 'https://prim.iledefrance-mobilites.fr/fr/jeux-de-donnees/' + dataset}
    raise ValueError('Unexpected pilot size; refusing unbounded download')


def build_network(associations, shapes, coverage, sources):
    covered = {(r['line'], r['ns2_stoppointref']): r for r in coverage}
    if len(covered) != len(coverage):
        raise ValueError('Duplicate coverage pairs')
    stops, seen = [], set()
    for row in associations:
        match = re.fullmatch(r'IDFM:(\d+)', row['stop_id'])
        if not match or row['id'] not in {'IDFM:' + line for line in LINES}:
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
        if code not in LINES:
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
        routes.append({'id': 'STIF:Line::' + code + ':', 'name': row['route_short_name'],
                       'mode': 'Métro' if code == 'C01374' else 'Bus',
                       'color': '#' + row['route_color'], 'geometry': geometry})
    if len(routes) != 2 or {r['id'] for r in routes} != {'STIF:Line::' + c + ':' for c in LINES}:
        raise ValueError('Both distinct pilot routes are required')
    if any(not any(s['line_id'] == r['id'] for s in stops) for r in routes):
        raise ValueError('Missing route stops')
    omitted = [{'line_id': line, 'monitoring_ref': ref, 'name': row['ns2_stopname']}
               for (line, ref), row in covered.items() if (line, ref) not in seen]
    return {'prepared_at': datetime.now(timezone.utc).isoformat(), 'routes': routes,
            'stops': sorted(stops, key=lambda s: (s['name'], s['line_id'], s['id'])),
            'unmapped': omitted, 'sources': sources}


def main():
    key = read_keys().get('PRIM_STATIC_TOKEN')
    if not key:
        raise SystemExit('Add PRIM_STATIC_TOKEN to .env first.')
    rows, sources = {}, []
    try:
        for dataset, query in QUERIES.items():
            rows[dataset], source = records(dataset, query, key)
            sources.append(source)
        network = build_network(*(rows[d] for d in QUERIES), sources)
    except Exception as error:
        raise SystemExit('Preparation failed (' + type(error).__name__ + '). Existing network was preserved; check access and source schema.') from None
    NETWORK.parent.mkdir(parents=True, exist_ok=True)
    temporary = NETWORK.with_suffix('.tmp')
    temporary.write_text(json.dumps(network, ensure_ascii=False), encoding='utf-8')
    temporary.replace(NETWORK)
    print(f"Prepared {len(network['routes'])} routes and {len(network['stops'])} boarding points; {len(network['unmapped'])} coverage points remain unmapped.")


if __name__ == '__main__':
    main()
