#!/usr/bin/env python3
"""Admit approved complete A2/B1 into a new pixel-space map and navigator."""
import base64
import copy
import hashlib
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
DENSITY = HERE.parent
CITY = DENSITY.parent
OLD = CITY / 'compact-pair-v1'
ROOT = CITY.parents[2]
CORE_X = 1504


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def props(obj):
    return {p['name']: p['value'] for p in obj.get('properties', [])}


def protected_files():
    files = [p for p in OLD.rglob('*') if p.is_file()]
    files += [p for p in DENSITY.rglob('*') if p.is_file() and HERE not in p.parents]
    files += [ROOT / 'delivery-game/assets/resources/map-sample/city.json', CITY / 'planning/current-scope.json',
              CITY / 'planning/compact-layout-v1.json']
    return {str(p): sha(p) for p in sorted(set(files))}


def export_graph(doc):
    nodes, edges, lookup, images = [], [], {}, []
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
            elif layer['type'] == 'imagelayer':
                path = (HERE / 'tiled' / layer['image']).resolve()
                with Image.open(path) as im:
                    dimensions = list(im.size)
                images.append({'elementId': 'cityA' if off[0] == 0 else 'cityB',
                               'file': '../tiled/' + layer['image'], 'size': dimensions,
                               'offset': off, 'sha256': sha(path),
                               'nativeSourceSHA256': props(layer)['nativeSourceSHA256']})
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
    for edge in edges:
        forward = tuple(tuple(p) for p in edge['points'])
        key = min(forward, forward[::-1])
        if key in signatures:
            duplicates.append(edge['name'])
        signatures.add(key)
    adjacency = {n['id']: [] for n in nodes}
    for e in edges:
        adjacency[e['from']].append(e['to'])
        adjacency[e['to']].append(e['from'])
    unseen, components = set(adjacency), []
    while unseen:
        pending, part = [min(unseen)], []
        while pending:
            u = pending.pop()
            if u not in unseen:
                continue
            unseen.remove(u)
            part.append(u)
            pending.extend(adjacency[u])
        components.append(sorted(part))
    # Every visible at-grade crossing must have an explicit graph node.
    missing_intersections = []
    node_points = [n['pixel'] for n in nodes]
    for i, e1 in enumerate(edges):
        for e2 in edges[i + 1:]:
            for a, b in zip(e1['points'], e1['points'][1:]):
                for c, d in zip(e2['points'], e2['points'][1:]):
                    r = [b[k] - a[k] for k in (0, 1)]
                    s = [d[k] - c[k] for k in (0, 1)]
                    cross = r[0] * s[1] - r[1] * s[0]
                    if abs(cross) < 1e-8:
                        continue
                    q = [c[k] - a[k] for k in (0, 1)]
                    t = (q[0] * s[1] - q[1] * s[0]) / cross
                    v = (q[0] * r[1] - q[1] * r[0]) / cross
                    if -1e-8 <= t <= 1 + 1e-8 and -1e-8 <= v <= 1 + 1e-8:
                        hit = [a[k] + t * r[k] for k in (0, 1)]
                        if min(math.dist(hit, p) for p in node_points) > 1e-6:
                            missing_intersections.append({'roads': [e1['name'], e2['name']], 'point': hit})
    if duplicates or missing_intersections or len(components) != 1:
        raise ValueError('Actual vector connectivity requires attention: ' + repr((duplicates, missing_intersections, components)))
    return {'coordinateSpace': 'native-image-pixels-not-metres', 'source': 'new A2/B1 Tiled copy, checked on complete approved artwork',
            'sourceTiledSHA256': sha(HERE / 'tiled/compact-pair-a2-b1.tmj'), 'nodes': nodes, 'edges': edges,
            'connectedComponents': components, 'duplicateEdges': duplicates, 'unmergedCrossings': missing_intersections,
            'offsetAppliedOnce': True, 'imageSize': [3008, 1024], 'images': images,
            'example': {'startPixel': [690, 940], 'endPixel': [2272, 304]},
            'newBusinessBindings': 0, 'integratedIntoGame': False}


