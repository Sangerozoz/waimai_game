#!/usr/bin/env python3
"""Correct this lease's owned map metadata after an actual Tiled reader diagnosis."""
import hashlib
import json
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    target = HERE / 'tiled/compact-pair-a2-b1.tmj'
    record = json.loads((HERE / 'static-record.json').read_text())
    if sha(target) != record['newTiledSHA256'] or (HERE / 'tiled-metadata-fix.json').exists():
        raise SystemExit('Map changed or fix already applied; preserve it without reset.')
    reader = json.loads((HERE / 'tiled/tiled-reader-normalized.tmj').read_text())
    observed = [{'name': g['name'], 'opacityReadByTiled': g.get('opacity')} for g in reader['layers'] if g['type'] == 'group']
    if not observed or any(g['opacityReadByTiled'] != 0 for g in observed):
        raise SystemExit('Observed reader result differs from the opacity hypothesis; stop.')
    source_doc = json.loads(target.read_text())
    (HERE / 'tiled/navigation-input-before-metadata-fix.tmj').write_bytes(target.read_bytes())
    changes = []
    def layers(rows):
        for layer in rows:
            if 'opacity' not in layer:
                changes.append({'layer': layer['name'], 'missingOpacitySetTo': 1})
                layer['opacity'] = 1
            if layer['type'] == 'group':
                layers(layer['layers'])
            elif layer['type'] == 'imagelayer':
                with Image.open(HERE / 'tiled' / layer['image']) as im:
                    layer['imagewidth'], layer['imageheight'] = im.size
    layers(source_doc['layers'])
    save(target, source_doc)
    old_graph = json.loads((HERE / 'navigation/graph.json').read_text())
    graph = json.loads(json.dumps(old_graph))
    graph['sourceTiledSHA256'] = sha(target)
    save(HERE / 'navigation/graph.json', graph)
    html_path = HERE / 'navigation/offline.html'
    html = html_path.read_text()
    old = 'globalThis.__embeddedGraph=' + json.dumps(old_graph, ensure_ascii=False) + ';'
    if html.count(old) != 1:
        raise RuntimeError('Offline page changed independently; no speculative replacement.')
    html_path.write_text(html.replace(old, 'globalThis.__embeddedGraph=' + json.dumps(graph, ensure_ascii=False) + ';'))
    record['newTiledSHA256'] = sha(target)
    record['newGraphSHA256'] = sha(HERE / 'navigation/graph.json')
    save(HERE / 'static-record.json', record)
    for old_name, new_name in [('browser-walkthrough.json', 'browser-walkthrough-before-metadata-fix.json'),
                               ('navigation-arrival-A2-B1.jpg', 'navigation-arrival-before-metadata-fix.jpg'),
                               ('tiled-cli-render.png', 'tiled-cli-render-transparent-before-fix.png')]:
        source = HERE / 'preview' / old_name
        destination = HERE / 'preview' / new_name
        if source.exists() and not destination.exists():
            source.rename(destination)
    save(HERE / 'tiled-metadata-fix.json', {
        'rootCauseEvidence': 'Official Tiled JSON export read absent group/object-layer opacity as 0; first rasterizer PNG was fully transparent.',
        'actualReaderObservation': observed, 'changes': changes,
        'imageDimensionsMadeExplicit': True, 'nativePixelsOrRoadGeometryChanged': False,
        'oldInputsWritten': False, 'newTiledSHA256': sha(target),
        'geometryIdentical': graph['nodes'] == old_graph['nodes'] and graph['edges'] == old_graph['edges'],
        'initialFailedRenderRetained': 'preview/tiled-cli-render-transparent-before-fix.png'})
    print(json.dumps({'metadataCorrected': changes, 'geometryIdentical': True,
                      'newTiledSHA256': sha(target)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
