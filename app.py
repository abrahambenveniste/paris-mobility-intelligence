"""Local Paris network explorer. Python standard library; no background polling."""
import argparse
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
import time
import webbrowser
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import Request, urlopen
from traffic import fetch_reports

ROOT = Path(__file__).resolve().parent
WEB = ROOT / 'web'
NETWORK = ROOT / 'data' / 'pilot-network.json'


def read_keys(path=ROOT / '.env'):
    values = {}
    if path.exists():
        for line in path.read_text(encoding='utf-8-sig').splitlines():
            if '=' in line and not line.lstrip().startswith('#'):
                key, value = line.split('=', 1)
                values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def timestamp(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return parsed if parsed.tzinfo else None
    except (ValueError, TypeError, AttributeError):
        return None


def normalize_departures(payload, line, now):
    service = payload['Siri']['ServiceDelivery']
    deliveries = service.get('StopMonitoringDelivery', [])
    if not deliveries or any(str(d.get('Status')).lower() != 'true' for d in deliveries):
        raise ValueError('Upstream service did not confirm a successful delivery')
    results, seen, excluded_past, excluded_invalid = [], set(), 0, 0
    for delivery in deliveries:
        for visit in delivery.get('MonitoredStopVisit', []):
            journey = visit.get('MonitoredVehicleJourney', {})
            if journey.get('LineRef', {}).get('value') != line:
                continue
            call = journey.get('MonitoredCall', {})
            kind = 'departure' if call.get('ExpectedDepartureTime') else 'arrival'
            expected = timestamp(call.get('ExpectedDepartureTime') or call.get('ExpectedArrivalTime'))
            cancelled = call.get('DepartureStatus') == 'cancelled' or call.get('ArrivalStatus') == 'cancelled'
            if expected is None and not cancelled:
                excluded_invalid += 1
                continue
            if expected is not None and expected < now and not cancelled:
                excluded_past += 1
                continue
            identity = visit.get('ItemIdentifier')
            if identity and identity in seen:
                continue
            if identity:
                seen.add(identity)
            destinations = journey.get('DestinationName') or journey.get('DirectionName') or []
            source = timestamp(visit.get('RecordedAtTime'))
            results.append({'expected_at': expected.isoformat() if expected else None,
                            'kind': kind, 'destination': destinations[0].get('value', 'Unknown destination') if destinations else 'Unknown destination',
                            'recorded_at': source.isoformat() if source else None,
                            'cancelled': cancelled})
    results.sort(key=lambda r: r['expected_at'] or '9999')
    return {'departures': results, 'fetched_at': now.isoformat(),
            'provider_response_at': service.get('ResponseTimestamp'),
            'excluded_past': excluded_past, 'excluded_invalid': excluded_invalid}


def fetch_departures(stop, line, key):
    if not key:
        raise RuntimeError('Add PRIM_API_KEY to the local .env file and restart the server.')
    url = 'https://prim.iledefrance-mobilites.fr/marketplace/stop-monitoring?' + urlencode({'MonitoringRef': stop})
    request = Request(url, headers={'apiKey': key, 'Accept': 'application/json',
                                   'User-Agent': 'ParisMobilityIntelligence/0.1 (+https://github.com/abrahambenveniste/paris-mobility-intelligence)'})
    with urlopen(request, timeout=15) as response:
        raw = response.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError('Response exceeded the safety limit')
    return normalize_departures(json.loads(raw), line, datetime.now(timezone.utc))


class RequestCache:
    """Single-process, 120-second cache and persistent rolling request budget."""
    def __init__(self, path, limit=900, ttl=120):
        self.path, self.limit, self.ttl = path, limit, ttl
        self.lock, self.cache = threading.Lock(), {}
        self.calls = json.loads(path.read_text(encoding='utf-8')) if path.exists() else []
        if not isinstance(self.calls, list) or any(not isinstance(t, (int, float)) for t in self.calls):
            raise ValueError('Invalid local request budget; inspect it before restarting.')

    def get(self, identifier, loader):
        with self.lock:
            now = time.time()
            previous = self.cache.get(identifier)
            if previous and now - previous[0] < self.ttl:
                return {**previous[1], 'cached': True}
            self.calls = [t for t in self.calls if now - t < 86400]
            if len(self.calls) >= self.limit:
                raise RuntimeError('Local request budget reached. Cached results remain available; try later.')
            self.calls.append(now)  # Failed calls also count.
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix('.tmp')
            temporary.write_text(json.dumps(self.calls), encoding='utf-8')
            temporary.replace(self.path)
            result = loader()
            self.cache[identifier] = time.time(), result
            return {**result, 'cached': False}


def handler_class(network, key, cache, traffic_cache=None):
    allowed_lines = {r['id'] for r in network.get('routes', []) if r.get('mode') == 'Métro'}
    allowed = {(s['line_id'], s['monitoring_ref']) for s in network['stops'] if s['live_supported']}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # Do not log request paths or upstream exception details.

        def send(self, status, body, mime='application/json; charset=utf-8'):
            raw = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(raw)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: https://tile.openstreetmap.org; connect-src 'self'; frame-ancestors 'none'")
            self.end_headers()
            try:
                self.wfile.write(raw)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def do_GET(self):
            host = self.headers.get('Host', '').split(':')[0]
            if host not in ('127.0.0.1', 'localhost') or self.headers.get('Sec-Fetch-Site') == 'cross-site':
                return self.send(403, {'error': 'This server is for local use only.'})
            url = urlsplit(self.path)
            if url.path == '/api/network':
                return self.send(200, network)
            if url.path == '/api/notice-history':
                from disruption_history import saved_history
                search = parse_qs(url.query).get('search', [''])[0]
                line = parse_qs(url.query).get('line', [''])[0]
                if line and line not in allowed_lines:
                    return self.send(400, {'error':'Select a published metro line.'})
                if len(search) > 200:
                    return self.send(400, {'error': 'Search is limited to 200 characters.'})
                try:
                    return self.send(200, saved_history(search=search,line=line))
                except Exception:
                    return self.send(503, {'error':'Saved history is unavailable. Try again after the current collection check.'})
            if url.path == '/api/traffic':
                line = parse_qs(url.query).get('line', [''])[0]
                if line not in allowed_lines:
                    return self.send(400, {'error': 'Select a supported metro line.'})
                if traffic_cache is None:
                    return self.send(503, {'error': 'Traffic reports are not configured.'})
                try:
                    result = traffic_cache.get(line, lambda: fetch_reports(line, key))
                    return self.send(200, result)
                except RuntimeError as error:
                    return self.send(503, {'error': str(error)})
                except Exception:
                    return self.send(502, {'error': 'Traffic reports unavailable or incomplete. No service conclusion can be drawn.'})
            if url.path == '/api/departures':
                query = parse_qs(url.query)
                line, stop = query.get('line', [''])[0], query.get('stop', [''])[0]
                if (line, stop) not in allowed:
                    return self.send(400, {'error': 'This boarding point is not in the supported metro network.'})
                try:
                    result = cache.get((line, stop), lambda: fetch_departures(stop, line, key))
                    return self.send(200, result)
                except RuntimeError as error:
                    return self.send(503, {'error': str(error)})
                except Exception:
                    return self.send(502, {'error': 'PRIM is unavailable or returned an unexpected response. Try again later.'})
            assets = {'/': ('index.html', 'text/html; charset=utf-8'),
                      '/history': ('history.html', 'text/html; charset=utf-8'),
                      '/history.js': ('history.js', 'text/javascript; charset=utf-8'),
                      '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
                      '/quality.js': ('quality.js', 'text/javascript; charset=utf-8'),
                      '/stations.js': ('stations.js', 'text/javascript; charset=utf-8'),
                      '/style.css': ('style.css', 'text/css; charset=utf-8')}
            if url.path not in assets:
                return self.send(404, {'error': 'Not found'})
            name, mime = assets[url.path]
            return self.send(200, (WEB / name).read_bytes(), mime)
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--open', action='store_true', help='Open the local explorer in your default browser')
    args = parser.parse_args()
    if not NETWORK.exists():
        raise SystemExit('First-time setup: run python prepare_data.py to download the metro reference network, then start again.')
    network = json.loads(NETWORK.read_text(encoding='utf-8'))
    if network.get('scope') != 'metro':
        raise SystemExit('Run python prepare_data.py to replace the old two-line snapshot with the metro network.')
    cache = RequestCache(ROOT / 'artifacts' / 'app-request-budget.json')
    traffic_cache = RequestCache(ROOT / 'artifacts' / 'traffic-request-budget.json', ttl=300)
    key = read_keys().get('PRIM_API_KEY', '')
    if not key:
        print('PRIM_API_KEY is missing from .env. The map works, but live requests need your key.', flush=True)
    try:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), handler_class(network, key, cache, traffic_cache))
    except OSError:
        raise SystemExit(f'Cannot open local port {args.port}. Close another running copy or use python app.py --port 8766.')
    address = f'http://127.0.0.1:{server.server_port}'
    print(f'Paris Mobility Intelligence: {address}\nKeep this terminal open. Press Ctrl+C to stop.', flush=True)
    if args.open:
        try:
            webbrowser.open(address)
        except webbrowser.Error:
            print('Open the address above in your browser.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
