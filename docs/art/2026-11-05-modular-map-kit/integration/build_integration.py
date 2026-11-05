#!/usr/bin/env python3
"""Build isolated seven-native-sprite Tiled pilot, or import its edited objects.

Only writes below this integration directory. No Cocos/game/source-map writes.
PNG data is copied byte for byte. Calibration is saved manual metadata.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import shutil
import struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PILOT = HERE.parent / 'pilot'
PROBE = ROOT / 'docs/research/2026-11-05-map-production/tiled-probe'
BASE = PROBE / 'edited-viewer/assets'


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def properties(values):
    return [{'name': k, 'type': 'bool' if isinstance(v, bool) else 'float' if isinstance(v, (int, float)) else 'string', 'value': v} for k, v in values.items()]


def props(obj):
    return {p['name']: p['value'] for p in obj.get('properties', [])}


def project(point, meta):
    p = meta['projection']
    dx, dy = [point[i] - p['originMap'][i] for i in (0, 1)]
    return [meta['editorOrigin'][i] + meta['pixelsPerUnit'] * (dx*p['axisX'][i] + dy*p['axisY'][i]) for i in (0, 1)]


def unproject(point, meta):
    p = meta['projection']
    x, y = [(point[i] - meta['editorOrigin'][i])/meta['pixelsPerUnit'] for i in (0, 1)]
    a, b = p['axisX']; c, d = p['axisY']; det = a*d-b*c
    return [p['originMap'][0] + (d*x-c*y)/det, p['originMap'][1] + (-b*x+a*y)/det]


def png_info(path):
    data = path.read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Expected PNG: ' + str(path))
    w, h, depth, colour = struct.unpack('>IIBB', data[16:26])
    return [w, h], {'bitDepth': depth, 'colourType': colour, 'hasNativeAlpha': colour in (4, 6)}


def calibration_asset(spec, meta):
    source = PILOT / spec['file']
    size, png = png_info(source)
    if not png['hasNativeAlpha']:
        raise ValueError('Pilot requires native alpha: ' + spec['file'])
    a = copy.deepcopy(spec)
    if 'groundCornersPixels' in spec:
        c = spec['groundCornersPixels']
        center = [(c['left'][i]+c['right'][i])/2 for i in (0, 1)]
        lengths = [math.dist(c['left'], c['front']), math.dist(c['front'], c['right'])]
        # Both ground axes have equal projected length at azimuth45.
        unit = math.hypot(*meta['projection']['axisX'])
        expected = [spec['footprintMeters'][i]*unit for i in (0, 1)]
        ppu = sum(x*y for x, y in zip(expected, lengths))/sum(x*x for x in expected)
        a['calibration'] = {'method': 'manual-visible-base-corners-uniform-least-squares', 'anchorPixel': center,
                            'measuredEdgeLengthsPx': lengths, 'expectedEdgeLengthsProjectionUnits': expected,
                            'independentEdgePixelsPerUnit': [lengths[i]/expected[i] for i in (0, 1)],
                            'edgeLengthResidualPixels': [lengths[i]-ppu*expected[i] for i in (0, 1)],
                            'measuredAbsEdgeSlopes': [abs((c['front'][1]-c['left'][1])/(c['front'][0]-c['left'][0])), abs((c['right'][1]-c['front'][1])/(c['right'][0]-c['front'][0]))],
                            'targetAbsEdgeSlope': abs(meta['projection']['axisX'][1]/meta['projection']['axisX'][0])}
        a['groundPolygon'] = [[v[0]/size[0], v[1]/size[1]] for v in [c['left'], [c['left'][0]+c['right'][0]-c['front'][0], c['left'][1]+c['right'][1]-c['front'][1]], c['right'], c['front']]]
    else:
        center = spec['anchorPixel']
        ppu = spec['nativePixelsPerUnit']
        a['calibration'] = {'method': spec['scaleMethod'], 'anchorPixel': center}
    a.update({'kind': 'block', 'nativeSize': size, 'png': png, 'sha256': sha(source),
              'anchorUV': [center[i]/size[i] for i in (0, 1)], 'nativePixelsPerUnit': ppu,
              'sortMap': spec['anchorMap'], 'projectionId': meta['projection']['id'],
              'status': 'manual-calibration-native-candidate-not-user-accepted',
              'source': str(source.relative_to(ROOT))})
    target = HERE / 'assets' / a['file']; target.parent.mkdir(exist_ok=True)
    shutil.copyfile(source, target)
    if sha(target) != a['sha256']:
        raise ValueError('Native source copy mismatch')
    return a


def make_object(oid, pid, asset, point, gid, meta):
    w, h = [n/asset['nativePixelsPerUnit']*meta['pixelsPerUnit'] for n in asset['nativeSize']]
    u, v = asset['anchorUV']; x, y = project(point, meta)
    return {'id': oid, 'name': pid, 'type': 'sprite', 'gid': gid, 'x': x-u*w, 'y': y+(1-v)*h,
            'width': w, 'height': h, 'rotation': 0, 'visible': True,
            'properties': properties({'persistentId': pid, 'assetId': asset['id'], 'orientationVariant': asset.get('orientationVariant', 'native'), 'scale': 1, 'manualLocked': False})}


def prepare():
    target_map = HERE / 'pilot.tmj'
    if target_map.exists():
        raise ValueError('Refusing to reset edited pilot.tmj. Use import to re-export saved map.')
    meta = read(PROBE / 'bridge-meta.json'); write(HERE / 'bridge-meta.json', meta)
    specs = read(HERE / 'calibration.json')['assets']
    if len(specs) != 7:
        raise ValueError('Need exactly four building views, one tree, two lamp native assets')
    assets = [calibration_asset(s, meta) for s in specs]
    # Keep only the actual runtime prerequisites from the existing viewer.
    old = read(BASE / 'asset-manifest.json')
    keep = [copy.deepcopy(a) for a in old['assets'] if a['id'] in ('HC-R-NE', 'HC-R-SW', 'S01-paving', 'S02-asphalt')]
    for a in keep:
        shutil.copyfile(BASE / a['file'], HERE / 'assets' / a['file'])
        if sha(HERE / 'assets' / a['file']) != a['sha256']:
            raise ValueError('Existing rider/material mismatch')
    manifest = {'schemaVersion': 1, 'packageComplete': True, 'status': 'isolated-seven-native-sprite-pilot-not-accepted',
                'projection': meta['projection'], 'assets': assets+keep,
                'notes': ['Native PNG bytes and alpha preserved. Anchors/physical dimensions are manual candidates.',
                          'Uniform positive scaling only; no plane rotations, mirroring, raster combinations or trimming.',
                          'Camera deviations and edge fringes remain for review. No game stage tests performed.']}
    write(HERE / 'assets/asset-manifest.json', manifest)
    write(HERE / 'source-integrity.json', {
        'status': 'bytewise-copy-record-not-art-acceptance',
        'roadReference': {'source': str((PROBE / 'original-roads.png').relative_to(ROOT)), 'sha256': sha(PROBE / 'original-roads.png')},
        'baselineLayoutSHA256': sha(BASE / 'scene-layout.json'),
        'originalProbeMapSHA256': sha(PROBE / 'probe.tmj'),
        'assets': [{'id': a['id'], 'file': a['file'], 'sha256': a['sha256'], 'source': a.get('source', str((BASE / a['file']).relative_to(ROOT)))} for a in assets+keep],
    })
    old_map = read(PROBE / 'probe.tmj')
    road_layer = copy.deepcopy(next(l for l in old_map['layers'] if l['type'] == 'imagelayer'))
    road_layer.update({'id': 1, 'image': 'original-roads.png', 'locked': True})
    shutil.copyfile(PROBE / 'original-roads.png', HERE / 'original-roads.png')
    tiles = [{'id': i, 'image': 'assets/'+a['file'], 'imagewidth': a['nativeSize'][0], 'imageheight': a['nativeSize'][1], 'properties': properties({'assetId': a['id']})} for i, a in enumerate(assets)]
    by_id = {a['id']: (a, i+1) for i, a in enumerate(assets)}
    objects = [make_object(i+1, 'pilot-'+a['id'], a, a['anchorMap'], i+1, meta) for i, a in enumerate(assets)]
    # Hidden editor templates contain independent normal objects; no new AI bitmap.
    oid = len(objects)+1; layers = []; lid = 4
    for aid, count, spacing in [('T01', 3, 5), ('L01', 3, 6), ('L02', 9, 5)]:
        for axis in (0, 1):
            a, gid = by_id[aid]; row = []
            for i in range(count):
                point = [-1635.0, 42.0]; point[axis] += i*spacing
                row.append(make_object(oid, f'template-{aid}-{count}-axis{axis}-{i+1}', a, point, gid, meta)); oid += 1
            layers.append({'id': lid, 'name': f'{aid} x{count} world-axis-{axis} independent instances', 'type': 'objectgroup', 'draworder': 'topdown', 'visible': True, 'opacity': 1, 'objects': row}); lid += 1
    doc = {'type': 'map', 'version': '1.10', 'tiledversion': '1.11.2', 'orientation': 'orthogonal', 'renderorder': 'right-down',
           'infinite': False, 'width': old_map['width'], 'height': old_map['height'], 'tilewidth': old_map['tilewidth'], 'tileheight': old_map['tileheight'],
           'backgroundcolor': '#dedbd0', 'nextobjectid': oid, 'nextlayerid': lid,
           'properties': properties({'projectionId': meta['projection']['id'], 'pixelsPerUnit': 16, 'note': 'Seven native candidates. Hidden templates are editable repeated instances. Do not rotate/mirror PNG objects.'}),
           'tilesets': [{'firstgid': 1, 'name': 'Seven modular native candidates', 'tilewidth': max(a['nativeSize'][0] for a in assets), 'tileheight': max(a['nativeSize'][1] for a in assets), 'tilecount': len(assets), 'columns': 0, 'objectalignment': 'bottomleft', 'tiles': tiles}],
           'layers': [road_layer, {'id': 2, 'name': 'Editable pilot objects', 'type': 'objectgroup', 'draworder': 'topdown', 'visible': True, 'opacity': 1, 'objects': objects},
                      {'id': 3, 'name': 'Optional 3-tree and 3/9-lamp templates — hidden by default', 'type': 'group', 'visible': False, 'opacity': 1, 'layers': layers}]}
    write(target_map, doc)
    write(HERE / 'initial-map-snapshot.json', doc)
    import_map(target_map)


def object_layers(layers, visible=True, offset=(0, 0)):
    for layer in layers:
        shown = visible and layer.get('visible', True)
        shift = (offset[0]+layer.get('offsetx', 0), offset[1]+layer.get('offsety', 0))
        if layer['type'] == 'group':
            yield from object_layers(layer['layers'], shown, shift)
        elif layer['type'] == 'objectgroup':
            yield layer, shown, shift


def import_map(path):
    path = path.resolve()
    if not path.is_relative_to(HERE):
        raise ValueError('Only integration maps can be imported')
    doc = read(path); meta = read(HERE / 'bridge-meta.json'); manifest = read(HERE / 'assets/asset-manifest.json')
    layout = copy.deepcopy(read(BASE / 'scene-layout.json'))
    previous_bounds = copy.deepcopy(layout['bounds'])
    originals = {a['id']: a for a in manifest['assets']}
    gids = {ts['firstgid']+t['id']: props(t)['assetId'] for ts in doc['tilesets'] for t in ts['tiles']}
    blocks = []; report = []; seen = set(); hidden = 0
    for layer, visible, shift in object_layers(doc['layers']):
        for obj in layer['objects']:
            if not visible or not obj.get('visible', True):
                hidden += 1; continue
            if obj.get('rotation', 0) or obj['gid'] & 0xf0000000:
                raise ValueError('PNG plane rotation/mirroring unsupported')
            aid = gids[obj['gid']]; a = originals[aid]; p = props(obj)
            if p.get('assetId', aid) != aid:
                raise ValueError('Object assetId must agree with its tile')
            pid = p.get('persistentId', obj['name'])
            if pid in seen:
                pid = pid+'-object-'+str(obj['id'])
            seen.add(pid)
            sx, sy = [obj[k]/(a['nativeSize'][i]/a['nativePixelsPerUnit']*meta['pixelsPerUnit']) for i, k in enumerate(('width', 'height'))]
            if sx <= 0 or not math.isclose(sx, sy, rel_tol=1e-5):
                raise ValueError('Only positive uniform scale supported')
            u, v = a['anchorUV']
            pixel = [obj['x']+shift[0]+u*obj['width'], obj['y']+shift[1]-(1-v)*obj['height']]
            point = unproject(pixel, meta)
            clone = copy.deepcopy(a); clone.update({'id': 'instance-'+pid, 'nativePixelsPerUnit': a['nativePixelsPerUnit']/sx, 'anchorMap': point, 'sortMap': point})
            manifest['assets'].append(clone)
            blocks.append({'assetId': clone['id'], 'anchorMap': point, 'sortMap': point, 'persistentId': pid, 'sourceAssetId': aid, 'scale': sx})
            report.append({'persistentId': pid, 'sourceAssetId': aid, 'map': point, 'scale': sx, 'tiledObjectId': obj['id'], 'anchorRoundtripEditorPx': math.dist(project(point, meta), pixel)})
    if not blocks:
        raise ValueError('Viewer requires at least one block')
    layout.update({'blocks': blocks, 'parcels': [], 'status': 'isolated-modular-pilot-manual-calibration-not-accepted', 'tiledSourceSHA256': sha(path)})
    # Preserve expanded ground enclosure and initial rider. Overview only changes view.
    layout['camera'] = dict(layout['camera'], focusMap=[-1590, 59], viewWidthUnits=80)
    layout['camera'].pop('zoom', None)
    out = HERE / 'runtime/assets'; out.mkdir(parents=True, exist_ok=True)
    for a in manifest['assets']:
        source = HERE / 'assets' / a['file']
        if sha(source) != a['sha256']:
            raise ValueError('Native copy SHA mismatch '+a['id'])
        shutil.copyfile(source, out / a['file'])
    write(out / 'asset-manifest.json', manifest); write(out / 'scene-layout.json', layout)
    write(HERE / 'runtime/import-report.json', {'map': str(path.relative_to(HERE)), 'mapSHA256': sha(path),
          'status': 'data-integrity-only-no-engine-or-game-test', 'objects': report, 'visibleInstances': len(blocks), 'hiddenTemplateInstances': hidden,
          'roadsUnchanged': layout['roads'] == read(BASE / 'scene-layout.json')['roads'],
          'riderUnchanged': layout['rider'] == read(BASE / 'scene-layout.json')['rider'],
          'expandedBoundsUnchanged': layout['bounds'] == previous_bounds, 'bounds': previous_bounds,
          'originalRoadReferenceBytewiseEqual': sha(HERE / 'original-roads.png') == sha(PROBE / 'original-roads.png'),
          'nativeAssetSHAsPreserved': True, 'maxAnchorRoundtripEditorPx': max(r['anchorRoundtripEditorPx'] for r in report),
          'runtimeDrawOrder': 'Existing viewer projected sortMap depth. Tiled object index order not reproduced.',
          'caveats': ['Manual anchor and dimensions candidates, no camera/art acceptance.', 'Hidden template groups omitted; toggle group visible in Tiled and re-import to preview.', 'No game stage tests, source/build modifications, or save access.']})
    print('Exported', len(blocks), 'visible instances;', hidden, 'hidden template instances; roads/rider/bounds preserved')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('prepare', 'import'))
    parser.add_argument('--map', type=Path, default=HERE / 'pilot.tmj')
    args = parser.parse_args()
    prepare() if args.command == 'prepare' else import_map(args.map)
