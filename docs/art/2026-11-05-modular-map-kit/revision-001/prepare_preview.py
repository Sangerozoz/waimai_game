#!/usr/bin/env python3
"""Package recovered native revision images into an isolated Tiled/Cocos preview.

No generation, raster edits, source-game edits, or writes to the original maps.
Ground corners are manual display candidates, not camera/physical validation.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

from PIL import Image

HERE = Path(__file__).resolve().parent
KIT = HERE.parent
ROOT = KIT.parents[2]
OLD = KIT / 'integration'
OUT = HERE / 'integration'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def native_info(path):
    with Image.open(path) as image:
        alpha = image.getchannel('A')
        hist = alpha.histogram()
        return {'size': list(image.size), 'mode': image.mode,
                'alphaExtrema': list(alpha.getextrema()),
                'alphaZeroPixels': hist[0], 'sha256': sha(path)}


def main():
    if (OUT / 'pilot.tmj').exists():
        raise SystemExit('Refusing to overwrite an editable revision map.')
    protected = [OLD / 'pilot.tmj', KIT / 'viewer/assets/scene-layout.json',
                 ROOT / 'docs/research/2026-11-05-map-production/tiled-probe/probe.tmj',
                 ROOT / 'delivery-game/assets/resources/map-sample/city.json']
    before = {str(p.relative_to(ROOT)): sha(p) for p in protected}
    spec = importlib.util.spec_from_file_location('isolated_bridge', OLD / 'build_integration.py')
    bridge = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bridge)
    bridge.HERE = OUT
    bridge.PILOT = HERE
    bridge.BASE = OLD / 'runtime/assets'
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'assets').mkdir(exist_ok=True)
    shutil.copyfile(OLD / 'bridge-meta.json', OUT / 'bridge-meta.json')
    shutil.copyfile(OLD / 'original-roads.png', OUT / 'original-roads.png')
    meta = load(OUT / 'bridge-meta.json')
    old_manifest = load(OLD / 'assets/asset-manifest.json')
    originals = {a['id']: a for a in old_manifest['assets']}
    replacements = {
        'B01-F00': ('B01-F00-v3.png', {'left': [70, 908], 'front': [914, 1136], 'right': [1242, 866]}),
        'B01-F90': ('B01-F90-v2.png', {'left': [66, 882], 'front': [332, 1090], 'right': [1253, 919]}),
        'B01-F180': ('B01-F180-v2.png', {'left': [66, 907], 'front': [914, 1111], 'right': [1240, 866]}),
        'B01-F270': ('B01-F270-v2.png', {'left': [75, 800], 'front': [330, 977], 'right': [1465, 847]}),
        'T01': ('T01-v1.png', {'left': [393, 1022], 'front': [621, 1174], 'right': [842, 1016]}),
    }
    assets = []
    for aid in ('B01-F00', 'B01-F90', 'B01-F180', 'B01-F270', 'T01', 'L01', 'L02'):
        old = originals[aid]
        fields = ('id', 'file', 'groundCornersPixels', 'anchorPixel',
                  'nativePixelsPerUnit', 'scaleMethod', 'footprintMeters',
                  'heightMeters', 'anchorMap', 'orientationVariant')
        candidate = {k: copy.deepcopy(old[k]) for k in fields if k in old}
        if aid in replacements:
            candidate['file'], candidate['groundCornersPixels'] = replacements[aid]
            candidate.pop('anchorPixel', None)
            candidate.pop('nativePixelsPerUnit', None)
            candidate['observations'] = [
                'Recovered native image, copied bytewise; no raster rotation, mirror, crop or repaint.',
                'Facade visibility revision only. Uniform scale and manually estimated base corners are display candidates.',
                'Ground-edge angles differ from the unchanged source-road projection; NOT camera/registration accepted.',
                'White/chromatic edge remnants and independent-view geometry/roof-equipment differences remain for review.',
            ]
            if aid == 'T01':
                candidate['observations'] = [
                    'Restore exact user-preferred T01-v1 native bytes and full visible trunk. Not a newly generated tree.',
                    'Uniform tree-pit scale is a display candidate only. Nominal six metres is NOT an acceptance limit.',
                    'Tree perspective and green/pale edge fringes still require visual review.',
                ]
        else:
            shutil.copyfile(KIT / 'pilot' / candidate['file'], HERE / candidate['file'])
            candidate['observations'] = copy.deepcopy(old.get('observations', []))
        assets.append(bridge.calibration_asset(candidate, meta))
    keep = [copy.deepcopy(a) for a in old_manifest['assets'] if a['id'] in ('HC-R-NE', 'HC-R-SW', 'S01-paving', 'S02-asphalt')]
    for asset in keep:
        shutil.copyfile(OLD / 'assets' / asset['file'], OUT / 'assets' / asset['file'])
    manifest = {'schemaVersion': 1, 'packageComplete': True,
                'status': 'revision-001-display-candidates-not-accepted',
                'projection': meta['projection'], 'assets': assets + keep,
                'notes': ['Ground projection and source roads unchanged. Sprite camera NOT validated.',
                          'Native bytes preserved. Uniform positive instance scale only.',
                          'No gameplay tests or user acceptance implied.']}
    save(OUT / 'assets/asset-manifest.json', manifest)
    by_id = {a['id']: a for a in assets}
    doc = copy.deepcopy(load(OLD / 'pilot.tmj'))
    tiles = doc['tilesets'][0]['tiles']
    gid_map = {}
    for tile in tiles:
        aid = bridge.props(tile)['assetId']
        asset = by_id[aid]
        gid_map[doc['tilesets'][0]['firstgid'] + tile['id']] = aid
        tile.update(image='assets/' + asset['file'], imagewidth=asset['nativeSize'][0], imageheight=asset['nativeSize'][1])
    doc['tilesets'][0].update(name='B01 facade revision and restored T01-v1 — candidates',
                              tilewidth=max(a['nativeSize'][0] for a in assets),
                              tileheight=max(a['nativeSize'][1] for a in assets))
    object_count = 0
    for layer, visible, shift in bridge.object_layers(doc['layers']):
        for obj in layer['objects']:
            if obj.get('rotation', 0) or obj['gid'] & 0xf0000000:
                raise ValueError('Unexpected source object rotation/mirror')
            aid = gid_map[obj['gid']]
            old = originals[aid]
            u, v = old['anchorUV']
            anchor = [obj['x'] + u * obj['width'], obj['y'] - (1-v) * obj['height']]
            scale = obj['width'] / (old['nativeSize'][0] / old['nativePixelsPerUnit'] * meta['pixelsPerUnit'])
            new = by_id[aid]
            w, h = [n / new['nativePixelsPerUnit'] * meta['pixelsPerUnit'] * scale for n in new['nativeSize']]
            u, v = new['anchorUV']
            obj.update(x=anchor[0]-u*w, y=anchor[1]+(1-v)*h, width=w, height=h)
            object_count += 1
    save(OUT / 'pilot.tmj', doc)
    bridge.import_map(OUT / 'pilot.tmj')
    viewer = HERE / 'viewer'
    shutil.copytree(KIT / 'viewer', viewer)
    for src in (OUT / 'runtime/assets').iterdir():
        if src.is_file():
            shutil.copyfile(src, viewer / 'assets' / src.name)
    after = {str(p.relative_to(ROOT)): sha(p) for p in protected}
    if before != after:
        raise RuntimeError('Protected source changed during packaging')
    runtime = load(viewer / 'assets/scene-layout.json')
    assert runtime['roads'] == load(OLD / 'runtime/assets/scene-layout.json')['roads']
    source_session = Path('/Users/sanger/.codex/generated_images/01a1a949-b8b5-7972-b6f4-d59fd32b7e35')
    native_sources = {
        'B01-F00-v3.png': source_session / 'exec-eb5ab60b-a5bc-413d-b5f8-d150d8486dc6.png',
        'B01-F90-v2.png': source_session / 'exec-bb940df2-5296-4e05-aba1-916fbc996245.png',
        'B01-F180-v2.png': source_session / 'exec-603c916f-e6ad-46bc-be52-a226cb1f19a3.png',
        'B01-F270-v2.png': source_session / 'exec-5c0c4400-6f94-49ec-8e45-3fc5872c0749.png',
        'T01-v1.png': KIT / 'pilot/T01-v1.png',
    }
    records = []
    for name, source in native_sources.items():
        target = HERE / name
        info = native_info(target)
        assert source.is_file() and sha(source) == info['sha256']
        assert sha(viewer / 'assets' / name) == info['sha256']
        records.append({'file': name, 'originalPath': str(source),
                        'bytewiseMatch': True, 'generationTool': 'built-in image_gen (prior source thread)',
                        'newGenerationThisContinuation': False, **info})
    report = {'sourceThread': 'thr_f494gzcxn2',
              'status': 'recovered-and-packaged-not-user-accepted',
              'nativeFiles': records, 'nativeRevisionBuildingViews': 4,
              'restoredTreeViews': 1, 'unchangedLampTypes': 2,
              'editableObjectsIncludingHidden': object_count,
              'visibleInstances': len(runtime['blocks']),
              'protectedBefore': before, 'protectedAfter': after,
              'protectedUnchanged': before == after,
              'sourceRoadsUnchanged': True, 'gameplayTestsRun': False,
              'cameraValidated': False, 'userAccepted': False,
              'knownIssues': ['Ground edges are not parallel to the unchanged 62.5/45 road axes.',
                              'Native edge fringes remain.',
                              'Four independently generated views differ in roof-equipment positions and proportions.',
                              'Rider inherited unchanged from the old enlarged demonstration, not a size standard.']}
    save(HERE / 'recovery-and-delivery.json', report)
    print(json.dumps({'revisionBuildingViews': 4, 'restoredTree': 1,
                      'visibleInstances': len(runtime['blocks']), 'protectedUnchanged': True,
                      'viewer': str(viewer.relative_to(ROOT)), 'allNativeHashesMatch': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()
