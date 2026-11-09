"""Prepare a public map from two openly accessible reference datasets."""
import json
from pathlib import Path
from prepare_data import SHAPES, ASSOCIATIONS, records, metro_codes, line_query, build_network
from app import ROOT

PUBLIC_NETWORK = ROOT / 'data' / 'public-network.json'


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
