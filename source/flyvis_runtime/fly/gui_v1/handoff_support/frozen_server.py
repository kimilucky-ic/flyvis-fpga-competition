"""Portable accepted-result replay. Python stdlib only; never performs inference."""
import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
import re
from urllib.parse import parse_qs, urlparse
import webbrowser


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(2097152), b''):
            h.update(chunk)
    return h.hexdigest()


def inside(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Path escapes package')
    return path


def route_key(url):
    parsed = urlparse(url)
    if parsed.path.endswith('/directions'):
        q = parse_qs(parsed.query)
        cell = q.get('cell', ['T4c'])[0]
        intensity = float(q.get('intensity', ['1'])[0])
        sample = int(q.get('sample', ['0'])[0]) if '/bar10/' in parsed.path else 0
        return f'{parsed.path}?cell={cell}&intensity={intensity:g}&sample={sample}'
    return parsed.path


def load_package(root):
    snapshot = json.loads((root / 'data/snapshot.json').read_text('utf-8'))
    routes_path = root / 'data/routes.json'
    if sha256(routes_path) != snapshot['routes_sha256']:
        raise ValueError('Route index SHA mismatch')
    routes = json.loads(routes_path.read_text('utf-8'))
    manifest = json.loads((root / 'package_manifest.json').read_text('utf-8'))
    verified = 0
    for entry in manifest['files']:
        if entry['role'] == 'editable_frontend':
            continue
        path = inside(root, entry['path'])
        if path.stat().st_size != entry['bytes'] or sha256(path) != entry['sha256']:
            raise ValueError(f"Package integrity mismatch: {entry['path']}")
        verified += 1
    for entry in routes.values():
        path = inside(root, entry['file'])
        if path.stat().st_size != entry['bytes'] or sha256(path) != entry['sha256']:
            raise ValueError('Replay payload SHA mismatch')
    return routes, snapshot, verified


def handler_factory(root, routes, snapshot):
    class Handler(BaseHTTPRequestHandler):
        def send(self, body, mime='application/json; charset=utf-8', status=200, headers=None):
            if not isinstance(body, bytes):
                body = json.dumps(body, ensure_ascii=False, allow_nan=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('X-Package-Mode', 'accepted-result-offline-replay')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; object-src 'none'; frame-ancestors 'none'")
            for k, v in (headers or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            try:
                parsed = urlparse(self.path)
                if parsed.path == '/api/package':
                    return self.send(snapshot)
                key = route_key(self.path)
                if key in routes:
                    entry = routes[key]
                    path = inside(root, entry['file'])
                    if path.stat().st_size != entry['bytes'] or sha256(path) != entry['sha256']:
                        return self.send({'status':'unavailable','error':'Verified replay file changed','result':None}, status=409)
                    return self.send(path.read_bytes(), entry['mime'], headers=entry['headers'])
                if re.fullmatch('/api/inference/[A-Za-z0-9_-]+', parsed.path):
                    return self.send({'status':'not_connected','execution_kind':None,'result':None,'error':'Visualization handoff has no GPU Job Service'}, status=503)
                if parsed.path.startswith('/api/'):
                    return self.send({'error':'No accepted replay route'}, status=404)
                name = 'index.html' if parsed.path == '/' else parsed.path.lstrip('/')
                path = inside(root / 'viewer', name)
                if not path.is_file():
                    return self.send({'error':'Not found'}, status=404)
                return self.send(path.read_bytes(), mimetypes.guess_type(str(path))[0] or 'application/octet-stream')
            except (ValueError, OSError, KeyError):
                return self.send({'error':'Invalid route or unavailable file'}, status=404)

        def do_POST(self):
            return self.send({'status':'not_connected','execution_kind':None,'result':None,'error':'This package only replays accepted results; no device operation or inference'}, status=503)
    return Handler


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--port', type=int, default=8781)
    p.add_argument('--no-open', action='store_true')
    args = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    routes, snapshot, count = load_package(root)
    handler = handler_factory(root, routes, snapshot)
    try:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), handler)
    except OSError:
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    url = f'http://127.0.0.1:{server.server_port}/'
    print(f'VERIFIED {count} files / 55 historical conditions / Full + Python 800 steps', flush=True)
    print(f'OFFLINE_REPLAY {url}', flush=True)
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
