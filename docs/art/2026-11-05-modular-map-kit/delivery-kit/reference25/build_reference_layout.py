#!/usr/bin/env python3
"""One-time visual-only reference layout; never rewrites v1 or user input."""
import copy
import hashlib
import json
import math
import shutil
import zipfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
V1 = HERE.parent / 'v1'
KIT = HERE.parent.parent


def read(path):
    return json.loads(path.read_text())


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def properties(obj):
    return {p['name']: p['value'] for p in obj.get('properties', [])}


def main():
    target = HERE / 'reference-layout.tmj'
    if target.exists():
        raise SystemExit('Reference layout already exists; preserve possible user edits.')
    base = read(V1 / 'metadata/base-scene.json')
    catalog = read(V1 / 'metadata/catalog.json')
    original_assets = {a['id']: copy.deepcopy(a) for a in catalog['assets']}
    protected = [V1 / 'user-layout.tmj', HERE.parent / 'map-assets-prototype-v1.zip',
                 KIT / 'revision-006/integration/neighborhood.tmj',
                 KIT / 'revision-006/viewer/assets/scene-layout.json']
    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    # Start from the originally delivered archive, never overwrite or rebase a live user file.
    with zipfile.ZipFile(protected[1]) as archive:
        doc = json.loads(archive.read('v1/user-layout.tmj'))
    projection = base['projection']

    def project(point):
        dx, dy = [point[k] - projection['originMap'][k] for k in (0, 1)]
        return [896 + 16 * (dx * projection['axisX'][k] + dy * projection['axisY'][k])
                for k in (0, 1)]

    def unproject(point):
        x, y = [(point[k] - 896) / 16 for k in (0, 1)]
        a, b = projection['axisX']
        c, d = projection['axisY']
        det = a * d - b * c
        return [projection['originMap'][0] + (d * x - c * y) / det,
                projection['originMap'][1] + (-b * x + a * y) / det]

    def objects(layers, offset=(0, 0)):
        for layer in layers:
            if not layer.get('visible', True):
                continue
            off = [offset[k] + layer.get(('offsetx', 'offsety')[k], 0) for k in (0, 1)]
            if layer['type'] == 'group':
                yield from objects(layer.get('layers', []), off)
            else:
                for obj in layer.get('objects', []):
                    obj = copy.deepcopy(obj)
                    obj['x'] = obj.get('x', 0) + off[0]
                    obj['y'] = obj.get('y', 0) + off[1]
                    yield obj

    all_objects = list(objects(doc['layers']))
    sprites = [o for o in all_objects if 'gid' in o]
    grounds = [o for o in all_objects if 'polygon' in o]
    next_id = max(doc['nextobjectid'], max(o['id'] for o in all_objects) + 1)
    asset_rows = {a['id']: a for a in catalog['assets']}
    for asset in asset_rows.values():
        asset['packageFile'] = '../v1/' + asset['packageFile']
    for tile in doc['tilesets'][0]['tiles']:
        tile['image'] = '../v1/' + tile['image']

    # Two completed native props, with provisional (not measured) game-size defaults.
    footprint = original_assets['B01']['calibration']['candidateFootprintPolygonMapAt005Placement']
    delta = [footprint[1][k] - footprint[0][k] for k in (0, 1)]
    length = math.hypot(*delta)
    uaxis = [v / length for v in delta]
    naxis = [-uaxis[1], uaxis[0]]
    pu = [sum(uaxis[k] * projection[('axisX', 'axisY')[k]][j] for k in (0, 1)) for j in (0, 1)]
    pn = [sum(naxis[k] * projection[('axisX', 'axisY')[k]][j] for k in (0, 1)) for j in (0, 1)]
    for aid, name in [('P11', '长花箱'), ('P12', '空候车棚')]:
        source = KIT / f'revision-009/art-expansion/asset-pack-supplement/native/{aid}-001'
        provenance = read(source / 'provenance.json')
        runtime = read(source / f'{aid}-runtime-280.runtime.json')
        png = source / runtime['file']
        assert hashlib.sha256(png.read_bytes()).hexdigest() == runtime['sha256']
        dest = HERE / 'assets/补充' / png.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(png, dest)
        dims = provenance['defaultDimensionsCandidate']
        width = (abs(pu[0]) * dims[0] + abs(pn[0]) * dims[1]) * 1.08
        height = width * runtime['runtimeSize'][1] / runtime['runtimeSize'][0]
        row = {'id': aid, 'nameZh': name, 'kind': original_assets['P03']['kind'],
               'categoryZh': '小物', 'file': png.name, 'packageFile': str(dest.relative_to(HERE)),
               'nativeSize': runtime['runtimeSize'], 'sha256': runtime['sha256'],
               'worldSizeUnits': [width, height],
               'anchorUV': provenance['defaultAnchorUVRuntimeApprox'],
               'nativePixelsPerUnit': (runtime['cropBox'][2] - runtime['cropBox'][0]) / width,
               'deliveryStatus': '可手调｜未精校；玻璃/软边/隐藏脚点风险见来源记录',
               'calibrationStatus': 'provisional game-size default, not a measured footprint',
               'sourceNativeSHA256': runtime['sourceSHA256']}
        asset_rows[aid] = row
        tile_id = len(doc['tilesets'][0]['tiles'])
        doc['tilesets'][0]['tiles'].append({'id': tile_id, 'image': row['packageFile'],
            'imagewidth': row['nativeSize'][0], 'imageheight': row['nativeSize'][1],
            'properties': [{'name': 'assetId', 'type': 'string', 'value': aid}]})
    doc['tilesets'][0]['tilecount'] = len(doc['tilesets'][0]['tiles'])
    gids = {properties(t)['assetId']: t['id'] + 1 for t in doc['tilesets'][0]['tiles']}
    by_pid = {properties(o).get('persistentId'): o for o in sprites}
    changes = []

    def place(obj, aid, anchor, scale):
        row = asset_rows[aid]
        w, h = [16 * v * scale for v in row['worldSizeUnits']]
        q = project(anchor)
        u, v = row['anchorUV']
        obj.update({'gid': gids[aid], 'x': q[0] - u * w, 'y': q[1] + (1 - v) * h,
                    'width': w, 'height': h, 'rotation': 0, 'visible': True})

    def move(pid, anchor, scale):
        obj = by_pid[pid]
        aid = properties(obj)['assetId']
        old = {'x': obj['x'], 'y': obj['y'], 'width': obj['width'], 'height': obj['height']}
        place(obj, aid, anchor, scale)
        changes.append({'id': pid, 'asset': aid, 'beforeTiled': old,
                        'newAnchorMap': anchor, 'newCanonicalScale': scale})

    def add(aid, name, anchor, scale=1.0):
        nonlocal next_id
        obj = {'id': next_id, 'name': name, 'type': 'sprite', 'properties': [
            {'name': 'assetId', 'type': 'string', 'value': aid},
            {'name': 'userVisualId', 'type': 'string', 'value': name},
            {'name': 'visualOnly', 'type': 'bool', 'value': True}]}
        next_id += 1
        place(obj, aid, anchor, scale)
        sprites.append(obj)
        return name

    # TR-33: dominant market mass, smaller frontage houses and a varied rear row.
    move('009r4-src-0587', [-1452.5, 220.0], 1.2)
    move('009compound-source0125-court-module-01-B05', [-1446.0, 203.0], .95)
    move('009compound-source0125-court-module-02-B01', [-1445.5, 191.0], 1.05)
    for pid, anchor in [('market-life-entry-sign', [-1443.3, 215.0]),
                        ('market-life-waste-bins', [-1441.9, 210.5]),
                        ('market-life-low-shrub', [-1467.0, 230.0]),
                        ('market-life-shade-tree', [-1467.0, 237.0]),
                        ('market-life-waiting-bench', [-1464.0, 232.0])]:
        obj = by_pid[pid]
        aid = properties(obj)['assetId']
        scale = obj['width'] / (16 * asset_rows[aid]['worldSizeUnits'][0])
        move(pid, anchor, scale)
    focus = ['009r4-src-0587', '009compound-source0125-court-module-01-B05',
             '009compound-source0125-court-module-02-B01']
    focus += [add('B06', 'ref25-rear-residential', [-1462.0, 187.5], 1.1),
              add('B03', 'ref25-height-accent', [-1463.0, 168.8], 1.05),
              add('B04', 'ref25-secondary-public', [-1480.0, 208.0], 1.05),
              add('P11', 'ref25-frontage-planter', [-1441.5, 195.0]),
              add('P12', 'ref25-roadside-shelter', [-1441.0, 230.0])]
    for i, (aid, anchor, scale) in enumerate([
            ('T01', [-1441.0, 182.0], .9), ('T02', [-1491.0, 217.0], 1),
            ('T02', [-1473.0, 175.0], .9), ('T05', [-1473.0, 225.0], .9)]):
        add(aid, f'ref25-green-{i + 1}', anchor, scale)

    # Replace only the reference copy's local patches, not any original ground data.
    kept = []
    for obj in grounds:
        points = [unproject([obj['x'] + p['x'], obj['y'] + p['y']]) for p in obj['polygon']]
        center = [sum(p[k] for p in points) / len(points) for k in (0, 1)]
        if not (-1498 < center[0] < -1438 and 160 < center[1] < 242):
            kept.append(obj)
    hard = next(s['materialId'] for s in base['groundSurfaces']
                if s['id'] == '009r4-src-0587-source-court-587')
    patches = [
        ('market-forecourt', hard, [[-1463, 210], [-1440, 210], [-1440, 235], [-1463, 235]]),
        ('residential-front', hard, [[-1453, 180], [-1440, 180], [-1440, 208], [-1453, 208]]),
        ('rear-residential', hard, [[-1472, 177], [-1453, 177], [-1453, 198], [-1472, 198]]),
        ('secondary-public', hard, [[-1489, 198], [-1469, 198], [-1469, 222], [-1489, 222]]),
        ('shared-link', hard, [[-1470, 209], [-1463, 209], [-1463, 219], [-1470, 219]]),
        ('residential-link', hard, [[-1455, 184], [-1449, 184], [-1449, 188], [-1455, 188]]),
        ('rear-green', 'G03-meadow', [[-1493, 192], [-1489, 192], [-1489, 229], [-1493, 227]]),
        ('market-green', 'G03-meadow', [[-1469, 225], [-1463, 225], [-1463, 239], [-1470, 237]])]
    for name, mat, points in patches:
        q = [project(p) for p in points]
        kept.append({'id': next_id, 'name': 'ref25-ground-' + name, 'x': q[0][0], 'y': q[0][1],
                     'polygon': [{'x': p[0] - q[0][0], 'y': p[1] - q[0][1]} for p in q],
                     'properties': [{'name': 'surfaceAssetId', 'type': 'string', 'value': mat}]})
        next_id += 1

    def foot_y(obj):
        row = asset_rows[properties(obj)['assetId']]
        return obj['y'] - (1 - row['anchorUV'][1]) * obj['height']

    sprites.sort(key=foot_y)
    doc['layers'] = [{'id': 1, 'name': 'Visual reference grounds — not navigation',
                      'type': 'objectgroup', 'draworder': 'index', 'objects': kept},
                     {'id': 2, 'name': 'Reference25 editable depth order',
                      'type': 'objectgroup', 'draworder': 'index', 'objects': sprites}]
    doc['nextlayerid'] = 3
    doc['nextobjectid'] = next_id
    write(target, doc)
    (HERE / 'metadata').mkdir(exist_ok=True)
    for name in ['base-scene.json', 'base-object-identity.json']:
        shutil.copyfile(V1 / 'metadata' / name, HERE / 'metadata' / name)
    catalog.update({'assets': list(asset_rows.values()), 'uniquePNG': len(asset_rows),
                    'categories': dict(Counter(a['categoryZh'] for a in asset_rows.values())),
                    'PNGBytes': sum(a['bytes'] if 'bytes' in a else (HERE / a['packageFile']).stat().st_size
                                    for a in asset_rows.values()),
                    'layoutQuality': 'TR-33-inspired visual-only rough block, not registered/final accepted'})
    write(HERE / 'metadata/catalog.json', catalog)
    shutil.copytree(V1 / 'preview', HERE / 'preview',
                    ignore=shutil.ignore_patterns('*.png'))
    # The immutable shell manifest is only an input to the existing exporter.
    library = copy.deepcopy(doc['tilesets'][0])
    library.pop('firstgid', None)
    for tile in library['tiles']:
        tile['image'] = '../' + tile['image']
    write(HERE / 'templates/asset-library.tsj', library)
    for aid in ['P11', 'P12']:
        obj = copy.deepcopy(next(o for o in sprites if properties(o)['assetId'] == aid))
        obj['id'] = 1
        obj.pop('x', None)
        obj.pop('y', None)
        obj['properties'] = [{'name': 'assetId', 'type': 'string', 'value': aid},
                             {'name': 'visualOnly', 'type': 'bool', 'value': True}]
        write(HERE / f'templates/{aid}.tx', {'type': 'template', 'tileset': {
            'firstgid': 1, 'source': 'asset-library.tsj'}, 'object': obj})
    refs = HERE / 'references'
    refs.mkdir(exist_ok=True)
    for name in ['approved-25-assembly-reference.jpg', 'source-record.json']:
        shutil.copyfile(KIT / 'revision-009/references/layout25' / name, refs / name)
    after = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    assert before == after
    report = {'status': 'visual-reference-draft-not-registration-or-acceptance',
              'referenceRegion': 'TR-33', 'fullAssembly': 'references/approved-25-assembly-reference.jpg',
              'referencePrinciples': ['dominant large market versus smaller frontage houses',
                                      'varied rear residential/public row instead of isolated objects',
                                      'connected grounds, green edges and roadside small props'],
              'changedExistingVisuals': changes, 'newVisuals': len(sprites) - len(base['blocks']),
              'visibleInstances': len(sprites), 'groundSurfaces': len(kept),
              'newBusinessBindings': 0, 'originalRoadDataChanged': False,
              'focusIDs': focus, 'protectedSHA256': after,
              'scope': 'new reference25 copy only; v1/user and canonical main map untouched',
              'remaining': ['rough spacing/collisions/grounds require user refinement',
                            'reference painting is not measured road registration',
                            'P11/P12 anchors and glass/soft edges provisional']}
    write(HERE / 'layout-changes.json', report)
    print(json.dumps({'map': str(target), 'instances': len(sprites), 'grounds': len(kept),
                      'focusIDs': ','.join(focus), 'protectedUnchanged': before == after}, ensure_ascii=False))


if __name__ == '__main__':
    main()
