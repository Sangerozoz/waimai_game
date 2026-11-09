#!/usr/bin/env python3
"""Build a two-region pixel-space Tiled map and export its actual road vectors."""
import base64
import copy
import hashlib
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ART = HERE.parent.parent
OLD_NAV = ART / '2026-11-05-modular-map-kit/delivery-kit/navigation-pilot'


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export_graph(tiled):
    nodes, edges, lookup = [], [], {}

    def node(point):
        key = tuple(round(v, 6) for v in point)
        if key not in lookup:
            lookup[key] = len(nodes)
            nodes.append({'id': len(nodes), 'pixel': list(key)})
        return lookup[key]

    def walk(layers, offset=(0, 0)):
        for layer in layers:
            off = [offset[k] + layer.get(('offsetx', 'offsety')[k], 0) + layer.get(('x', 'y')[k], 0) for k in (0, 1)]
            if layer['type'] == 'group':
                walk(layer['layers'], off)
            if layer['type'] != 'objectgroup':
                continue
            for obj in layer.get('objects', []):
                if obj.get('type') != 'road' or 'polyline' not in obj:
                    continue
                points = [[off[0] + obj['x'] + p['x'], off[1] + obj['y'] + p['y']] for p in obj['polyline']]
                edges.append({'id': len(edges), 'name': obj['name'], 'from': node(points[0]), 'to': node(points[-1]),
                              'points': points, 'bidirectional': True,
                              'lengthPixels': sum(math.dist(a, b) for a, b in zip(points, points[1:]))})
    walk(tiled['layers'])
    adjacency = {n['id']: [] for n in nodes}
    for edge in edges:
        adjacency[edge['from']].append(edge['to'])
        adjacency[edge['to']].append(edge['from'])
    unseen, components = set(adjacency), []
    while unseen:
        stack, component = [min(unseen)], []
        while stack:
            u = stack.pop()
            if u not in unseen:
                continue
            unseen.remove(u)
            component.append(u)
            stack.extend(adjacency[u])
        components.append(sorted(component))
    return {'coordinateSpace': 'native-image-pixels', 'unitsAreNotMetres': True,
            'source': 'assistant visual tracing of actual A/B native images, re-read from compact-pair.tmj',
            'offsetAppliedOnce': True, 'nodes': nodes, 'edges': edges, 'connectedComponents': components,
            'imageSize': [3008, 1024], 'sourceTiledSHA256': sha(HERE / 'tiled/compact-pair.tmj'),
            'example': {'startPixel': [690, 940], 'endPixel': [2272, 304]},
            'integratedIntoGame': False, 'userAccepted': False}


