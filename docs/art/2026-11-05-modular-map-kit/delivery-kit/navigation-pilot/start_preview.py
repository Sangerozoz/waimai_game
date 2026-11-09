#!/usr/bin/env python3
"""Open this standalone navigation preview locally; no account or extra packages."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import webbrowser

root = Path(__file__).resolve().parent
with ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(root))) as server:
    url = f'http://127.0.0.1:{server.server_port}/'
    print(f'导航小样：{url}\n关闭此终端或按 Control+C 停止。', flush=True)
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
