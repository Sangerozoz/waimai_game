#!/usr/bin/env python3
"""Draw a geometry-only reference from one unchanged source-road segment.
No generated art pixels are modified; this is a proxy, not a delivered sprite.
"""
import hashlib
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
LAYOUT = BASE / 'revision-002/viewer/assets/scene-layout.json'
layout = json.loads(LAYOUT.read_text())
p = layout['projection']
road = next(r for r in layout['roads'] if r['id'] == '149397380-0')
a, b = road['nodes'][10:12]
dx, dy = b[0]-a[0], b[1]-a[1]
length = math.hypot(dx, dy)
u = [dx/length, dy/length]
n = [-u[1], u[0]]
# Candidate dimensions preserve a compact two-storey silhouette; not survey data.
frontage, depth, height = 8.0, 5.5, 8.0
mid = [a[i]+0.6*(b[i]-a[i]) for i in (0, 1)]
center = [mid[i]-n[i]*(road['width']/2+2+depth/2) for i in (0, 1)]
ppu = 108.0
origin = [768.0, 1000.0]

def vec(v):
    return [v[0]*p['axisX'][i]+v[1]*p['axisY'][i] for i in (0, 1)]

def project(local, z: float = 0.0):
    v = vec(local)
    return [origin[i]+ppu*(v[i]+z*p['axisZ'][i]) for i in (0, 1)]

local = [[s*frontage/2*u[i]+t*depth/2*n[i] for i in (0, 1)]
         for s, t in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]
ground = [project(v) for v in local]
roof = [project(v, height) for v in local]
im = Image.new('RGBA', (1536, 1536), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
# A/B are back edge, C/D the road-facing long edge; verticals are exactly vertical.
d.polygon([ground[0], ground[3], roof[3], roof[0]], fill='#ddd6ca', outline='#716d69', width=3)
d.polygon([ground[3], ground[2], roof[2], roof[3]], fill='#f3eee3', outline='#716d69', width=3)
d.polygon(roof, fill='#9296a1', outline='#716d69', width=4)
for i, j in [(0, 3), (3, 2)]:
    for fraction in [0.08, 0.5, 0.94]:
        h = height*fraction
        d.line([tuple(project(local[i], h)), tuple(project(local[j], h))], fill='#b6ad9f', width=4)
# Simple inset parapet: same ground-plane axes, never arbitrary image rotation.
inset = [[x*.94, y*.94] for x, y in local]
d.line([tuple(project(v, height)) for v in inset]+[tuple(project(inset[0], height))], fill='#c8c7cf', width=9)
proxy = HERE / 'road-aligned-building-guide.png'
if proxy.exists():
    raise SystemExit('Refusing to replace an existing guide')
im.save(proxy)
angles = {k: math.degrees(math.atan2(vec(v)[1], vec(v)[0])) for k, v in [('frontage', u), ('depth', n)]}
record = {
    'status': 'geometry-guide-only-not-generated-building-or-acceptance',
    'sourceLayout': str(LAYOUT.relative_to(BASE)),
    'sourceLayoutSHA256': hashlib.sha256(LAYOUT.read_bytes()).hexdigest(),
    'roadId': road['id'], 'sourceNodeIds': road['sourceNodeIds'][10:12],
    'segmentMap': [a, b], 'projection': p, 'streetTangentMap': u,
    'outwardPerpendicularMap': [-v for v in n],
    'groundEdgeAnglesScreenDeg': angles,
    'candidateDimensions': {'frontage': frontage, 'depth': depth, 'height': height,
                            'note': 'PM display candidates, not user dimensions or source measurements'},
    'candidateAnchorMap': center, 'roadReferenceMap': mid,
    'nativeGuidePixelsPerUnit': ppu, 'guideSize': list(im.size),
    'guideAnchorPixel': origin, 'guideGroundCornersABCD': ground,
    'guideRoofCornersABCD': roof,
    'notes': ['Source roads and original Tiled map untouched.',
              'No plane rotation, shear, warp or recolouring of old native sprite.',
              'Image generation must be inspected; numeric guide does not guarantee its output.']}
(HERE / 'road-constraint.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(record, ensure_ascii=False))
