#!/usr/bin/env python3
"""Resume missing records after the parent changed its live progress index."""
import base64
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
CITY = HERE.parent


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if (HERE / 'static-record.json').exists():
        raise SystemExit('Already resumed; preserve subsequent edits.')
    graph_path = HERE / 'navigation/graph.json'
    graph = json.loads(graph_path.read_text())
    if graph['sourceTiledSHA256'] != sha(HERE / 'tiled/compact-three.tmj'):
        raise SystemExit('Map changed since build; preserve it.')
    protected = json.loads((HERE / 'protected-inputs.json').read_text())
    shared = str(CITY / 'planning/progress-current.json')
    changes = [{'path': p, 'beforeSHA256': value, 'currentSHA256': sha(Path(p))} for p, value in protected.items() if sha(Path(p)) != value]
    if any(c['path'] != shared for c in changes):
        raise SystemExit('Immutable production input changed; no restore: ' + repr(changes))
    # This is only a UI status sign. It is not produced D artwork.
    plate = Image.new('RGB', (1472, 960), '#e1e6df')
    draw = ImageDraw.Draw(plate)
    for x in range(-960, 1472, 64):
        draw.line([(x, 0), (x + 960, 960)], fill='#ced6cd', width=2)
    font = ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc', 56)
    draw.multiline_text((260, 350), 'D 尚未制作\n未计入当前三地区', fill='#58695c', font=font, spacing=24)
    plate.save(HERE / 'tiled/D-not-produced-status.png')
    for spec in graph['images']:
        spec['sha256'] = sha(HERE / 'navigation' / spec['file'])
    graph_path.write_text(json.dumps(graph, ensure_ascii=False, indent=2) + '\n')
    composite = Image.new('RGB', (3008, 1984), '#e1e6df')
    for spec in graph['images']:
        im = Image.open(HERE / 'navigation' / spec['file']).convert('RGB')
        composite.paste(im, tuple(spec['offset']))
    composite.save(HERE / 'preview/three-native-pixels.png')
    small = composite.copy(); small.thumbnail((1504, 992)); small.save(HERE / 'preview/three-overview.jpg', quality=93)
    overlay = composite.copy(); draw = ImageDraw.Draw(overlay)
    for edge in graph['edges']:
        draw.line([tuple(p) for p in edge['points']], fill='#ff28b8', width=4, joint='curve')
    overlay.save(HERE / 'preview/actual-roads.png')
    html = (HERE / 'navigation/index.html').read_text()
    for spec in graph['images']:
        binary = (HERE / 'navigation' / spec['file']).read_bytes()
        html = html.replace(spec['file'], 'data:image/png;base64,' + base64.b64encode(binary).decode())
    js = (HERE / 'navigation/navigation.js').read_text()
    html = html.replace('<script src="navigation.js"></script>', '<script>globalThis.__embeddedGraph=' + json.dumps(graph, ensure_ascii=False) + ';\n' + js + '</script>')
    (HERE / 'navigation/offline.html').write_text(html)
    record = {'status': 'new-three-map-awaiting-real-render-and-navigation', 'independentNativeRegions': 3,
              'actualAdmittedRegions': ['A2', 'B1', 'C-001'], 'nodes': len(graph['nodes']), 'edges': len(graph['edges']),
              'components': len(graph['connectedComponents']), 'newTiledSHA256': sha(HERE / 'tiled/compact-three.tmj'),
              'newGraphSHA256': sha(graph_path), 'COffset': [0, 960], 'CCoreStartsAtLocalY': 64,
              'sharedPortalGlobal': [679.5, 1024], 'regionPNGCount': sum(i['role'] == 'region-art' for i in graph['images']),
              'regionPNGBytes': sum((HERE / 'navigation' / i['file']).stat().st_size for i in graph['images'] if i['role'] == 'region-art'),
              'totalReferencedPNGIncludingStatusPlate': len(graph['images']), 'DNativeProduced': False,
              'immutableProductionInputsUnchanged': True, 'sharedParentProgressUpdatesObserved': changes,
              'sharedProgressWrittenOrRestoredByThisThread': False, 'CUserArtAccepted': False,
              'ImagesRequestsForIntegration': 0, 'actualNewNavigationVerified': False, 'TiledCliRenderVerified': False,
              'GUIVerified': False, 'gameTestsOrSaveOperations': False, 'newServiceStarted': False}
    (HERE / 'static-record.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'resumedMissingRecordsOnly': True, 'nodes': len(graph['nodes']), 'edges': len(graph['edges']),
                      'independentRegions': 3, 'externalParentProgressChangeObserved': bool(changes),
                      'immutableProductionInputsUnchanged': True, 'noSourceRestored': True}))


if __name__ == '__main__':
    main()
