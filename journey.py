"""Retrieve a bounded metro-and-walking journey, optionally avoiding one line."""
from datetime import datetime, timezone
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from traffic import line_uri


def normalize_journeys(payload, avoided):
    if 'error' in payload:
        return {'journeys': [], 'message': 'The provider could not find a journey for this request.',
                'fetched_at': datetime.now(timezone.utc).isoformat()}
    if not isinstance(payload.get('journeys'), list):
        raise ValueError('Unexpected journey response')
    journeys = []
    for journey in payload['journeys'][:3]:
        sections = []
        for section in journey['sections']:
            kind = section['type']
            if kind not in ('public_transport', 'street_network', 'transfer', 'waiting', 'crow_fly'):
                raise ValueError('Unsupported journey section')
            info = section.get('display_informations', {})
            if kind == 'public_transport':
                line_ids = [link.get('id') for link in section.get('links', []) if link.get('type') == 'line']
                if info.get('commercial_mode') not in ('Métro', 'Metro') or len(line_ids) != 1 or line_ids[0] == avoided:
                    raise ValueError('Unexpected transport mode or avoided line')
            if kind in ('street_network', 'crow_fly') and section.get('mode') not in (None, 'walking'):
                raise ValueError('Unexpected street mode')
            sections.append({'kind': kind, 'from': section.get('from', {}).get('name'),
                             'to': section.get('to', {}).get('name'), 'duration': section.get('duration'),
                             'line': info.get('code'), 'direction': info.get('direction'),
                             'freshness': section.get('data_freshness')})
        journeys.append({'duration': journey['duration'], 'departure': journey.get('departure_date_time'),
                         'arrival': journey.get('arrival_date_time'), 'sections': sections})
    return {'journeys': journeys, 'provider_time_local': payload.get('context', {}).get('current_datetime'),
            'fetched_at': datetime.now(timezone.utc).isoformat()}


def fetch_journeys(start, end, avoided_line, key):
    avoided = line_uri(avoided_line) if avoided_line else None
    params = [('from', f"{start['lon']};{start['lat']}"), ('to', f"{end['lon']};{end['lat']}"),
              ('data_freshness', 'realtime'), ('allowed_id[]', 'physical_mode:Metro'),
              ('max_nb_journeys', '3')]
    if avoided:
        params.append(('forbidden_uris[]', avoided))
    url = 'https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia/journeys?' + urlencode(params)
    request = Request(url, headers={'apikey': key, 'Accept': 'application/json',
                                    'User-Agent': 'ParisMobilityIntelligence/0.1'})
    with urlopen(request, timeout=20) as response:
        raw = response.read(2_000_001)
    if len(raw) > 2_000_000:
        raise ValueError('Journey response exceeded the size limit')
    return normalize_journeys(json.loads(raw), avoided)
