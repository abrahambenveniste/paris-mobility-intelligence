"""On-demand, explicitly line-linked traffic reports; no incident prediction."""
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import re
from urllib.parse import quote
from urllib.request import Request, urlopen

def line_uri(line):
    match = re.fullmatch(r'STIF:Line::(C\d+):', line)
    if not match:
        raise ValueError('Unexpected line identifier')
    return 'line:IDFM:' + match[1]


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def message_text(messages):
    # Prefer the detailed web message over a short title or notification.
    ordered = sorted(messages, key=lambda m: 'web' not in m.get('channel', {}).get('types', []))
    for message in ordered:
        raw = message.get('text', '')
        if not isinstance(raw, str):
            raise ValueError('Unexpected message text')
        parser = PlainText()
        parser.feed(raw)
        text = ' '.join(' '.join(parser.parts).split())
        if text:
            return text
    return 'No message text supplied.'


def local_time(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y%m%dT%H%M%S').isoformat()
    except (ValueError, TypeError):
        raise ValueError('Unexpected provider date') from None


def normalize_reports(payload, line, now):
    target = line_uri(line)
    if 'error' in payload or not isinstance(payload.get('line_reports'), list):
        raise ValueError('Traffic response did not contain line reports')
    pagination = payload['pagination']
    if pagination['start_page'] != 0 or pagination['items_on_page'] != len(payload['line_reports']):
        raise ValueError('Unexpected pagination')
    if pagination['total_result'] != pagination['items_on_page']:
        raise ValueError('Incomplete traffic response; refusing to imply completeness')
    zone = payload.get('context', {}).get('timezone')
    if zone != 'Europe/Paris':
        raise ValueError('Unexpected or missing source timezone')
    linked = set()
    for report in payload['line_reports']:
        if report.get('line', {}).get('id') != target:
            raise ValueError('Unexpected line in response')
        linked.update(link['id'] for link in report['line'].get('links', [])
                      if link.get('type') == 'disruption')
    results, seen = [], set()
    disruptions = payload.get('disruptions', [])
    if not isinstance(disruptions, list):
        raise ValueError('Unexpected disruption records')
    for item in disruptions:
        identity = item['id']
        direct = any(obj.get('pt_object', {}).get('id') == target
                     for obj in item.get('impacted_objects', []))
        if identity not in linked and not direct:
            continue
        if identity in seen:
            continue
        seen.add(identity)
        periods = [{'begin': local_time(p.get('begin')), 'end': local_time(p.get('end'))}
                   for p in item.get('application_periods', [])]
        results.append({'id': identity, 'text': message_text(item.get('messages', [])),
                        'status': item.get('status', 'unknown'),
                        'effect': item.get('severity', {}).get('effect', 'UNKNOWN_EFFECT'),
                        'updated_at_local': local_time(item.get('updated_at')),
                        'periods_local': periods})
    if linked - {item['id'] for item in disruptions}:
        raise ValueError('Linked traffic report missing from response')
    return {'line_id': line, 'reports': results, 'fetched_at': now.isoformat(),
            'timezone': zone, 'provider_time_local': local_time(payload['context'].get('current_datetime')),
            'excluded_unlinked': sum(1 for item in disruptions if item['id'] not in seen)}


def fetch_reports(line, key):
    target = line_uri(line)
    if not key:
        raise RuntimeError('Add PRIM_API_KEY to .env and restart the server.')
    url = ('https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia/line_reports/lines/'
           + quote(target, safe='') + '/line_reports?count=100')
    request = Request(url, headers={'apiKey': key, 'Accept': 'application/json',
                                   'User-Agent': 'ParisMobilityIntelligence/0.1'})
    with urlopen(request, timeout=15) as response:
        raw = response.read(2_000_001)
    if len(raw) > 2_000_000:
        raise ValueError('Traffic response exceeds size bound')
    return normalize_reports(json.loads(raw), line, datetime.now(timezone.utc))
