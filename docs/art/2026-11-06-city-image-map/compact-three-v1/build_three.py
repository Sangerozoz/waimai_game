#!/usr/bin/env python3
"""Build a new A2/B1/C pixel map without changing any old region or source."""
import base64
import copy
import hashlib
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
CITY = HERE.parent
BASE = CITY / 'compact-pair-v2-density/integration'
CROOT = CITY / 'regions/C-001'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text())


def save(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def properties(obj):
    return {p['name']: p['value'] for p in obj.get('properties', [])}


def graph_from_map(doc):
    nodes, edges, image_rows, lookup = [], [], [], {}
    def node(p):
        key = tuple(round(v, 6) for v in p)
        if key not in lookup:
            lookup[key] = len(nodes)
            nodes.append({'id': len(nodes), 'pixel': list(key)})
        return lookup[key]
    def walk(layers, offset=(0, 0), region=None):
        for layer in layers:
            off = [offset[k] + layer.get(('offsetx', 'offsety')[k], 0) + layer.get(('x', 'y')[k], 0) for k in (0, 1)]
            pr = properties(layer)
            if layer['type'] == 'group':
                walk(layer['layers'], off, pr.get('regionId', region))
            elif layer['type'] == 'imagelayer':
                file = HERE / 'tiled' / layer['image']
                with Image.open(file) as im:
                    size = list(im.size)
                image_rows.append({'elementId': 'city' + (region or 'D'), 'file': '../tiled/' + layer['image'],
                                   'offset': off, 'size': size, 'sha256': sha(file),
                                   'nativeSourceSHA256': pr.get('nativeSourceSHA256'),
                                   'role': 'unproduced-D-status-only' if region is None else 'region-art'})
            elif layer['type'] == 'objectgroup':
                for obj in layer.get('objects', []):
                    if obj.get('type') != 'road':
                        continue
                    points = [[off[0] + obj['x'] + p['x'], off[1] + obj['y'] + p['y']] for p in obj['polyline']]
                    edges.append({'id': len(edges), 'name': obj['name'], 'from': node(points[0]), 'to': node(points[-1]),
                                  'points': points, 'bidirectional': True,
                                  'lengthPixels': sum(math.dist(a, b) for a, b in zip(points, points[1:]))})
    walk(doc['layers'])
    signatures, duplicates = set(), []
    for e in edges:
        p = tuple(tuple(p) for p in e['points'])
        signature = min(p, p[::-1])
        if signature in signatures:
            duplicates.append(e['name'])
        signatures.add(signature)
    adjacency = {n['id']: [] for n in nodes}
    for e in edges:
        adjacency[e['from']].append(e['to']); adjacency[e['to']].append(e['from'])
    unseen, components = set(adjacency), []
    while unseen:
        pending, part = [min(unseen)], []
        while pending:
            u = pending.pop()
            if u not in unseen:
                continue
            unseen.remove(u); part.append(u); pending.extend(adjacency[u])
        components.append(sorted(part))
    crossings = []
    for i, first in enumerate(edges):
        for second in edges[i + 1:]:
            for a, b in zip(first['points'], first['points'][1:]):
                for c, d in zip(second['points'], second['points'][1:]):
                    r = [b[k] - a[k] for k in (0, 1)]; s = [d[k] - c[k] for k in (0, 1)]
                    cross = r[0] * s[1] - r[1] * s[0]
                    if abs(cross) < 1e-8:
                        continue
                    q = [c[k] - a[k] for k in (0, 1)]
                    t = (q[0] * s[1] - q[1] * s[0]) / cross
                    v = (q[0] * r[1] - q[1] * r[0]) / cross
                    if -1e-8 <= t <= 1 + 1e-8 and -1e-8 <= v <= 1 + 1e-8:
                        hit = [a[k] + t * r[k] for k in (0, 1)]
                        if min(math.dist(hit, n['pixel']) for n in nodes) > 1e-6:
                            crossings.append({'roads': [first['name'], second['name']], 'point': hit})
    if len(components) != 1 or duplicates or crossings:
        raise ValueError('Do not fake connectivity: ' + repr((components, duplicates, crossings)))
    return {'coordinateSpace': 'native-image-pixels-not-metres', 'sourceTiledSHA256': sha(HERE / 'tiled/compact-three.tmj'),
            'nodes': nodes, 'edges': edges, 'connectedComponents': components, 'duplicateEdges': duplicates,
            'unmergedCrossings': crossings, 'imageSize': [3008, 1984], 'images': image_rows,
            'independentRegions': ['A', 'B', 'C'], 'DProduced': False, 'offsetAppliedOnce': True,
            'example': {'startPixel': [573, 1910], 'endPixel': [2272, 304]}, 'newBusinessBindings': 0}


def main():
    if (HERE / 'tiled/compact-three.tmj').exists():
        raise SystemExit('Map exists: preserve possible user work.')
    known = {'README.md', 'build_three.py'}
    if any(p.name not in known for p in HERE.iterdir()):
        raise SystemExit('Unexpected existing three-region content; no clearing.')
    protected = read(CROOT / 'protected-inputs.json')
    protected.update({str(p): sha(p) for p in BASE.rglob('*') if p.is_file()})
    save(HERE / 'protected-inputs.json', protected)
    for directory in ['tiled', 'navigation', 'preview', 'sources']:
        (HERE / directory).mkdir(exist_ok=True)
    cpath = CROOT / 'native.png'
    cp = read(CROOT / 'provenance.json')
    if sha(cpath) != cp['nativeSHA256']:
        raise SystemExit('C native changed.')
    c = Image.open(cpath).convert('RGB')
    if c.size != (1536, 1024):
        raise SystemExit('Unexpected C size; no interpolation.')
    (HERE / 'sources/C-001-native.png').write_bytes(cpath.read_bytes())
    for file in ['A2-core.png', 'B1-core.png']:
        (HERE / 'tiled' / file).write_bytes((BASE / 'tiled' / file).read_bytes())
    c.crop((0, 64, 1536, 1024)).save(HERE / 'tiled/C-core.png')
    # Explicit UI-only status plate, NOT a generated D region or terrain.
    placeholder = Image.new('RGB', (1472, 960), '#e1e6df')
    pdraw = ImageDraw.Draw(placeholder)
    for x in range(-960, 1472, 64):
        pdraw.line([(x, 0), (x + 960, 960)], fill='#ced6cd', width=2)
    font_path = Path('/System/Library/Fonts/STHeiti Medium.ttc')
    font = ImageFont.truetype(str(font_path), 56) if font_path.exists() else ImageFont.load_default()
    label = 'D 尚未制作\n未计入当前三地区' if font_path.exists() else 'D NOT PRODUCED\nNOT PART OF THE THREE REGIONS'
    pdraw.multiline_text((260, 350), label, fill='#58695c', font=font, spacing=24)
    placeholder.save(HERE / 'tiled/D-not-produced-status.png')
    doc = copy.deepcopy(read(BASE / 'tiled/compact-pair-a2-b1.tmj'))
    next_layer = doc['nextlayerid']; next_object = doc['nextobjectid']
    roads = [
        ('C-north-portal', [(679.5, 64), (674, 120), (662, 226)]),
        ('C-spine-to-cross', [(662, 226), (644, 420), (631.5, 540)]),
        ('C-south', [(631.5, 540), (618, 650), (600, 800), (578, 900), (559.5, 1024)]),
        ('C-west', [(0, 540), (174, 540)]),
        ('C-main-west', [(174, 540), (631.5, 540)]),
        ('C-main-middle', [(631.5, 540), (1050, 540)]),
        ('C-east', [(1050, 540), (1536, 540)]),
        ('C-upper-loop', [(174, 540), (240, 340), (267, 279), (292, 254), (335, 246), (510, 235), (662, 226)]),
        ('C-service-road', [(1050, 540), (1082, 660), (1134, 820), (1190, 1024)])]
    objects = []
    for name, pts in roads:
        x, y = pts[0]
        objects.append({'id': next_object, 'name': name, 'type': 'road', 'x': x, 'y': y, 'width': 0, 'height': 0,
                        'visible': True, 'rotation': 0, 'opacity': 1,
                        'polyline': [{'x': p[0] - x, 'y': p[1] - y} for p in pts],
                        'properties': [{'name': 'traceMethod', 'type': 'string', 'value': 'assistant visual trace of actual C native'},
                                       {'name': 'newBusinessBinding', 'type': 'bool', 'value': False}]})
        next_object += 1
    doc['layers'].append({'id': next_layer, 'type': 'group', 'name': 'C 工坊服务／城市庭院', 'offsetx': 0, 'offsety': 960,
                          'visible': True, 'opacity': 1, 'locked': False,
                          'properties': [{'name': 'regionId', 'type': 'string', 'value': 'C'}],
                          'layers': [{'id': next_layer + 1, 'type': 'imagelayer', 'name': 'C核心（北64px归既有图）',
                                      'image': 'C-core.png', 'imagewidth': 1536, 'imageheight': 960,
                                      'offsetx': 0, 'offsety': 64, 'visible': True, 'opacity': 1, 'locked': True,
                                      'properties': [{'name': 'nativeSourceSHA256', 'type': 'string', 'value': cp['nativeSHA256']}]},
                                     {'id': next_layer + 2, 'type': 'objectgroup', 'name': 'C 可编辑道路中心线',
                                      'draworder': 'index', 'visible': True, 'opacity': 1, 'locked': False, 'color': '#ff28b8', 'objects': objects}]})
    doc['layers'].insert(0, {'id': next_layer + 3, 'type': 'imagelayer', 'name': 'D尚未制作（非地图状态牌）',
                             'image': 'D-not-produced-status.png', 'imagewidth': 1472, 'imageheight': 960,
                             'offsetx': 1536, 'offsety': 1024, 'visible': True, 'opacity': 1, 'locked': True})
    doc.update({'width': 94, 'height': 62, 'nextlayerid': next_layer + 4, 'nextobjectid': next_object})
    for prop in doc['properties']:
        if prop['name'] == 'pixelCanvasHeight':
            prop['value'] = 1984
    save(HERE / 'tiled/compact-three.tmj', doc)
    graph = graph_from_map(read(HERE / 'tiled/compact-three.tmj'))
    save(HERE / 'navigation/graph.json', graph)
    composite = Image.new('RGB', (3008, 1984), '#e1e6df')
    for spec in graph['images']:
        im = Image.open(HERE / 'navigation' / spec['file']).convert('RGB')
        composite.paste(im, tuple(spec['offset']))
    composite.save(HERE / 'preview/three-native-pixels.png')
    small = composite.copy(); small.thumbnail((1504, 992)); small.save(HERE / 'preview/three-overview.jpg', quality=93)
    composite.crop((550, 900, 815, 1180)).save(HERE / 'preview/C-north-seam-1x.png')
    c.crop((780, 100, 1536, 530)).save(HERE / 'preview/C-workshop-1x.png')
    overlay = composite.copy(); draw = ImageDraw.Draw(overlay)
    for edge in graph['edges']:
        draw.line([tuple(p) for p in edge['points']], fill='#ff28b8', width=4, joint='curve')
    overlay.save(HERE / 'preview/actual-roads.png')
    js = (BASE / 'navigation/navigation.js').read_text()
    (HERE / 'navigation/navigation.js').write_text(js)
    html = (BASE / 'navigation/index.html').read_text()
    old_images = '<image id="cityA" href="../tiled/A2-core.png" x="0" y="0" width="1504" height="1024"/><image id="cityB" href="../tiled/B1-core.png" x="1504" y="0" width="1504" height="1024"/>'
    new_images = '<image id="cityD" href="../tiled/D-not-produced-status.png" x="1536" y="1024" width="1472" height="960"/>' + old_images + '<image id="cityC" href="../tiled/C-core.png" x="0" y="1024" width="1536" height="960"/>'
    if old_images not in html:
        raise RuntimeError('Existing navigator shell changed; no guessed replacement.')
    html = html.replace(old_images, new_images).replace('viewBox="0 0 3008 1024"', 'viewBox="0 0 3008 1984"')
    html = html.replace('完整A2城市核心 ↔ 原B1住宅文教', '新C工坊庭院 → A2城市核心 → B1住宅文教')
    html = html.replace('示例：A 南路 → B 校园', '示例：C → A2 → B1')
    html = html.replace('本轮实际加载完整获认可A2的核心及原B1，逐图校验SHA；新道路副本和新运行证据，不套用旧到达结果。',
                        '实际加载A2/B1/C三张区域图，D灰色状态牌表示尚未制作。新C道路和新跨三地区证据，不套旧两区到达。')
    html = html.replace('../tiled/compact-pair-a2-b1.tmj', '../tiled/compact-three.tmj')
    (HERE / 'navigation/index.html').write_text(html)
    offline = html
    for spec in graph['images']:
        binary = (HERE / 'navigation' / spec['file']).read_bytes()
        offline = offline.replace(spec['file'], 'data:image/png;base64,' + base64.b64encode(binary).decode())
    offline = offline.replace('<script src="navigation.js"></script>', '<script>globalThis.__embeddedGraph=' + json.dumps(graph, ensure_ascii=False) + ';\n' + js + '</script>')
    (HERE / 'navigation/offline.html').write_text(offline)
    shared_progress = str(CITY / 'planning/progress-current.json')
    changed = [p for p, value in protected.items() if sha(Path(p)) != value and p != shared_progress]
    if changed:
        raise RuntimeError('Protected input changed; no restore: ' + repr(changed))
    save(HERE / 'static-record.json', {'status': 'new-three-map-awaiting-real-render-and-navigation', 'independentNativeRegions': 3,
         'actualAdmittedRegions': ['A2', 'B1', 'C-001'], 'nativeC': {'path': str(cpath), 'sha256': sha(cpath), 'size': list(c.size)},
         'COffset': [0, 960], 'CCoreStartsAtLocalY': 64, 'sharedPortalGlobal': [679.5, 1024],
         'CActualNorthAsphaltAtY64': [653, 705], 'A2ActualAsphaltAtY1023': [653, 706],
         'note': 'C center near679 differs from679.5 reference by about half a pixel; widths53/54 have a one-pixel difference, no warp or painted-road repair.',
         'newTiledSHA256': sha(HERE / 'tiled/compact-three.tmj'), 'newGraphSHA256': sha(HERE / 'navigation/graph.json'),
         'nodes': len(graph['nodes']), 'edges': len(graph['edges']), 'components': len(graph['connectedComponents']),
         'regionPNGCount': sum(i['role'] == 'region-art' for i in graph['images']),
         'regionPNGBytes': sum((HERE / 'navigation' / i['file']).stat().st_size for i in graph['images'] if i['role'] == 'region-art'),
         'totalReferencedPNGIncludingStatusPlate': len(graph['images']), 'DNativeProduced': False,
         'protectedInputsUnchanged': True, 'CUserArtAccepted': False, 'ImagesRequestsForIntegration': 0,
         'actualNewNavigationVerified': False, 'TiledCliRenderVerified': False, 'GUIVerified': False,
         'gameTestsOrSaveOperations': False, 'newServiceStarted': False})
    print(json.dumps({'map': str(HERE / 'tiled/compact-three.tmj'), 'nodes': len(graph['nodes']), 'edges': len(graph['edges']),
                      'components': len(graph['connectedComponents']), 'admittedRegions': 3, 'DProduced': False}))


if __name__ == '__main__':
    main()
