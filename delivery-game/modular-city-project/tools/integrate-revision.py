"""Merge PM revision data into isolated runtime data; never edits PM source files."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

parser = argparse.ArgumentParser()
parser.add_argument('revision', type=Path)
args = parser.parse_args()
project = Path(__file__).resolve().parents[1]
base = project / 'revision-backups/mc-rev1-start/deployed-assets'
output = project / 'runtime-data'
output.mkdir(exist_ok=True)
revision = json.loads(args.revision.read_text())
manifest = json.loads((base / 'asset-manifest.json').read_text())
layout = json.loads((base / 'sample-layout.json').read_text())
assets = {a['id']: a for a in manifest['assets']}
for asset in revision['assets']:
    source = args.revision.parent / asset['file']
    if not source.is_file():
        raise ValueError(f'Missing native source {source}')
    if Path(asset['file']).is_absolute() or '..' in Path(asset['file']).parts:
        raise ValueError('Asset file must be a local relative path')
    target = output / asset['file']
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    assets[asset['id']] = asset
placements = {p['id']: p for p in layout['placements']}
for override in revision.get('placementOverrides', []):
    placements[override['id']].update(override)
for p in layout['placements']:
    asset = assets[p['assetId']]
    if asset['kind'] != 'building':
        continue
    if not asset.get('frontage'):
        raise ValueError(f'Building lacks frontage metadata: {p["id"]}')
    front = asset['frontage']
    if not (front.get('entranceUV') or front.get('entranceMapOffset')):
        raise ValueError(f'Building lacks entrance position: {p["id"]}')
    # Recompute whole ground footprint from the new native UV and unchanged projection.
    width = asset['displayWidthMeters'] * p.get('scale', 1)
    points = []
    for u, v in asset['groundPolygon']:
        sx = (u - asset['anchor'][0]) * width
        sy = (v - asset['anchor'][1]) * width * asset['nativeSize'][1] / asset['nativeSize'][0]
        points.append([p['map'][0] + sy + sx / 1.7320508, p['map'][1] + sy - sx / 1.7320508])
    p['groundFootprint'] = points
assets['R01']['displayWidthMeters'] = 6.4
manifest['assets'] = list(assets.values())
manifest['status'] = 'mc-rev1-integrated-candidate-not-user-accepted'
layout['status'] = 'mc-rev1-integrated-candidate-not-game-tested'
layout['revision'] = 'MC-REV1'
# Preserve engine-v3 framing so 6.4m rider is exactly twice the old screen size.
layout['cameraFocus']['fixedScale'] = 0.6129619059310744
layout['cameraFocus']['map'] = [-1591, 75]
layout['cameraFocus']['screenOffset'] = [0, -70]
for name, data in [('asset-manifest.json', manifest), ('sample-layout.json', layout)]:
    (output / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
for asset in manifest['assets']:
    if not (output / asset['file']).exists():
        shutil.copy2(base / asset['file'], output / asset['file'])
record = {
    'revisionSource': str(args.revision.resolve()),
    'sha256': {str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in sorted(output.rglob('*')) if p.is_file() and p.name != 'integration-record.json'},
    'limitations': ['No game tests, typecheck or browser display performed',
                    'Hidden entrance offsets and heights are art candidates, not surveyed geometry',
                    '2D ground projections do not receive on facades'],
}
(output / 'integration-record.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'output': str(output), 'assets': len(manifest['assets']), 'placements': len(layout['placements']),
                  'manifestSHA256': record['sha256']['asset-manifest.json'],
                  'layoutSHA256': record['sha256']['sample-layout.json']}, ensure_ascii=False))
