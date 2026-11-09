#!/usr/bin/env python3
"""Offline file/image inventory only. Does not import/execute game TypeScript.
Compares hashes, crop arithmetic, image dimensions/alpha and metadata UUIDs.
"""
from pathlib import Path
import hashlib
import json
import uuid
from PIL import Image

DOC = Path(__file__).resolve().parent
ROOT = DOC.parents[4]
RES = ROOT / 'delivery-game/assets/resources'
OUT = RES / 'ui-v2/web'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    report = json.loads((DOC / 'asset-records.json').read_text())
    pack = json.loads((OUT / 'pack.json').read_text())
    previous = json.loads((DOC.parent / 'asset-audit.json').read_text())
    previous_sources = {row['source']: row for row in previous['assets']}
    issues, all_aliases, derived_paths, generated_uuids = [], set(), set(), set()
    prior_matches = []
    for resource, source in report['sources'].items():
        path = Path(source['path'])
        if sha(path) != source['sha256']:
            issues.append('source changed: ' + str(path))
        prior = previous_sources.get(str(path))
        if prior:
            prior_matches.append(str(path))
            if sha(path) != prior['sha256']:
                issues.append('source changed since original resource audit: ' + str(path))
        if resource.startswith('ui-v2/map-preview-'):
            issues.append('map source incorrectly included')
    for asset in report['assets']:
        for alias in asset['keys']:
            if alias in all_aliases:
                issues.append('duplicate alias: ' + alias)
            all_aliases.add(alias)
        derivative = asset['derivative']
        path = Path(derivative['path'])
        derived_paths.add(path)
        if not path.is_relative_to(OUT):
            issues.append('output outside exclusive web scope: ' + str(path))
        if sha(path) != derivative['sha256'] or path.stat().st_size != derivative['bytes']:
            issues.append('derivative size/hash mismatch: ' + str(path))
        with Image.open(path) as image:
            if list(image.size) != derivative['size']:
                issues.append('derivative dimensions differ: ' + str(path))
        x, y, w, h = asset['sourceRect']
        with Image.open(asset['source']) as source:
            crop = source.crop((x, y, x+w, y+h))
            needs_alpha = 'A' in crop.getbands() and crop.getchannel('A').getextrema() != (255, 255)
            if needs_alpha and path.suffix != '.png':
                issues.append('alpha source not kept in PNG: ' + str(path))
        lookup = pack['sources'][asset['sourceResource']]['regions'][','.join(map(str, asset['sourceRect']))]
        if lookup['resource'] != derivative['resource'] or lookup['size'] != derivative['size']:
            issues.append('runtime mapping mismatch: ' + str(path))
        for key, inset in asset['scaledInsets'].items():
            dw, dh = derivative['size']
            if any(value < 0 for value in inset.values()) or inset['left']+inset['right'] > dw or inset['top']+inset['bottom'] > dh:
                issues.append('scaled inset outside derivative: ' + key)
        meta = json.loads(Path(str(path)+'.meta').read_text())
        identifier = meta['uuid']
        uuid.UUID(identifier)
        if identifier in generated_uuids:
            issues.append('duplicate generated UUID: ' + identifier)
        generated_uuids.add(identifier)
        texture = meta['subMetas']['6c48a']
        if texture['uuid'] != identifier+'@6c48a' or texture['name'] != 'texture' or meta['userData']['redirect'] != texture['uuid']:
            issues.append('texture metadata route mismatch: ' + str(path))
    auxiliary_meta = []
    all_generated_uuids = set(generated_uuids)
    for path in (OUT / 'pack.json.meta', RES / 'ui-v2/web.meta'):
        meta = json.loads(path.read_text())
        identifier = meta['uuid']
        uuid.UUID(identifier)
        if identifier in all_generated_uuids:
            issues.append('duplicate auxiliary UUID: ' + identifier)
        all_generated_uuids.add(identifier)
        auxiliary_meta.append(dict(path=str(path), uuid=identifier, importer=meta['importer']))
    collisions = []
    for path in (ROOT / 'delivery-game/assets').rglob('*.meta'):
        if path.is_relative_to(OUT) or path == RES / 'ui-v2/web.meta':
            continue
        try:
            identifier = json.loads(path.read_text()).get('uuid')
        except (ValueError, OSError):
            continue
        if identifier in all_generated_uuids:
            collisions.append(str(path))
    issues.extend('UUID collides with ' + path for path in collisions)
    image_files = {p for p in OUT.iterdir() if p.suffix in ('.png', '.jpg')}
    if image_files != derived_paths:
        issues.append('unregistered image file in web pack')
    # Map sources are only hashed against the existing inventory: no crop,
    # generation, alias, mapping, map-preview or maps.json write occurs.
    maps = []
    for source, prior in previous_sources.items():
        if prior['group'] == 'map_cards':
            path = Path(source)
            record = dict(path=source, sha256=sha(path), matchesPrevious=sha(path) == prior['sha256'])
            maps.append(record)
            if not record['matchesPrevious']:
                issues.append('map original differs from pre-existing audit: ' + source)
    hero = next(a for a in report['assets'] if 'portraits/hero' in a['keys'])
    if 'cartoon/avatar' not in hero['keys']:
        issues.append('hero source crop split between loaders')
    source_files = []
    for name in ('UIArtResources.ts', 'V2ImageSkin.ts', 'CartoonArt.ts', 'VehicleSideArt.ts', 'FoodImages.ts'):
        path = ROOT / 'delivery-game/assets/scripts/map-sample' / name
        source_files.append(dict(path=str(path), sha256=sha(path)))
    manifests = []
    for name in ('manifest', 'portraits', 'maps'):
        path = RES / f'ui-v2/{name}.json'
        manifests.append(dict(path=str(path), bytes=path.stat().st_size, sha256=sha(path), modifiedByThisWork=False))
    summary = dict(scope='offline images/files/arithmetic only; not game/runtime/build validation',
                   sources=len(report['sources']), derivativeImages=len(derived_paths), aliases=len(all_aliases),
                   sourcesMatchingEarlierAudit=len(prior_matches), mapsUnchanged=maps,
                   pngCount=sum(p.suffix == '.png' for p in derived_paths), jpegCount=sum(p.suffix == '.jpg' for p in derived_paths),
                   uniqueImageUuids=len(generated_uuids), uniqueAllGeneratedUuids=len(all_generated_uuids), auxiliaryMeta=auxiliary_meta, collisions=collisions,
                   sharedHero=dict(aliases=hero['keys'], sourceRect=hero['sourceRect'], resource=hero['derivative']['resource']),
                   originalBytes=sum(s['bytes'] for s in report['sources'].values()),
                   derivativeBytes=sum(p.stat().st_size for p in derived_paths),
                   mappingBytes=(OUT/'pack.json').stat().st_size,
                   manifests=manifests, sourceFiles=source_files, issues=issues)
    (DOC / 'image-inventory.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if issues:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