def main():
    target = HERE / 'tiled/compact-pair.tmj'
    if target.exists():
        raise SystemExit('Existing map; preserve user edits, never initialize again.')
    images = {}
    for region in ['A', 'B']:
        path = HERE / f'native/{region}/native.png'
        provenance = json.loads((path.parent / 'provenance.json').read_text())
        if sha(path) != provenance['sha256']:
            raise ValueError('Native bytes changed.')
        image = Image.open(path).convert('RGB')
        if image.size != (1536, 1024):
            raise ValueError('Actual native size changed; no interpolation or offset guessing.')
        images[region] = image
    for name in ['tiled', 'navigation', 'preview']:
        (HERE / name).mkdir(exist_ok=True)
    # Only lossless core crops. The original returned images remain byte-for-byte.
    a_core = images['A'].crop((0, 0, 1504, 1024))
    b_core = images['B'].crop((32, 0, 1536, 1024))
    a_core.save(HERE / 'tiled/A-core.png')
    b_core.save(HERE / 'tiled/B-core.png')
    pair = Image.new('RGB', (3008, 1024))
    pair.paste(a_core, (0, 0))
    pair.paste(b_core, (1504, 0))
    pair.save(HERE / 'preview/pair-composite.png')
    pair.crop((1240, 425, 1770, 730)).save(HERE / 'preview/seam-1x.png')
    images['A'].crop((360, 230, 1110, 660)).save(HERE / 'preview/market-1x.png')
    overview = pair.copy()
    overview.thumbnail((1504, 512))
    overview.save(HERE / 'preview/pair-overview.jpg', quality=93)
    # Traced from actual artwork, not the structure guide or old city coordinates.
    roads = {
        'A': [
            ('A-west', [(0, 558), (95, 558)]),
            ('A-main-to-south', [(95, 558), (350, 558), (715, 558)]),
            ('A-main-to-loop', [(715, 558), (1105, 558)]),
            ('A-portal', [(1105, 558), (1300, 557), (1504, 558)]),
            ('A-upper-loop', [(95, 558), (120, 474), (149, 367), (180, 280), (204, 243), (260, 231),
                              (500, 217), (730, 203), (870, 197), (911, 220), (959, 305), (1030, 432), (1105, 558)]),
            ('A-south', [(715, 558), (713, 640), (704, 752), (692, 900), (683, 1024)])],
        'B': [
            ('B-portal', [(32, 558), (200, 558), (350, 558)]),
            ('B-main-to-south', [(350, 558), (604, 558)]),
            ('B-main-to-loop', [(604, 558), (1126, 558)]),
            ('B-east', [(1126, 558), (1536, 558)]),
            ('B-upper-loop', [(350, 558), (388, 492), (445, 409), (487, 344), (522, 308),
                              (570, 304), (800, 304), (973, 304), (1016, 325), (1052, 397), (1089, 484), (1126, 558)]),
            ('B-south', [(604, 558), (589, 659), (560, 800), (525, 1024)])]
    }
    layers, layer_id, object_id = [], 1, 1
    for region, offset in [('A', 0), ('B', 1472)]:
        image_layer = {'id': layer_id + 1, 'type': 'imagelayer', 'name': region + ' 整区底图（楼不可单独拖动）',
                       'image': region + '-core.png', 'offsetx': 0 if region == 'A' else 32,
                       'offsety': 0, 'visible': True, 'locked': True, 'opacity': 1}
        objects = []
        for name, points in roads[region]:
            x, y = points[0]
            objects.append({'id': object_id, 'name': name, 'type': 'road', 'x': x, 'y': y,
                            'rotation': 0, 'visible': True,
                            'polyline': [{'x': p[0] - x, 'y': p[1] - y} for p in points],
                            'properties': [{'name': 'traceMethod', 'type': 'string', 'value': 'assistant-actual-native-visual-trace'},
                                           {'name': 'newBusinessBinding', 'type': 'bool', 'value': False}]})
            object_id += 1
        road_layer = {'id': layer_id + 2, 'type': 'objectgroup', 'name': region + ' 可编辑道路中心线',
                      'draworder': 'index', 'visible': True, 'locked': False, 'color': '#ff28b8', 'objects': objects}
        layers.append({'id': layer_id, 'type': 'group', 'name': region + ' 区域（整体偏移仅在此）',
                       'offsetx': offset, 'offsety': 0, 'visible': True, 'locked': False,
                       'properties': [{'name': 'regionId', 'type': 'string', 'value': region},
                                      {'name': 'nativeSHA256', 'type': 'string', 'value': sha(HERE / f'native/{region}/native.png')}],
                       'layers': [image_layer, road_layer]})
        layer_id += 3
    layers.append({'id': layer_id, 'type': 'objectgroup', 'name': '边界、停靠及独立装饰（可编辑，当前空白）',
                   'objects': [], 'visible': True, 'locked': False, 'draworder': 'index'})
    doc = {'type': 'map', 'version': '1.10', 'tiledversion': '1.12.2', 'orientation': 'orthogonal',
           'renderorder': 'right-down', 'width': 94, 'height': 32, 'tilewidth': 32, 'tileheight': 32,
           'infinite': False, 'backgroundcolor': '#a3ae8c', 'nextobjectid': object_id,
           'nextlayerid': layer_id + 1, 'tilesets': [], 'layers': layers,
           'properties': [{'name': 'coordinateSpace', 'type': 'string', 'value': 'native-image-pixels-not-metres'},
                          {'name': 'pixelCanvasWidth', 'type': 'int', 'value': 3008},
                          {'name': 'pixelCanvasHeight', 'type': 'int', 'value': 1024},
                          {'name': 'newBusinessBindings', 'type': 'int', 'value': 0}]}
    save(target, doc)
    graph = export_graph(json.loads(target.read_text()))
    if len(graph['connectedComponents']) != 1:
        raise ValueError('Disconnected traced graph; do not manufacture a cross-region link.')
    save(HERE / 'navigation/graph.json', graph)
    overlay = pair.copy()
    draw = ImageDraw.Draw(overlay)
    for edge in graph['edges']:
        draw.line([tuple(p) for p in edge['points']], fill='#ff28b8', width=4, joint='curve')
    draw.line([(1504, 0), (1504, 1024)], fill='#df8c28', width=2)
    overlay.save(HERE / 'preview/traced-pair.png')
    # Reuse the existing independent navigator; modify only this new copy's inputs.
    js = (OLD_NAV / 'navigation.js').read_text()
    js = js.replace('state.start = nearestRoad([1182, 100]); state.end = nearestRoad([200, 548]);',
                    'state.start = nearestRoad(state.graph.example.startPixel); state.end = nearestRoad(state.graph.example.endPixel);')
    js = js.replace('这里不在已确认路网上；左下错误车道也不参与导航。请点靠近主路中心的位置。',
                    '这里不在本次按图描出的路网上；请点道路中心附近。')
    original_load = "const response = await fetch('graph.json', {cache: 'no-store'});\n    if (!response.ok) throw new Error(`路网读取失败 HTTP ${response.status}`);\n    const graph = await response.json();"
    replacement_load = "const graph = globalThis.__embeddedGraph || await (async () => { const r = await fetch('graph.json', {cache:'no-store'}); if (!r.ok) throw new Error('graph HTTP '+r.status); return r.json(); })();"
    if original_load not in js:
        raise RuntimeError('Existing navigator changed; inspect rather than guessing replacement.')
    js = js.replace(original_load, replacement_load)
    js = js.replace("decoded.src = 'native-city-block.png';", "decoded.src = $('city').getAttribute('href');")
    js = js.replace('decoded.naturalWidth !== 1536 || decoded.naturalHeight !== 1024',
                    'decoded.naturalWidth !== graph.imageSize[0] || decoded.naturalHeight !== graph.imageSize[1]')
    (HERE / 'navigation/navigation.js').write_text(js)
    html = (OLD_NAV / 'index.html').read_text()
    html = html.replace('小街区｜路网与导航对齐', '紧凑相邻两区｜独立导航')
    html = html.replace('小街区：路网与导航对齐', 'A 商业生活核心 ↔ B 住宅文教')
    html = html.replace('在已确认道路上依次点起点、终点，或直接看示例。左下错误车道已从导航中排除。',
                        '两张真实原生各1536×1024，64px重叠按核心裁切。点击道路选点，或播放跨区示例。')
    html = html.replace('示例：上方 → 左侧', '示例：A 南路 → B 校园')
    html = html.replace('viewBox="0 0 1536 1024"', 'viewBox="0 0 3008 1024"')
    html = html.replace('href="native-city-block.png"', 'href="../preview/pair-composite.png"')
    html = html.replace('width="1536" height="1024"', 'width="3008" height="1024"')
    html = html.replace('原图左下车道待美术修正，点击该处不会创建导航。',
                        '本轮仅两区候选；接缝纹理、树形及小物仍待用户确认。不是全城美术验收。')
    html = html.replace('导航路网.tmj', '../tiled/compact-pair.tmj')
    (HERE / 'navigation/index.html').write_text(html)
    # Existing 4186 only serves the old modular kit. No service/root/global changes.
    # A fully self-contained local page avoids file:// fetch restrictions honestly.
    image_data = 'data:image/png;base64,' + base64.b64encode((HERE / 'preview/pair-composite.png').read_bytes()).decode()
    offline = html.replace('../preview/pair-composite.png', image_data)
    offline = offline.replace('<script src="navigation.js"></script>',
                              '<script>globalThis.__embeddedGraph=' + json.dumps(graph, ensure_ascii=False) + ';\n' + js + '</script>')
    (HERE / 'navigation/offline.html').write_text(offline)
    protected = json.loads((HERE / 'protected-inputs.json').read_text())
    changed = [p for p, value in protected.items() if sha(Path(p)) != value]
    if changed:
        raise RuntimeError('Readonly inputs changed; report without restoring: ' + repr(changed))
    save(HERE / 'build-record.json', {
        'nativeSizes': {'A': [1536, 1024], 'B': [1536, 1024]},
        'nativeTotalBytes': sum((HERE / f'native/{r}/native.png').stat().st_size for r in ['A', 'B']),
        'imageOffsets': {'A': [0, 0], 'B': [1472, 0]}, 'overlap': 64,
        'coreCropBoxes': {'A': [0, 0, 1504, 1024], 'B': [32, 0, 1536, 1024]},
        'sharedNodeGlobalPixel': [1504, 558], 'noNativeRescaleOrWarp': True,
        'portalObservation': 'A native road center near556, B near558, common traced center558 remains within actual visible asphalt; no native road moved.',
        'tiled': 'tiled/compact-pair.tmj', 'graph': 'navigation/graph.json',
        'nodes': len(graph['nodes']), 'edges': len(graph['edges']), 'components': len(graph['connectedComponents']),
        'offsetAppliedOnce': True, 'sourceTiledSHA256': graph['sourceTiledSHA256'],
        'sourceProtectionUnchanged': True, 'changedReadonlyInputs': changed,
        'httpService': {'existingPort': 4186, 'existingRoot': str(ART / '2026-11-05-modular-map-kit'),
                        'coversThisNewWriteSet': False, 'newServiceStarted': False,
                        'fallback': 'self-contained navigation/offline.html, no network fetch or new port'},
        'runtimeNavigationVerified': False, 'tiledNativeGUIOpened': False,
        'gameTestsRun': False, 'userAccepted': False, 'wholeCityComplete': False})
    print(json.dumps({'tiled': str(target), 'graphNodes': len(graph['nodes']), 'graphEdges': len(graph['edges']),
                      'connectedComponents': len(graph['connectedComponents']), 'readonlyInputsUnchanged': True}))


if __name__ == '__main__':
    main()
