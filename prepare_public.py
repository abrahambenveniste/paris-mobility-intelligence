"""Prepare a public map from two openly accessible reference datasets."""
import json
from pathlib import Path
from urllib.request import Request, urlopen
from datetime import datetime, timezone
from prepare_data import SHAPES, ASSOCIATIONS, records, metro_codes, line_query, build_network
from app import ROOT

PUBLIC_NETWORK = ROOT / 'data' / 'public-network.json'
AREA_URL = 'https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/arrondissements/records?limit=20&order_by=c_ar'


def validate_areas(payload):
    rows = payload.get('results', [])
    if payload.get('total_count') != 20 or len(rows) != 20 or {r.get('c_ar') for r in rows} != set(range(1, 21)):
        raise ValueError('Expected exactly the 20 Paris arrondissements')
    areas = []
    for row in rows:
        geometry = row.get('geom', {}).get('geometry', {})
        rings = geometry.get('coordinates', [])
        if geometry.get('type') != 'Polygon' or not rings:
            raise ValueError('Invalid arrondissement polygon')
        for ring in rings:
            if not 4 <= len(ring) <= 20000 or ring[0] != ring[-1]:
                raise ValueError('Invalid polygon ring')
            for point in ring:
                if (len(point) < 2 or any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in point[:2])
                        or not (1.5 <= point[0] <= 3.5 and 48 <= point[1] <= 49.5)):
                    raise ValueError('Polygon coordinate outside expected region')
        areas.append({'number': row['c_ar'], 'name': row.get('l_aroff') or row.get('l_ar'), 'geometry': geometry})
    return sorted(areas, key=lambda a: a['number'])


def fetch_areas():
    request = Request(AREA_URL, headers={'User-Agent': 'ParisMobilityIntelligence/0.1', 'Accept-Encoding': 'identity'})
    with urlopen(request, timeout=20) as response:
        raw = response.read(3_000_001)
    if len(raw) > 3_000_000:
        raise ValueError('Boundary dataset too large')
    return validate_areas(json.loads(raw))


def main():
    try:
        shapes, shape_source = records(SHAPES, 'route_type="Subway"', '')
        codes = metro_codes(shapes)
        stops, stop_source = records(ASSOCIATIONS, line_query('id', codes, 'IDFM:'), '')
        network = build_network(stops, shapes, [], [shape_source, stop_source])
        # Coverage is unknown here; do not publish false coverage conclusions.
        for stop in network['stops']:
            stop.pop('live_supported', None)
            stop.pop('monitoring_ref', None)
        network.pop('unmapped', None)
        network['arrondissements'] = fetch_areas()
        network['area_source'] = {'name': 'Ville de Paris — Arrondissements',
                                  'url': 'https://opendata.paris.fr/explore/dataset/arrondissements/',
                                  'licence': 'ODbL', 'retrieved_at': datetime.now(timezone.utc).isoformat()}
        network['scope'] = 'public_map_preview'
        PUBLIC_NETWORK.parent.mkdir(parents=True, exist_ok=True)
        temporary = PUBLIC_NETWORK.with_suffix('.tmp')
        temporary.write_text(json.dumps(network, ensure_ascii=False), encoding='utf-8')
        temporary.replace(PUBLIC_NETWORK)
        print(f"Prepared public map: {len(network['routes'])} métro lines and {len(network['stops'])} boarding-point records.")
    except Exception as error:
        raise SystemExit('Public reference preparation failed ('+type(error).__name__+'). No incomplete map was saved.') from None


if __name__ == '__main__':
    main()
