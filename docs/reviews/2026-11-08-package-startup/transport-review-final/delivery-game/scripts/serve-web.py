#!/usr/bin/env python3
"""Static preview server with precompressed transfer and version-aware caching."""
import argparse
import hashlib
import mimetypes
import re
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


def encoding_qualities(header):
    qualities = {}
    for part in (header or '').split(','):
        pieces = part.strip().lower().split(';')
        if not pieces[0]:
            continue
        quality = 1.0
        for parameter in pieces[1:]:
            name, _, value = parameter.strip().partition('=')
            if name == 'q':
                try:
                    quality = float(value)
                    if not 0 <= quality <= 1:
                        quality = 0.0
                except ValueError:
                    quality = 0.0
        qualities[pieces[0]] = quality
    return qualities


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory, **kwargs):
        self.build_root = Path(directory).resolve()
        super().__init__(*args, directory=str(self.build_root), **kwargs)

    def send_head(self):
        try:
            parts = urlsplit(self.path)
            requested = unquote(parts.path)
            candidate = (self.build_root / requested.lstrip('/')).resolve()
            candidate.relative_to(self.build_root)
            if candidate.is_dir():
                if not parts.path.endswith('/'):
                    self.send_response(301)
                    self.send_header('Location', parts.path + '/' + ('?' + parts.query if parts.query else ''))
                    self.send_header('Content-Length', '0')
                    self.end_headers()
                    return None
                candidate = (candidate / 'index.html').resolve()
                candidate.relative_to(self.build_root)
        except (ValueError, OSError):
            self.send_error(403, 'Outside build root')
            return None
        if not candidate.is_file():
            self.send_error(404, 'File not found')
            return None
        encoded = candidate.with_name(candidate.name + '.gz')
        try:
            # Sidecars are generated from these exact bytes by the packager.
            encoded.resolve().relative_to(self.build_root)
        except ValueError:
            encoded = candidate
        qualities = encoding_qualities(self.headers.get('Accept-Encoding'))
        gzip_quality = qualities.get('gzip', qualities.get('*', 0))
        identity_quality = qualities.get('identity', 0 if qualities.get('*') == 0 else 1)
        use_gzip = encoded != candidate and encoded.is_file() and gzip_quality > 0
        if not use_gzip and identity_quality <= 0:
            self.send_error(406, 'No acceptable content encoding')
            return None
        selected = encoded if use_gzip else candidate
        try:
            stream = selected.open('rb')
            stat = selected.stat()
            digest = hashlib.sha256()
            for block in iter(lambda: stream.read(128 * 1024), b''):
                digest.update(block)
            stream.seek(0)
        except OSError:
            self.send_error(404, 'File not found')
            return None
        etag = '"' + digest.hexdigest() + '"'
        versioned = bool(re.search(r'[.-][0-9a-f]{5,64}\.', candidate.name))
        cache = 'public, max-age=31536000, immutable' if versioned else 'no-cache'
        if candidate.suffix.lower() == '.html':
            cache = 'no-cache'
        supplied = self.headers.get('If-None-Match', '')
        tags = [part.strip().removeprefix('W/') for part in supplied.split(',')]
        if '*' in tags or etag in tags:
            stream.close()
            self.send_response(304)
            self.send_header('ETag', etag)
            self.send_header('Cache-Control', cache)
            self.send_header('Vary', 'Accept-Encoding')
            self.end_headers()
            return None
        content_type = {'.js': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8',
                        '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
                        '.wasm': 'application/wasm'}.get(candidate.suffix.lower())
        if content_type is None:
            content_type = mimetypes.guess_type(str(candidate))[0] or 'application/octet-stream'
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(stat.st_size))
        self.send_header('Last-Modified', self.date_time_string(stat.st_mtime))
        self.send_header('ETag', etag)
        self.send_header('Cache-Control', cache)
        self.send_header('Vary', 'Accept-Encoding')
        if use_gzip:
            self.send_header('Content-Encoding', 'gzip')
        self.end_headers()
        return stream


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--bind', default='127.0.0.1')
    options = parser.parse_args()
    if not options.directory.is_dir():
        parser.error('build directory does not exist')
    server = ThreadingHTTPServer((options.bind, options.port), partial(Handler, directory=options.directory))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
