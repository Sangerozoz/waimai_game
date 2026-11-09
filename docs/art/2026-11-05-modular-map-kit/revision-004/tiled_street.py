#!/usr/bin/env python3
"""Independent Tiled street candidate -> existing isolated Cocos shell.
Only writes in this revision. Never overwrites original or user-edited maps.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
OLD = BASE / 'revision-003'
INTEGRATION = HERE / 'integration'
MAP = INTEGRATION / 'street.tmj'
META = BASE / 'revision-001/integration/bridge-meta.json'


def read(p):
    return json.loads(p.read_text())


def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def props(obj):
    return {p['name']: p['value'] for p in obj.get('properties', [])}


def properties(values):
    return [{'name': k, 'type': 'bool' if isinstance(v, bool) else 'float' if isinstance(v, (int, float)) else 'string', 'value': v} for k, v in values.items()]


def project(point, meta):
    p = meta['projection']
    dx, dy = [point[i]-p['originMap'][i] for i in (0, 1)]
    return [meta['editorOrigin'][i]+meta['pixelsPerUnit']*(dx*p['axisX'][i]+dy*p['axisY'][i]) for i in (0, 1)]


def unproject(point, meta):
    p = meta['projection']
    x, y = [(point[i]-meta['editorOrigin'][i])/meta['pixelsPerUnit'] for i in (0, 1)]
    a, b = p['axisX']; c, d = p['axisY']; det = a*d-b*c
    return [p['originMap'][0]+(d*x-c*y)/det, p['originMap'][1]+(-b*x+a*y)/det]


def protected():
    paths = [BASE/'revision-001/integration/revision.tmj',
             BASE/'revision-002/viewer/assets/scene-layout.json',
             OLD/'viewer/assets/scene-layout.json', OLD/'B01-road-aligned-native-v1.png',
             BASE/'pilot/T01-v1.png', BASE/'pilot/L01-v1.png', BASE/'pilot/L02-v1.png',
             BASE.parent/'../research/2026-11-05-map-production/tiled-probe/probe.tmj']
    return {str(p.resolve()): sha(p) for p in paths}


def initialize():
    if MAP.exists() or (HERE/'viewer').exists():
        raise ValueError('Refusing to reset an existing candidate map/viewer; use export')
    INTEGRATION.mkdir(parents=True, exist_ok=True)
    before = protected()
    meta = read(META)
    manifest = read(OLD/'viewer/assets/asset-manifest.json')
    ids = ['B01-road-tangent-candidate', 'T01', 'L01', 'L02', 'HC-R-NE', 'HC-R-SW', 'S01-paving', 'S02-asphalt']
    assets = [copy.deepcopy(next(a for a in manifest['assets'] if a['id'] == aid)) for aid in ids]
    for a in assets:
        src = OLD/'viewer/assets'/a['file']
        if sha(src) != a['sha256']:
            raise ValueError('Native source SHA mismatch: '+a['id'])
        dst = INTEGRATION/'assets'/a['file']; dst.parent.mkdir(exist_ok=True)
        shutil.copyfile(src, dst)
    manifest['assets'] = assets
    manifest['status'] = 'tiled-one-street-native-candidate-not-accepted'
    write(INTEGRATION/'asset-manifest.json', manifest)
    write(INTEGRATION/'bridge-meta.json', meta)
    shutil.copyfile(BASE/'revision-001/integration/original-roads.png', INTEGRATION/'original-roads.png')
    constraint = read(OLD/'road-constraint.json')
    mid = constraint['roadReferenceMap']; u = constraint['streetTangentMap']
    n = [-u[1], u[0]]

    def point(tangent, normal):
        return [mid[i]+tangent*u[i]+normal*n[i] for i in (0, 1)]

    specs = [
        ('building-B01', ids[0], constraint['candidateAnchorMap']),
        ('tree-west', 'T01', point(-8.3, -7)),
        ('tree-east', 'T01', point(8.5, -7)),
        ('tree-far-east', 'T01', point(14.5, -7)),
        ('lamp-single-west', 'L01', point(-4.6, -5.2)),
        ('lamp-single-east', 'L01', point(5.0, -5.2)),
        ('lamp-double-opposite', 'L02', point(1.5, 5.2)),
    ]
    by_id = {a['id']: a for a in assets}
    tiles = []
    for i, aid in enumerate(ids[:4]):
        a = by_id[aid]
        tiles.append({'id': i, 'image': 'assets/'+a['file'], 'imagewidth': a['nativeSize'][0], 'imageheight': a['nativeSize'][1],
                      'properties': properties({'assetId': aid, 'anchorU': a['anchorUV'][0], 'anchorV': a['anchorUV'][1], 'nativePixelsPerUnit': a['nativePixelsPerUnit']})})
    objects = []
    for oid, (pid, aid, anchor) in enumerate(specs, 1):
        a = by_id[aid]; x, y = project(anchor, meta)
        w, h = [v/a['nativePixelsPerUnit']*meta['pixelsPerUnit'] for v in a['nativeSize']]
        au, av = a['anchorUV']
        objects.append({'id': oid, 'name': pid, 'type': 'sprite', 'gid': ids.index(aid)+1,
                        'x': x-au*w, 'y': y+(1-av)*h, 'width': w, 'height': h, 'rotation': 0, 'visible': True,
                        'properties': properties({'persistentId': pid, 'assetId': aid, 'manualLocked': False})})
    # The initial stack follows ground contact depth. Tiled index edits are authoritative afterwards.
    anchors = {pid: anchor for pid, aid, anchor in specs}
    objects.sort(key=lambda o: project(anchors[o['name']], meta)[1])
    parcel_map = [point(t, q) for t, q in [(-6.2, -13), (6.2, -13), (6.2, -5.8), (-6.2, -5.8)]]
    parcel_px = [project(v, meta) for v in parcel_map]
    px, py = parcel_px[0]
    surface = {'id': 8, 'name': 'B01-paved-forecourt', 'type': 'ground-surface', 'x': px, 'y': py,
               'width': 0, 'height': 0, 'rotation': 0, 'visible': True,
               'polygon': [{'x': v[0]-px, 'y': v[1]-py} for v in parcel_px],
               'properties': properties({'surfaceAssetId': 'S01-paving'})}
    doc = {'type': 'map', 'version': '1.10', 'tiledversion': '1.11.2', 'orientation': 'orthogonal', 'renderorder': 'right-down',
           'infinite': False, 'width': 56, 'height': 56, 'tilewidth': 32, 'tileheight': 32, 'backgroundcolor': '#dedbd0',
           'nextobjectid': 9, 'nextlayerid': 4,
           'properties': properties({'projectionId': meta['projection']['id'], 'pixelsPerUnit': meta['pixelsPerUnit'],
                                     'status': 'editable-street-candidate-not-user-accepted'}),
           'tilesets': [{'firstgid': 1, 'name': 'Road-corrected building and approved fixtures', 'tilewidth': max(t['imagewidth'] for t in tiles),
                         'tileheight': max(t['imageheight'] for t in tiles), 'tilecount': 4, 'columns': 0, 'objectalignment': 'bottomleft', 'tiles': tiles}],
           'layers': [
               {'id': 1, 'name': 'Original roads — locked reference', 'type': 'imagelayer', 'image': 'original-roads.png', 'x': 0, 'y': 0, 'opacity': 1, 'visible': True, 'locked': True},
               {'id': 2, 'name': 'Editable paving polygon', 'type': 'objectgroup', 'draworder': 'index', 'opacity': 1, 'visible': True, 'color': '#e0d7c8', 'objects': [surface]},
               {'id': 3, 'name': 'Editable objects — manual index order exported', 'type': 'objectgroup', 'draworder': 'index', 'opacity': 1, 'visible': True, 'objects': objects},
           ]}
    write(MAP, doc)
    write(INTEGRATION/'initial-snapshot.json', doc)
    write(INTEGRATION/'protected-before.json', before)
    if before != protected():
        raise ValueError('Protected sources changed')
    export(MAP)


def layers(layers_in, shown=True, offset=(0, 0)):
    for layer in layers_in:
        visible = shown and layer.get('visible', True)
        shift = (offset[0]+layer.get('offsetx', 0), offset[1]+layer.get('offsety', 0))
        if visible and layer.get('opacity', 1) != 1:
            raise ValueError('Partial layer opacity is unsupported; refusing silent mismatch')
        if layer['type'] == 'group':
            yield from layers(layer.get('layers', []), visible, shift)
        elif layer['type'] == 'objectgroup' and visible:
            yield layer, shift


def export(path):
    path = path.resolve()
    if not path.is_relative_to(INTEGRATION):
        raise ValueError('Import only maps in this independent candidate directory')
    before = protected(); meta = read(INTEGRATION/'bridge-meta.json')
    doc = read(path); manifest = read(INTEGRATION/'asset-manifest.json')
    source_layout = read(OLD/'viewer/assets/scene-layout.json')
    layout = copy.deepcopy(source_layout)
    originals = {a['id']: a for a in manifest['assets']}
    gids = {ts['firstgid']+t['id']: props(t)['assetId'] for ts in doc['tilesets'] for t in ts['tiles']}
    layout['blocks'] = []; layout['groundSurfaces'] = []; report = []; seen = set()
    for layer, shift in layers(doc['layers']):
        objects = [o for o in layer['objects'] if o.get('visible', True)]
        order = layer.get('draworder', 'topdown')
        if order == 'topdown':
            objects = sorted(objects, key=lambda o: o['y'])
        elif order != 'index':
            raise ValueError('Unsupported object draw order')
        for obj in objects:
            if obj.get('rotation', 0):
                raise ValueError('Plane rotation is unsupported; use native orientation assets')
            if obj.get('opacity', 1) != 1:
                raise ValueError('Partial object opacity unsupported')
            if 'polygon' in obj:
                surface_id = props(obj).get('surfaceAssetId')
                if surface_id not in ('S01-paving', 'S02-asphalt'):
                    raise ValueError('Unknown surface material')
                polygon = [unproject([obj['x']+shift[0]+v['x'], obj['y']+shift[1]+v['y']], meta) for v in obj['polygon']]
                layout['groundSurfaces'].append({'id': obj['name'], 'materialId': surface_id, 'polygonMap': polygon})
                continue
            if obj['gid'] & 0xf0000000:
                raise ValueError('Mirrored/rotated tile flags unsupported')
            a = originals[gids[obj['gid']]]; p = props(obj)
            if p.get('assetId', a['id']) != a['id']:
                raise ValueError('Object metadata disagrees with tile asset')
            sx, sy = [obj[k]/(a['nativeSize'][i]/a['nativePixelsPerUnit']*meta['pixelsPerUnit']) for i, k in enumerate(('width', 'height'))]
            if not sx > 0 or not math.isclose(sx, sy, rel_tol=1e-5):
                raise ValueError('Only positive uniform sprite scaling supported')
            au, av = a['anchorUV']
            px = [obj['x']+shift[0]+au*obj['width'], obj['y']+shift[1]-(1-av)*obj['height']]
            anchor = unproject(px, meta)
            pid = p.get('persistentId', obj['name'])
            if not pid or pid in seen:
                raise ValueError('Each object needs a unique persistentId')
            seen.add(pid); aid = 'instance-'+pid; index = len(layout['blocks'])
            clone = copy.deepcopy(a)
            clone.update({'id': aid, 'nativePixelsPerUnit': a['nativePixelsPerUnit']/sx, 'anchorMap': anchor, 'sortMap': anchor})
            manifest['assets'].append(clone)
            layout['blocks'].append({'assetId': aid, 'anchorMap': anchor, 'sortMap': anchor, 'persistentId': pid,
                                     'sourceAssetId': a['id'], 'editorRenderOrder': index})
            report.append({'persistentId': pid, 'assetId': aid, 'tiledObjectId': obj['id'], 'layerId': layer['id'], 'draworder': order,
                           'editorRenderOrder': index, 'anchorMap': anchor, 'uniformScale': sx, 'anchorRoundtripPx': math.dist(project(anchor, meta), px)})
    if not layout['blocks']:
        raise ValueError('No visible candidate sprites')
    layout['camera'] = {'focusMap': originals['B01-road-tangent-candidate']['anchorMap'], 'viewWidthUnits': 15, 'screenOffset': [0, 0], 'referenceWidth': 720, 'referenceHeight': 1280}
    layout['status'] = 'editable-tiled-street-export-candidate-not-accepted'
    layout['notes'] = [note for note in layout['notes'] if not note.startswith('One-building display staging only;')]
    layout['notes'].append('Exported from the independent street.tmj candidate; original user maps never overwritten.')
    layout['staticOrdering'] = 'Tiled layer order + index/topdown object order; dynamic rider inserted by ground depth without reordering statics'
    layout['tiledSourceSHA256'] = sha(path)
    # Copy an immutable previous shell once. Later exports update only derived asset data.
    viewer = HERE/'viewer'
    if not viewer.exists():
        shutil.copytree(OLD/'viewer', viewer)
        patch_shell(viewer)
    centered_zoom(viewer)
    for a in manifest['assets']:
        source = INTEGRATION/'assets'/a['file']
        if sha(source) != a['sha256']:
            raise ValueError('Native asset copy changed')
        shutil.copyfile(source, viewer/'assets'/a['file'])
    write(viewer/'assets/asset-manifest.json', manifest)
    write(viewer/'assets/scene-layout.json', layout)
    if before != protected():
        raise ValueError('Protected sources changed during export')
    if layout['roads'] != source_layout['roads'] or layout['projection'] != source_layout['projection']:
        raise ValueError('Source roads/projection changed')
    write(INTEGRATION/'export-report.json', {'status': 'data-export-integrity-not-art-or-game-acceptance', 'tiledMap': str(path), 'tiledSHA256': sha(path),
          'spriteCount': len(report), 'surfaceCount': len(layout['groundSurfaces']), 'objects': report,
          'sourceRoadsAndProjectionUnchanged': True, 'nativePNGBytesPreserved': True, 'protectedSHA256': before,
          'maxAnchorRoundtripPx': max(r['anchorRoundtripPx'] for r in report), 'gameTestsRun': False, 'engineRebuilt': False,
          'dynamicOrderingLimit': 'Manual static order is exact. Rider depth insertion remains a simple ground-depth policy, not full per-pixel occlusion.'})
    print('Exported', len(report), 'editable native sprites and', len(layout['groundSurfaces']), 'paving polygon; old maps untouched')


def centered_zoom(viewer):
    # Generated shell only: keep the viewed map point fixed when zooming.
    bundle = viewer/'assets/main/index.probe41.js'
    code = bundle.read_text()
    old = 's=function(e){t.zoom=Math.max(.35*t.initialZoom,Math.min(8*t.initialZoom,t.zoom*e)),t.world.setScale(t.zoom,t.zoom,1)}'
    new = 's=function(e){var z=t.zoom;t.zoom=Math.max(.35*t.initialZoom,Math.min(8*t.initialZoom,t.zoom*e));var q=t.zoom/z,p=t.world.position;t.world.setScale(t.zoom,t.zoom,1);t.world.setPosition(p.x*q,p.y*q,0)}'
    if code.count(old) == 1:
        bundle.write_text(code.replace(old, new))
    elif code.count(new) != 1:
        raise ValueError('Unexpected zoom implementation; refusing a blind patch')


def patch_shell(viewer):
    bundle = viewer/'assets/main/index.probe41.js'
    code = bundle.read_text()
    old = 'this.items.push({node:P,depth:I,bias:0})'
    new = 'this.items.push({node:P,depth:I,bias:0,editorOrder:z.editorRenderOrder,persistentId:z.persistentId})'
    if code.count(old) != 1:
        raise ValueError('Unexpected static-item implementation')
    code = code.replace(old, new)
    old = 'o.sort=function(){this.items.sort((function(t,e){return t.depth-e.depth||t.bias-e.bias})),this.items.forEach((function(t,e){return t.node.setSiblingIndex(e+1)}))}'
    new = 'o.sort=function(){var s=this.items.filter(function(i){return Number.isFinite(i.editorOrder)}).sort(function(a,b){return a.editorOrder-b.editorOrder}),d=this.items.filter(function(i){return !Number.isFinite(i.editorOrder)}).sort(function(a,b){return a.depth-b.depth||a.bias-b.bias});d.forEach(function(i){var k=s.findIndex(function(j){return j.depth>i.depth||(j.depth===i.depth&&j.bias>i.bias)});s.splice(k<0?s.length:k,0,i)});s.forEach(function(i,k){i.node.setSiblingIndex(k+1)});globalThis.__mapPreviewOrder=s.map(function(i){return {name:i.node.name,persistentId:i.persistentId||null,editorOrder:Number.isFinite(i.editorOrder)?i.editorOrder:null,siblingIndex:i.node.getSiblingIndex(),depth:i.depth,x:i.node.position.x,y:i.node.position.y}})}'
    if code.count(old) != 1:
        raise ValueError('Unexpected sorting implementation')
    code = code.replace(old, new)
    # Add the editable ground patch BEFORE the unchanged original road strokes.
    old = 'u.lineCap="round",u.lineJoin="round";'
    new = 'for(var gs of this.layout.groundSurfaces||[]){u.beginPath();gs.polygonMap.forEach(function(q,k){k?u.lineTo(q[0],q[1]):u.moveTo(q[0],q[1])});u.closePath();u.fillStyle=gs.materialId==="S02-asphalt"?g:w;u.fill()}u.lineCap="round",u.lineJoin="round";'
    if code.count(old) != 1:
        raise ValueError('Unexpected ground implementation')
    code = code.replace(old, new)
    # This revision has no old-art toggle; old comparison remains intact in revision-003.
    old = 'fetch(e.endsWith("asset-manifest.json")&&new URLSearchParams(location.search).get("variant")==="before"?e.replace("asset-manifest.json","asset-manifest-before.json"):e,{cache:"no-store"})'
    if code.count(old) != 1:
        raise ValueError('Unexpected comparison loader')
    code = code.replace(old, 'fetch(e,{cache:"no-store"})')
    bundle.write_text(code)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['init', 'export'])
    parser.add_argument('--map', type=Path, default=MAP)
    args = parser.parse_args()
    initialize() if args.command == 'init' else export(args.map)
