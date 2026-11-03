"""Author native-image metadata from manual pixel annotations. Never edits image pixels."""
from pathlib import Path
import hashlib
import json
import math
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sources = json.loads((ROOT / 'metadata/source-map.json').read_text())['assets']
records = {entry['file']: entry for entry in sources}
inputs = json.loads((ROOT / 'metadata/selected-annotations.json').read_text())
assets, annotations = [], []

def local(pixel, anchor, width, native_width):
    sx = (pixel[0] - anchor[0]) * width / native_width
    sy = (pixel[1] - anchor[1]) * width / native_width
    return [sy + sx / math.sqrt(3), sy - sx / math.sqrt(3)]

for entry in inputs['buildings']:
    path = ROOT / entry['file']
    im = Image.open(path)
    w, h = im.size
    left, front, right = entry['visibleGroundCornersPixels']
    rear = [left[0] + right[0] - front[0], left[1] + right[1] - front[1]]
    polygon = [left, rear, right, front]
    width = entry.get('displayWidthMeters', 18)
    points = [local(p, front, width, w) for p in polygon]
    direction = entry['direction']
    frontage = {'screenSide': 'right' if direction == 'E' else 'left' if direction == 'W' else 'hidden-left',
                'visible': direction != 'N', 'normalMap': [1, 0] if direction == 'E' else [0, 1] if direction == 'W' else [-1, 0]}
    if direction == 'N':
        hidden_door = [(left[0] + rear[0]) / 2, (left[1] + rear[1]) / 2]
        frontage['entranceMapOffset'] = [round(v, 6) for v in local(hidden_door, front, width, w)]
    else:
        frontage['entranceUV'] = [round(entry['entrancePixel'][0] / w, 8), round(entry['entrancePixel'][1] / h, 8)]
    edges = [[left, front], [front, right]]
    vectors = [[q[0] - p[0], q[1] - p[1]] for p, q in edges]
    slopes = [v[1] / v[0] for v in vectors]
    elevation = math.degrees(math.atan(math.sqrt(-slopes[0] * slopes[1])))
    alpha = im.getchannel('A').histogram() if im.mode == 'RGBA' else None
    source = records[entry['file']]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assets.append({'id': entry['id'], 'file': entry['file'], 'kind': 'building', 'nativeSize': [w, h],
                   'anchor': [round(front[0] / w, 8), round(front[1] / h, 8)],
                   'groundPolygon': [[round(x / w, 8), round(y / h, 8)] for x, y in polygon],
                   'footprintMeters': [round(max(p[i] for p in points) - min(p[i] for p in points), 4) for i in (0, 1)],
                   'displayWidthMeters': width, 'heightMeters': entry['heightMeters'], 'frontage': frontage,
                   'source': {'tool': 'built-in image_gen', 'originalPath': source['originalPath'], 'sha256': digest},
                   'notes': ['Native PNG and alpha preserved byte-for-byte; no flip, rotation, shear, crop or recoloring.',
                             'Manual facade-ground corners and doorway candidates. Rear corner and hidden doorway are estimates.',
                             'Camera elevation from hand-picked edges is a candidate, not a calibrated camera or user acceptance.',
                             'Height is an art projection parameter, not surveyed geometry.']})
    annotations.append({'id': entry['id'], 'file': entry['file'], 'anchorPixel': front,
                        'visibleGroundCornersPixels': entry['visibleGroundCornersPixels'],
                        'estimatedRearGroundCornerPixel': rear, 'estimatedVertexIndices': [1],
                        'localGroundFootprintMeters': points, 'frontage': frontage,
                        'inferredElevationIfRectangularDegrees': round(elevation, 3),
                        'visibleGroundEdgeAnglesDegrees': [round(math.degrees(math.atan2(v[1], v[0])), 3) for v in vectors],
                        'alphaZeroPixels': alpha[0] if alpha else None, 'alphaOpaquePixels': alpha[255] if alpha else None,
                        'status': 'candidate-not-user-accepted'})

for id, file in [('S03-entry', 'S03-entry-brick-v1.png'), ('S04-soil', 'S04-soil-grass-v1.png')]:
    path = ROOT / file
    im = Image.open(path)
    assets.append({'id': id, 'file': file, 'kind': 'material', 'nativeSize': list(im.size),
                   'anchor': [], 'groundPolygon': [], 'footprintMeters': [], 'displayWidthMeters': 2,
                   'source': {'tool': 'built-in image_gen', 'originalPath': records[file]['originalPath'],
                              'sha256': hashlib.sha256(path.read_bytes()).hexdigest()},
                   'notes': ['Native opaque material; use on assigned ground regions, not across the entire map.']})

manifest = {'schemaVersion': 1, 'revision': 'MC-REV1', 'status': 'art-candidates-not-user-accepted',
            'projection': {'axisX': [.8660254, .5], 'axisY': [-.8660254, .5], 'vertical': [0, -1], 'pixelsPerMeter': 32},
            'assets': assets, 'placementOverrides': inputs['placementOverrides'],
            'cameraFocusOverride': {'fixedScale': 0.6129619059310744},
            'limitations': ['Hidden facades/entrances are not visible from current camera; metadata is a candidate.',
                            'Ground projections are 2D approximations and do not receive on vertical facades.',
                            'No game tests, browser display verification or user acceptance claimed.']}
(ROOT / 'revision-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
(ROOT / 'metadata/current-annotations.json').write_text(json.dumps({'schemaVersion': 1, 'annotations': annotations}, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'assets': len(assets), 'placements': len(inputs['placementOverrides']),
                  'manifestSHA256': hashlib.sha256((ROOT / 'revision-manifest.json').read_bytes()).hexdigest(),
                  'cameraCandidates': {a['id']: a['inferredElevationIfRectangularDegrees'] for a in annotations}}, ensure_ascii=False))
