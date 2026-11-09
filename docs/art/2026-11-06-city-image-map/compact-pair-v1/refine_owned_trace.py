#!/usr/bin/env python3
"""One bounded correction to this turn's owned trace, guarded against user edits."""
import importlib.util
import json
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent


def main():
    record = json.loads((HERE / 'build-record.json').read_text())
    target = HERE / 'tiled/compact-pair.tmj'
    spec = importlib.util.spec_from_file_location('pair_exporter', HERE / 'assemble_pair.py')
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if module.sha(target) != record['sourceTiledSHA256'] or (HERE / 'trace-adjustment.json').exists():
        raise SystemExit('Map changed or adjustment already applied; preserve it without reset.')
    doc = json.loads(target.read_text())
    old_graph = json.loads((HERE / 'navigation/graph.json').read_text())
    changed = []
    actual_loop = [(95, 558), (120, 474), (149, 367), (180, 280), (204, 243), (260, 231),
                   (500, 217), (730, 203), (870, 197), (911, 215), (957, 245), (992, 300),
                   (1045, 380), (1085, 440), (1122, 500), (1155, 558)]
    for group in doc['layers']:
        for layer in group.get('layers', []):
            for obj in layer.get('objects', []):
                if obj['name'] == 'A-main-to-loop':
                    points = [(715, 558), (1155, 558)]
                elif obj['name'] == 'A-portal':
                    points = [(1155, 558), (1300, 557), (1504, 558)]
                elif obj['name'] == 'A-upper-loop':
                    points = actual_loop
                else:
                    continue
                changed.append(obj['name'])
                obj['x'], obj['y'] = points[0]
                obj['polyline'] = [{'x': p[0] - obj['x'], 'y': p[1] - obj['y']} for p in points]
    module.save(target, doc)
    graph = module.export_graph(json.loads(target.read_text()))
    module.save(HERE / 'navigation/graph.json', graph)
    offline = HERE / 'navigation/offline.html'
    html = offline.read_text()
    before = 'globalThis.__embeddedGraph=' + json.dumps(old_graph, ensure_ascii=False) + ';'
    if html.count(before) != 1:
        raise RuntimeError('Embedded graph changed; no speculative replacement.')
    html = html.replace(before, 'globalThis.__embeddedGraph=' + json.dumps(graph, ensure_ascii=False) + ';')
    offline.write_text(html)
    overlay = Image.open(HERE / 'preview/pair-composite.png').convert('RGB')
    draw = ImageDraw.Draw(overlay)
    for edge in graph['edges']:
        draw.line([tuple(p) for p in edge['points']], fill='#ff28b8', width=4, joint='curve')
    draw.line([(1504, 0), (1504, 1024)], fill='#df8c28', width=2)
    overlay.save(HERE / 'preview/traced-pair.png')
    record['sourceTiledSHA256'] = module.sha(target)
    module.save(HERE / 'build-record.json', record)
    module.save(HERE / 'trace-adjustment.json', {
        'changedRoads': changed, 'reason': 'Initial A eastern-loop trace ran near the curb; moved only the new vector centerline onto visible asphalt.',
        'actualNativeSupportingRows': {'y300': [963, 1021], 'y380': [1016, 1074], 'y440': [1055, 1114], 'y500': [1091, 1153]},
        'nativeImagesChanged': False, 'extraImageRequests': 0,
        'newTiledSHA256': module.sha(target), 'userMapReset': False})
    print(json.dumps({'corrected': changed, 'nodes': len(graph['nodes']), 'edges': len(graph['edges']),
                      'components': len(graph['connectedComponents']), 'noNativeEdits': True}))


if __name__ == '__main__':
    main()
