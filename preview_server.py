"""Public map-only preview: no credentials, database, live requests, or history."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from urllib.parse import urlsplit
from app import ROOT, WEB
from prepare_public import PUBLIC_NETWORK


def preview_handler(network):
    assets = {'/': ('public.html','text/html; charset=utf-8'),
              '/public.js': ('public.js','text/javascript; charset=utf-8'),
              '/stations.js': ('stations.js','text/javascript; charset=utf-8'),
              '/style.css': ('style.css','text/css; charset=utf-8')}
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def do_GET(self):
            path = urlsplit(self.path).path
            if path == '/api/network':
                raw = json.dumps(network,ensure_ascii=False).encode('utf-8')
                mime, status = 'application/json; charset=utf-8', 200
            elif path in assets:
                name,mime=assets[path]
                raw,status=(WEB/name).read_bytes(),200
            else:
                raw,mime,status=b'Not found','text/plain; charset=utf-8',404
            self.send_response(status)
            self.send_header('Content-Type',mime)
            self.send_header('Content-Length',str(len(raw)))
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: https://tile.openstreetmap.org; connect-src 'self'; frame-ancestors 'none'")
            self.end_headers()
            try:
                self.wfile.write(raw)
            except (BrokenPipeError,ConnectionResetError):
                pass
    return Handler


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--public',action='store_true',help='Bind to the hosting service network')
    args=parser.parse_args()
    if not PUBLIC_NETWORK.exists():
        raise SystemExit('Run python prepare_public.py before starting the preview.')
    network=json.loads(PUBLIC_NETWORK.read_text(encoding='utf-8'))
    if network.get('scope') != 'public_map_preview' or not network.get('routes') or not network.get('stops'):
        raise SystemExit('Invalid public reference snapshot; run python prepare_public.py again.')
    port=int(os.environ.get('PORT','8766'))
    server=ThreadingHTTPServer(('0.0.0.0' if args.public else '127.0.0.1',port),preview_handler(network))
    print(f'Public map preview listening on port {port}',flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