def main():
    target = HERE / 'tiled/compact-pair-a2-b1.tmj'
    if target.exists():
        raise SystemExit('New map already exists; preserve possible user editing.')
    known = {'README.md', 'build_integration.py', 'tmxrasterizer-help.txt', 'tmxrasterizer-cocoa-help.txt'}
    unknown = [p.name for p in HERE.iterdir() if p.name not in known]
    if unknown:
        raise SystemExit('Unknown existing integration content: ' + repr(unknown))
    before = protected_files()
    save(HERE / 'protected-inputs.json', before)
    sources = {'A2': DENSITY / 'native/A-v2-api.png', 'B1': OLD / 'native/B/native.png'}
    expected = {'A2': '6b6cdf35fad8fc64e593a1c97571e99cc58fc809854b201e9e685e226c3028fe',
                'B1': '9ea79c46fbf16d8fea278fdcea9fb127e535c9041beeb7875ff047ecaf794baf'}
    for directory in ['sources', 'tiled', 'navigation', 'preview', 'next-C']:
        (HERE / directory).mkdir(exist_ok=True)
    images = {}
    for key, path in sources.items():
        if sha(path) != expected[key]:
            raise SystemExit('Source SHA mismatch: ' + key)
        (HERE / 'sources' / (key + '-native.png')).write_bytes(path.read_bytes())
        images[key] = Image.open(path).convert('RGB')
        if images[key].size != (1536, 1024):
            raise ValueError('Actual image dimensions changed; no interpolation.')
    images['A2'].crop((0, 0, CORE_X, 1024)).save(HERE / 'tiled/A2-core.png')
    images['B1'].crop((CORE_X - 1472, 0, 1536, 1024)).save(HERE / 'tiled/B1-core.png')
    pair = Image.new('RGB', (3008, 1024))
    pair.paste(images['A2'].crop((0, 0, CORE_X, 1024)), (0, 0))
    pair.paste(images['B1'].crop((CORE_X - 1472, 0, 1536, 1024)), (CORE_X, 0))
    pair.save(HERE / 'preview/pair-native-pixels.png')
    small = pair.copy()
    small.thumbnail((1504, 512))
    small.save(HERE / 'preview/pair-overview.jpg', quality=94)
    pair.crop((1200, 250, 1820, 660)).save(HERE / 'preview/east-building-and-seam-1x.png')
    pair.crop((1380, 470, 1660, 640)).save(HERE / 'preview/road-seam-1x.png')
    images['A2'].crop((1200, 0, 1536, 520)).save(HERE / 'preview/A2-east-whole-building-1x.png')
    marked = images['A2'].copy()
    draw = ImageDraw.Draw(marked)
    draw.line([(CORE_X, 0), (CORE_X, 1024)], fill='#00dcff', width=2)
    marked.crop((1380, 0, 1536, 1024)).save(HERE / 'preview/core-boundary-evidence.png')
    doc = copy.deepcopy(read(OLD / 'tiled/compact-pair.tmj'))
    corrections = []
    for group in doc['layers']:
        if group['type'] != 'group':
            continue
        region = props(group)['regionId']
        source_key = 'A2' if region == 'A' else 'B1'
        group['name'] = source_key + ' 区域（整体偏移仅在此）'
        for item in group.get('properties', []):
            if item['name'] == 'nativeSHA256':
                item['value'] = expected[source_key]
        for layer in group['layers']:
            if layer['type'] == 'imagelayer':
                key = 'A2' if region == 'A' else 'B1'
                layer.update({'image': key + '-core.png', 'offsetx': 0 if region == 'A' else CORE_X - 1472,
                              'offsety': 0, 'name': key + ' 完整原生的无损核心',
                              'properties': [{'name': 'nativeSourceSHA256', 'type': 'string', 'value': expected[key]}]})
            for obj in layer.get('objects', []):
                if region != 'A' or obj.get('type') != 'road':
                    continue
                old = [[obj['x'] + p['x'], obj['y'] + p['y']] for p in obj['polyline']]
                pts = copy.deepcopy(old)
                if obj['name'] in ['A-west', 'A-main-to-south', 'A-main-to-loop']:
                    for p in pts:
                        p[1] = 556
                elif obj['name'] == 'A-portal':
                    pts = [[1155, 556], [1300, 556], [CORE_X, 558]]
                elif obj['name'] == 'A-upper-loop':
                    pts[0][1] = 556
                    pts[-1][1] = 556
                elif obj['name'] == 'A-south':
                    pts[0][1] = 556
                    pts[-1] = [679.5, 1024]
                if old != pts:
                    corrections.append({'road': obj['name'], 'before': old, 'after': pts,
                                        'reason': 'New A2 visible centerline/exit correction only, no raster movement.'})
                obj['x'], obj['y'] = pts[0]
                obj['polyline'] = [{'x': p[0] - pts[0][0], 'y': p[1] - pts[0][1]} for p in pts]
    def explicit_layer_fields(layers):
        for layer in layers:
            layer['opacity'] = 1
            if layer['type'] == 'group':
                explicit_layer_fields(layer['layers'])
            elif layer['type'] == 'imagelayer':
                with Image.open(HERE / 'tiled' / layer['image']) as raster:
                    layer['imagewidth'], layer['imageheight'] = raster.size
    explicit_layer_fields(doc['layers'])
    doc['properties'].append({'name': 'artworkVersion', 'type': 'string', 'value': 'approved complete A2 + original B1; no clipped mask composite'})
    save(target, doc)
    graph = export_graph(read(target))
    save(HERE / 'navigation/graph.json', graph)
    save(HERE / 'road-adjustments.json', corrections)
    overlay = pair.copy()
    draw = ImageDraw.Draw(overlay)
    for edge in graph['edges']:
        draw.line([tuple(p) for p in edge['points']], fill='#f82bba', width=4, joint='curve')
    overlay.save(HERE / 'preview/actual-road-overlay.png')
    js = (OLD / 'navigation/navigation.js').read_text()
    old_decode = "const decoded = new Image();\n    decoded.src = $('city').getAttribute('href');\n    await decoded.decode();\n    if (decoded.naturalWidth !== graph.imageSize[0] || decoded.naturalHeight !== graph.imageSize[1]) throw new Error('底图像素尺寸与路网不一致');\n    const rect = $('city').getBoundingClientRect();\n    if (!rect.width || !rect.height) throw new Error('底图没有可见尺寸');"
    new_decode = """state.loadedImages = await Promise.all(graph.images.map(async spec => {
      const el = $(spec.elementId), href = el.getAttribute('href');
      const decoded = new Image(); decoded.src = href; await decoded.decode();
      if (decoded.naturalWidth !== spec.size[0] || decoded.naturalHeight !== spec.size[1]) throw new Error('区域图片尺寸不一致');
      const bytes = await (await fetch(href)).arrayBuffer();
      const digest = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))).map(v => v.toString(16).padStart(2,'0')).join('');
      if (digest !== spec.sha256) throw new Error('实际加载图片SHA不匹配');
      const rect = el.getBoundingClientRect(); if (!rect.width || !rect.height) throw new Error('区域图片未显示');
      return {elementId:spec.elementId, sha256:digest, nativeSourceSHA256:spec.nativeSourceSHA256, decodedSize:[decoded.naturalWidth,decoded.naturalHeight], displayed:true};
    }));"""
    if old_decode not in js:
        raise RuntimeError('Navigator source changed; inspect rather than guessing.')
    js = js.replace(old_decode, new_decode)
    js = js.replace("graphSourceSHA256: state.graph?.sourceTiledSHA256 ?? null", "loadedImages: state.loadedImages ?? [], graphSourceSHA256: state.graph?.sourceTiledSHA256 ?? null")
    (HERE / 'navigation/navigation.js').write_text(js)
    html = (OLD / 'navigation/index.html').read_text()
    old_image = '<image id="city" href="../preview/pair-composite.png" x="0" y="0" width="3008" height="1024"/>'
    new_images = '<image id="cityA" href="../tiled/A2-core.png" x="0" y="0" width="1504" height="1024"/><image id="cityB" href="../tiled/B1-core.png" x="1504" y="0" width="1504" height="1024"/>'
    if old_image not in html:
        raise RuntimeError('Navigator HTML source changed.')
    html = html.replace(old_image, new_images).replace('A 商业生活核心 ↔ B 住宅文教', '完整A2城市核心 ↔ 原B1住宅文教')
    html = html.replace('两张真实原生各1536×1024，64px重叠按核心裁切。点击道路选点，或播放跨区示例。',
                        '本轮实际加载完整获认可A2的核心及原B1，逐图校验SHA；新道路副本和新运行证据，不套用旧到达结果。')
    html = html.replace('本轮仅两区候选；接缝纹理、树形及小物仍待用户确认。不是全城美术验收。',
                        'A2美术方向/密度已获认可；技术接入独立核验，不表示全城或正式游戏通过。')
    html = html.replace('../tiled/compact-pair.tmj', '../tiled/compact-pair-a2-b1.tmj')
    (HERE / 'navigation/index.html').write_text(html)
    offline = html
    for image in graph['images']:
        binary = (HERE / 'navigation' / image['file']).read_bytes()
        offline = offline.replace(image['file'], 'data:image/png;base64,' + base64.b64encode(binary).decode())
    offline = offline.replace('<script src="navigation.js"></script>', '<script>globalThis.__embeddedGraph=' + json.dumps(graph, ensure_ascii=False) + ';\n' + js + '</script>')
    (HERE / 'navigation/offline.html').write_text(offline)
    # C remains a contract only. The band follows actual A2/B1 core ownership.
    pair.crop((0, 960, 1536, 1024)).save(HERE / 'next-C/actual-north-edge-64.png')
    delta = [-12.5, 124]
    magnitude = math.hypot(*delta)
    save(HERE / 'next-C/identity-and-edge-contract.json', {
        'status': 'contract-only-no-image-request', 'identity': 'workshop service plus urban housing transitioning toward courtyards',
        'styleAndDensity': 'Urban portion follows accepted A2 density and painting; become sparser only toward suburban gardens. No repeated market hall/villa kit or all-vegetable landscape.',
        'source': '../../../planning/compact-layout-v1.json', 'proposedNativeSizeReference': [1536, 1024],
        'proposedWorldOffset': [0, 960], 'northOverlapPixels': 64,
        'coreOwnership': 'Existing A2/B1 own y<1024; proposed C core starts at local y64/global y1024, no clipping existing frontage.',
        'actualNorthernBand': 'actual-north-edge-64.png', 'actualBandGlobalBounds': [0, 960, 1536, 1024],
        'bandContainsA2AndB1CoreOwnershipAtCorner': True,
        'portal': {'sourceRoad': 'A-south', 'globalPixel': [679.5, 1024], 'CNativePixel': [679.5, 64],
                   'asphaltWidthObservedNearBoundaryPixels': 54, 'observation': 'Native y1023 neutral-asphalt span x653..706, supported by visual road inspection; not metre calibration.',
                   'southwardUnitDirection': [v / magnitude for v in delta]},
        'protect': ['Existing full A2/B1 pixels and complete frontage', 'same road/person/building readable scale', 'no density homogenization across whole city'],
        'nativeGenerated': False, 'ImagesRequestsThisRound': 0, 'worldMetresEstablished': False, 'finalGridFrozen': False})
    after = protected_files()
    if before != after:
        raise RuntimeError('Readonly input changed; report without restoring it.')
    save(HERE / 'static-record.json', {
        'A2Source': {'path': str(sources['A2']), 'sha256': expected['A2'], 'bytes': sources['A2'].stat().st_size},
        'B1Source': {'path': str(sources['B1']), 'sha256': expected['B1'], 'bytes': sources['B1'].stat().st_size},
        'sourceByteCopiesExact': all((HERE / 'sources' / (k + '-native.png')).read_bytes() == p.read_bytes() for k, p in sources.items()),
        'coreBoundaryX': CORE_X, 'coreChoice': '1504 retained after 1:1 inspection: east curved shop/tower/foreground buildings lie wholly to its left; B left32 crop contains no building.',
        'imageOffsets': {'A2': [0, 0], 'B1': [1472, 0]}, 'nativeWarpMirrorRecolor': False,
        'runtimeUniquePNG': len(graph['images']), 'runtimePNGBytes': sum((HERE / 'navigation' / s['file']).stat().st_size for s in graph['images']),
        'newTiledSHA256': sha(target), 'newGraphSHA256': sha(HERE / 'navigation/graph.json'),
        'nodes': len(graph['nodes']), 'edges': len(graph['edges']), 'components': len(graph['connectedComponents']),
        'duplicateEdges': graph['duplicateEdges'], 'unmergedCrossings': graph['unmergedCrossings'],
        'roadCorrections': len(corrections), 'protectedInputsUnchanged': before == after,
        'ImagesRequests': 0, 'newServiceStarted': False, 'actualNewNavigationVerified': False,
        'TiledCliRenderVerified': False, 'TiledGUIVerified': False,
        'gameTestsOrSaveOperations': False, 'wholeCityAccepted': False})
    print(json.dumps({'map': str(target), 'nativeSources': expected, 'runtimePNG': len(graph['images']),
                      'runtimePNGBytes': sum((HERE / 'navigation' / s['file']).stat().st_size for s in graph['images']),
                      'nodes': len(graph['nodes']), 'edges': len(graph['edges']), 'components': len(graph['connectedComponents']),
                      'protectedUnchanged': True, 'ImagesRequests': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
