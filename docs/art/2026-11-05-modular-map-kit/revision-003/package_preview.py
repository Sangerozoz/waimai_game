#!/usr/bin/env python3
"""Package a one-building before/after Cocos display without editing old sources.
Requires real native-art metadata from manual inspection, not the geometry proxy.
"""
import copy
import hashlib
import json
from pathlib import Path
import shutil
from PIL import Image

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
OLD = BASE / 'revision-002/viewer'

def read(path):
    return json.loads(path.read_text())

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    target = HERE / 'viewer'
    if target.exists():
        raise SystemExit('Refusing to overwrite an existing viewer; preserve any user edits')
    calibration = read(HERE / 'native-calibration.json')
    native = HERE / calibration['file']
    with Image.open(native) as im:
        size = list(im.size)
        if im.mode != 'RGBA':
            raise ValueError('Expected actual native RGBA')
    if sha(native) != calibration['sha256']:
        raise ValueError('Native PNG differs from inspected original')
    layout = read(OLD / 'assets/scene-layout.json')
    manifest = read(OLD / 'assets/asset-manifest.json')
    constraint = read(HERE / 'road-constraint.json')
    protected = [BASE/'revision-001/integration/revision.tmj',
                 OLD/'assets/scene-layout.json', OLD/'assets/main/index.probe41.js',
                 BASE/'pilot/T01-v1.png', BASE/'pilot/L01-v1.png', BASE/'pilot/L02-v1.png']
    before = {str(p.relative_to(BASE)): sha(p) for p in protected}
    shutil.copytree(OLD, target)
    shutil.copyfile(native, target/'assets'/native.name)
    # Keep approved tree/lights in their original positions; omit other buildings.
    layout['blocks'] = [b for b in layout['blocks'] if b['sourceAssetId'] in ('T01', 'L01', 'L02')]
    aid = 'B01-road-tangent-candidate'
    anchor = constraint['candidateAnchorMap']
    layout['blocks'].append({'assetId': aid, 'anchorMap': anchor, 'sortMap': anchor,
                             'persistentId': aid, 'sourceAssetId': aid, 'scale': 1})
    mid = constraint['roadReferenceMap']
    layout['camera'] = {'focusMap': anchor, 'viewWidthUnits': 8,
                        'screenOffset': [0, 0], 'referenceWidth': 720, 'referenceHeight': 1280}
    layout['status'] = 'isolated-one-building-road-direction-candidate-not-accepted'
    layout['notes'] = [s for s in layout['notes'] if s != 'No testing/typecheck/page automation/save access.']
    layout['notes'].append('Visual-only isolated browser inspection; no game tests or save access.')
    layout['notes'].append('One-building display staging only; not an edited or exported Tiled authority map.')
    layout['rider']['map'] = mid
    asset = {'id': aid, 'kind': 'block', 'file': native.name, 'nativeSize': size,
             'sha256': sha(native), 'anchorUV': calibration['anchorUV'],
             'nativePixelsPerUnit': calibration['nativePixelsPerUnit'],
             'anchorMap': anchor, 'sortMap': anchor,
             'projectionId': constraint['projection']['id'],
             'orientationVariant': 'source-road-149397380-segment-10',
             'status': 'hand-calibrated-native-candidate-not-user-accepted'}
    manifest['assets'].append(asset)
    manifest['status'] = 'one-building-perspective-display-only'
    previous = copy.deepcopy(manifest)
    old = copy.deepcopy(next(a for a in manifest['assets'] if a['id'] == 'B01-F90'))
    old.update({'id': aid, 'anchorMap': anchor, 'sortMap': anchor,
                'status': 'known-wrong-camera-control-at-same-display-anchor'})
    previous['assets'][-1] = old
    write(target/'assets/asset-manifest.json', manifest)
    write(target/'assets/asset-manifest-before.json', previous)
    write(target/'assets/scene-layout.json', layout)
    # Derived shell only. Switch appearance metadata; roads/camera/anchor remain identical.
    bundle = target/'assets/main/index.probe41.js'
    code = bundle.read_text()
    needle = 'fetch(e,{cache:"no-store"})'
    replacement = 'fetch(e.endsWith("asset-manifest.json")&&new URLSearchParams(location.search).get("variant")==="before"?e.replace("asset-manifest.json","asset-manifest-before.json"):e,{cache:"no-store"})'
    if code.count(needle) != 1:
        raise ValueError('Unexpected derived shell fetch implementation')
    bundle.write_text(code.replace(needle, replacement))
    if before != {str(p.relative_to(BASE)): sha(p) for p in protected}:
        raise ValueError('Protected source changed')
    assert layout['roads'] == read(OLD/'assets/scene-layout.json')['roads']
    assert layout['projection'] == read(OLD/'assets/scene-layout.json')['projection']
    approved = [a for a in manifest['assets'] if a['id'] in ('instance-pilot-T01', 'instance-pilot-L01', 'instance-pilot-L02')]
    assert len(approved) == 3
    assert all(sha(target/'assets'/a['file']) == sha(OLD/'assets'/a['file']) for a in approved)
    write(HERE/'package-verification.json', {
        'status': 'static-package-integrity-not-camera-or-game-acceptance',
        'sourceRoadsUnchanged': True, 'sourceProjectionUnchanged': True,
        'approvedTreeAndLightsBytewisePreserved': True, 'protectedSHA256': before,
        'displayInstances': len(layout['blocks']), 'nativePNG': asset,
        'engineRebuilt': False, 'gameTestsRun': False,
        'caveats': ['Before and after share one staged anchor/camera/road; original maps untouched.',
                    'Before/after native raster footprint dimensions are different; this is a direction comparison, not equal-volume proof.',
                    'Native calibration is manually estimated; geometry guide alone does not verify the generated image.']})
    print('Packaged one native building and three unchanged approved tree/light instances')

if __name__ == '__main__':
    main()
