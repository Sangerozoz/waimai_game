#!/usr/bin/env python3
"""Re-export manually edited road nodes without writing the Tiled input."""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    spec = importlib.util.spec_from_file_location('pair_exporter', HERE / 'assemble_pair.py')
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    target = HERE / 'tiled/compact-pair.tmj'
    before = module.sha(target)
    tiled = json.loads(target.read_text())
    groups = [l for l in tiled['layers'] if l['type'] == 'group']
    offsets = [(g.get('offsetx', 0), g.get('offsety', 0)) for g in groups]
    if offsets != [(0, 0), (1472, 0)]:
        raise SystemExit('Region offsets were edited. Preserve them; regenerate the raster canvas and inspect the new seam before navigation export. No auto-reset.')
    graph = module.export_graph(tiled)
    if len(graph['connectedComponents']) != 1:
        raise SystemExit('Edited roads are disconnected; preserve input and align actual shared endpoints. No through-building fallback.')
    previous = json.loads((HERE / 'navigation/graph.json').read_text())
    html_path = HERE / 'navigation/offline.html'
    html = html_path.read_text()
    old = 'globalThis.__embeddedGraph=' + json.dumps(previous, ensure_ascii=False) + ';'
    if html.count(old) != 1:
        raise SystemExit('Offline preview changed independently; preserve it instead of overwriting.')
    replacement = 'globalThis.__embeddedGraph=' + json.dumps(graph, ensure_ascii=False) + ';'
    module.save(HERE / 'navigation/graph.json', graph)
    html_path.write_text(html.replace(old, replacement))
    if module.sha(target) != before:
        raise RuntimeError('Tiled input changed during export; no restore performed.')
    print(json.dumps({'mapWritten': False, 'nodes': len(graph['nodes']), 'edges': len(graph['edges']),
                      'components': len(graph['connectedComponents']), 'preview': str(html_path),
                      'newRuntimeVerificationRequired': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()
