#!/usr/bin/env python3
"""Prepare read-only-source crops and labelled geometry proxies, NOT native art.
Run from anywhere with Python 3 + Pillow + NumPy. Writes only beside this script.
Default refuses existing outputs; --refresh replaces only this script's outputs.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

HERE = Path(__file__).resolve().parent
assert HERE.name == 'references' and HERE.parent.name == 'revision-005'
KIT = HERE.parent.parent
ROOT = next(p for p in HERE.parents if (p / 'AGENTS.md').is_file())
SIZE = 1536
MARGIN = 100
# Extra clearance for corner markers; header/footer are guide annotations only.
FIT = (124.0, 150.0, 1412.0, 1368.0)
IDS = ['B02', 'B03', 'B04', 'B05']
EXPECTED = {'B02': (10, 7, 14), 'B03': (7, 6, 18),
            'B04': (12, 9, 7), 'B05': (7, 5, 7.5)}
LIGHT = ('Match accepted B01 qualitatively: soft daylight from the upper-left, '
         'light roof/parapet highlights, restrained neutral facade shading, '
         'small rooftop shadows falling broadly away toward the lower-right. '
         'This is visual guidance, not a measured light vector; no yellow wash or glowing windows.')
APPEARANCE = {
    'B02': 'Selected TR-22 terraced office: blue-green horizontal glazing bands, pale stone/white framing, clearly receding upper storeys, compact rooftop service core. Source terrace greenery is context, not permission for rooftop trees.',
    'B03': 'Selected TR-33 slim mid-rise: tall blue-green vertical glazed bays between pale stone piers, a narrow upright silhouette and small rooftop service cap; not an apartment/storefront clone.',
    'B04': 'Selected TR-22 low public pavilion: pale stone broad low wings, a raised central hall with a long narrow roof light, warm dark entrance glazing and a prominent vertical entrance surround. Do not include the outdoor sculpture or forecourt.',
    'B05': 'SOURCE FRAMING LIMITATION: the exact selected TR-22 box contains only a partial pale lower facade/forecourt, vegetation and much blank outer margin; the intended complete house and roof are NOT visible. Do not infer roof identity from neighboring houses or claim this crop proves a gable. The two-storey pitched dwelling is the canonical PM candidate, pending parent source-identity review before native generation.'
}
DESIGN = {
    'B02': 'A genuine three-tier terraced glass office, not a single cuboid. Full 10x7 base reaches z=4.6; middle tier is inset along both ends and especially the road-facing edge and reaches z=9.2; upper tier recedes again and reaches z=13.3; small service core alone reaches total z=14. Keep the terraces open and clearly separated, with parapets but no planted trees. No B01 shop fascia.',
    'B03': 'A narrow vertically articulated glass mid-rise, footprint 7x6. Main shaft z=16.7 and compact roof service cap to total z=18. Strong slim vertical stone piers and continuous glazed bays, a modest recessed entry, no broad B01 horizontal shop bands; keep the tall silhouette.',
    'B04': 'A broad low public exhibition pavilion, full candidate envelope 12x9. Raised central hall to z=6.4, narrow roof-light volume to total z=7, two genuinely low asymmetric side wings z=3.4/3.0, recessed central public entrance and shallow canopy z=3.5. Retain the stepped low roofline and broad entrance, not a seven-unit-high box or shopping block.',
    'B05': 'A compact two-storey dwelling, wall footprint 7x5, wall/eave height 5.5 plus a 2-unit pitched roof rise to ridge z=7.5. Ridge runs parallel to frontage; show both roof slopes and the visible gable end as in guide. Slate blue-grey roof, pale domestic walls, modest door and windows; no flat roof/parapet shop conversion. Roof overhang candidate is 0.25 at the ends and 0.30 at the depth edges.'
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return str(path.relative_to(ROOT))


def font(size):
    for path in ('/System/Library/Fonts/Supplemental/Arial.ttf',
                 '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def rounded(v):
    if isinstance(v, float):
        return round(v, 8)
    if isinstance(v, (tuple, list)):
        return [rounded(x) for x in v]
    if isinstance(v, dict):
        return {k: rounded(x) for k, x in v.items()}
    return v


def box(name, s0, s1, t0, t1, z0, z1):
    return {'name': name, 'rect': [s0, s1, t0, t1], 'z0': z0, 'z1': z1}


def rect_vertices(rect, z):
    s0, s1, t0, t1 = rect
    return [(s0, t0, z), (s1, t0, z), (s1, t1, z), (s0, t1, z)]


def subtract_rect(rect, cut):
    x0, x1, y0, y1 = rect
    a0, a1, b0, b1 = cut
    a0, a1, b0, b1 = max(x0, a0), min(x1, a1), max(y0, b0), min(y1, b1)
    if a1 <= a0 or b1 <= b0:
        return [rect]
    candidates = [[x0, a0, y0, y1], [a1, x1, y0, y1],
                  [a0, a1, y0, b0], [a0, a1, b1, y1]]
    return [r for r in candidates if r[1] - r[0] > 1e-8 and r[3] - r[2] > 1e-8]


def model(asset):
    if asset == 'B02':
        solids = [box('base', -5, 5, -3.5, 3.5, 0, 4.6),
                  box('middle-setback', -4.7, 4.7, -3.5, 2.1, 4.6, 9.2),
                  box('upper-setback', -4.4, 2.4, -3.5, 0.6, 9.2, 13.3),
                  box('service-core', -3.4, -1.5, -2.7, -1.0, 13.3, 14)]
    elif asset == 'B03':
        solids = [box('vertical-main-shaft', -3.5, 3.5, -3, 3, 0, 16.7),
                  box('roof-service-cap', -2.4, 2.4, -2.1, 1.7, 16.7, 18)]
    elif asset == 'B04':
        solids = [box('complete-low-plinth', -6, 6, -4.5, 4.5, 0, 0.35),
                  box('left-low-wing', -6, -3.3, -4.5, 4.5, 0.35, 3.4),
                  box('right-low-wing', 3.3, 6, -4.5, 4.5, 0.35, 3.0),
                  box('central-exhibition-hall', -3.3, 3.3, -4.5, 3.0, 0.35, 6.4),
                  box('entrance-canopy', -2.5, 2.5, 3.0, 4.5, 3.25, 3.5),
                  box('entrance-left-post', -2.45, -2.25, 4.1, 4.3, 0.35, 3.25),
                  box('entrance-right-post', 2.25, 2.45, 4.1, 4.3, 0.35, 3.25),
                  box('long-narrow-roof-light', -2.6, 2.6, -3.4, -2.1, 6.4, 7)]
    else:
        solids = [box('two-storey-wall-body', -3.5, 3.5, -2.5, 2.5, 0, 5.5)]
    faces, verticals, roofs = [], [], []
    for b in solids:
        g, r = rect_vertices(b['rect'], b['z0']), rect_vertices(b['rect'], b['z1'])
        faces += [(b['name'], 'wall-left', [g[0], g[3], r[3], r[0]]),
                  (b['name'], 'wall-front', [g[3], g[2], r[2], r[3]]),
                  (b['name'], 'roof', r)]
        verticals += [[g[i], r[i]] for i in range(4)]
        exposed = [b['rect']]
        for other in solids:
            if other is b or other['z0'] > b['z1'] + 1e-8 or other['z1'] <= b['z1'] + 1e-8:
                continue
            exposed = [piece for r0 in exposed for piece in subtract_rect(r0, other['rect'])]
        if asset != 'B05':
            roofs += [{'name': b['name'] + '-exposed-' + str(i + 1),
                       'vertices': rect_vertices(r0, b['z1'])} for i, r0 in enumerate(exposed)]
    if asset == 'B05':
        # Do not draw a fake flat roof under the gable.
        faces = [f for f in faces if f[1] != 'roof']
        e = rect_vertices([-3.75, 3.75, -2.8, 2.8], 5.5)
        ra, rb = (-3.75, 0, 7.5), (3.75, 0, 7.5)
        slopes = [('rear-pitched-slope', [e[0], e[1], rb, ra]),
                  ('front-pitched-slope', [ra, rb, e[2], e[3]])]
        faces += [(name, 'roof', points) for name, points in slopes]
        faces += [('visible-gable', 'wall-left', [e[0], e[3], ra])]
        roofs = [{'name': name, 'vertices': points} for name, points in slopes]
    return solids, faces, verticals, roofs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', action='store_true')
    args = parser.parse_args()
    outputs = []

    def output(name):
        p = HERE / name
        assert p.resolve().is_relative_to(HERE), 'Write escaped reference ownership'
        if p.exists() and not args.refresh:
            raise RuntimeError('Refusing existing output; use --refresh for owned files: ' + str(p))
        p.parent.mkdir(parents=True, exist_ok=True)
        outputs.append(p)
        return p

    def save_json(name, data):
        # Preserve the canonical road/projection float precision in references.
        output(name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

    selection_path = KIT / 'building-selection.json'
    brief_path = HERE.parent / 'production-brief.json'
    constraint_path = KIT / 'revision-003/road-constraint.json'
    constraint_script = KIT / 'revision-003/make_road_guide.py'
    selection = {b['id']: b for b in json.loads(selection_path.read_text())}
    brief = json.loads(brief_path.read_text())
    candidates = {b['id']: b for b in brief['buildings']}
    constraint = json.loads(constraint_path.read_text())
    layout_path = KIT / constraint['sourceLayout']
    assert sha(layout_path) == constraint['sourceLayoutSHA256']
    layout = json.loads(layout_path.read_text())
    road = next(r for r in layout['roads'] if r['id'] == constraint['roadId'])
    assert road['nodes'][10:12] == constraint['segmentMap']
    assert road['sourceNodeIds'][10:12] == constraint['sourceNodeIds']
    p = constraint['projection']
    assert layout['projection'] == p
    u = constraint['streetTangentMap']
    # B01's make_road_guide uses LEFT-normal n for positive depth.
    # road-constraint stores OUTWARD = -n. Do not silently use outward as +depth.
    n = [-x for x in constraint['outwardPerpendicularMap']]
    assert all(abs(n[i] - [-u[1], u[0]][i]) < 1e-12 for i in (0, 1))
    a, b = constraint['segmentMap']
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    assert all(abs(u[i] - (b[i] - a[i]) / length) < 1e-12 for i in (0, 1))

    def world(q):
        s, t, z = q
        return [s * u[i] + t * n[i] for i in (0, 1)] + [z]

    def screen(q):
        x, y, z = world(q)
        return [x * p['axisX'][i] + y * p['axisY'][i] + z * p['axisZ'][i] for i in (0, 1)]

    def angle(q):
        x, y = screen(q)
        return math.degrees(math.atan2(y, x))

    angles = {'frontage': angle((1, 0, 0)), 'depth': angle((0, 1, 0))}
    assert all(abs(angles[k] - constraint['groundEdgeAnglesScreenDeg'][k]) < 1e-10 for k in angles)
    assert all(abs(angles[k] - brief[k + 'AngleScreenDeg']) < 1e-10 for k in angles)
    b01_error = []
    for z, key in [(0, 'guideGroundCornersABCD'), (8, 'guideRoofCornersABCD')]:
        for q, expected in zip(rect_vertices([-4, 4, -2.75, 2.75], z), constraint[key]):
            projected = screen(q)
            b01_error.extend(abs(constraint['guideAnchorPixel'][i] + constraint['nativeGuidePixelsPerUnit'] * projected[i] - expected[i]) for i in (0, 1))
    assert max(b01_error) < 1e-9
    elev = math.radians(p['elevationDeg'])
    viewer_direction = [(u[0] + u[1]) / math.sqrt(2) * math.cos(elev),
                        (n[0] + n[1]) / math.sqrt(2) * math.cos(elev), math.sin(elev)]
    assert all(abs(v) < 1e-12 for v in screen(viewer_direction))

    def planes_for_box(box0):
        x0, x1, y0, y1 = box0['rect']
        return [((1, 0, 0), x1), ((-1, 0, 0), -x0),
                ((0, 1, 0), y1), ((0, -1, 0), -y0),
                ((0, 0, 1), box0['z1']), ((0, 0, -1), -box0['z0'])]

    def ray_hits(q, planes):
        lo, hi = 1e-6, float('inf')
        for normal, bound in planes:
            start = sum(normal[i] * q[i] for i in range(3))
            delta = sum(normal[i] * viewer_direction[i] for i in range(3))
            bound -= 1e-7  # strict interior, not a merely touching edge
            if abs(delta) < 1e-12:
                if start > bound:
                    return False
            elif delta > 0:
                hi = min(hi, (bound - start) / delta)
            else:
                lo = max(lo, (bound - start) / delta)
        return hi > lo

    def fit(points):
        xy = [screen(q) for q in points]
        bounds = [min(v[0] for v in xy), min(v[1] for v in xy),
                  max(v[0] for v in xy), max(v[1] for v in xy)]
        ppu = math.floor(min((FIT[2] - FIT[0]) / (bounds[2] - bounds[0]),
                             (FIT[3] - FIT[1]) / (bounds[3] - bounds[1])) * 1000) / 1000
        anchor = [(FIT[i] + FIT[i + 2]) / 2 - ppu * (bounds[i] + bounds[i + 2]) / 2 for i in (0, 1)]

        def project(q):
            xy0 = screen(q)
            return [anchor[i] + ppu * xy0[i] for i in (0, 1)]

        return ppu, anchor, project

    def dashed(draw, p0, p1, fill, width=3):
        dist = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        for start in range(0, int(dist), 19):
            end = min(start + 10, dist)
            draw.line([(p0[0] + (p1[0] - p0[0]) * k / dist,
                        p0[1] + (p1[1] - p0[1]) * k / dist) for k in (start, end)], fill=fill, width=width)

    def base_image(asset, dimensions):
        im = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)
        draw.text((60, 22), asset + ' | GEOMETRY ONLY - NOT NATIVE ART', font=font(32), fill='#23455d')
        draw.text((60, 68), dimensions + ' | PM candidate, not source survey', font=font(24), fill='#45515a')
        draw.text((60, 1416), 'Orange dashed: ground ABCD | Cyan: exposed roof constraints | Magenta: ground-centre anchor', font=font(23), fill='#45515a')
        draw.text((60, 1450), 'Frontage -28.486362689 deg | Depth +55.405984491 deg | Wall verticals stay screen-vertical', font=font(23), fill='#45515a')
        draw.text((60, 1484), 'Annotations/proxy shading are NOT final art. Do not copy labels, lines or proxy materials.', font=font(23), fill='#45515a')
        return im, draw

    def draw_proxy_faces(im, faces, project):
        # Depth-aware flat constraint rendering prevents a broad lower roof from
        # overpainting a small higher skylight. This is proxy geometry, NOT art.
        rgba = np.zeros((SIZE, SIZE, 4), dtype=np.uint8)
        zbuffer = np.full((SIZE, SIZE), -np.inf, dtype=np.float32)
        colors = {'wall-left': (191, 198, 202, 255),
                  'wall-front': (225, 229, 231, 255), 'roof': (161, 179, 190, 255)}
        projected_faces = []
        for name, kind, vertices in faces:
            xy = np.asarray([project(q) for q in vertices], dtype=np.float64)
            dep = np.asarray([sum(q[i] * viewer_direction[i] for i in range(3)) for q in vertices])
            projected_faces.append((xy, dep))
            for j in range(1, len(vertices) - 1):
                tri = xy[[0, j, j + 1]]
                depths = dep[[0, j, j + 1]]
                x0, y0 = np.maximum(np.floor(tri.min(axis=0)).astype(int), 0)
                x1, y1 = np.minimum(np.ceil(tri.max(axis=0)).astype(int), SIZE - 1)
                yy, xx = np.mgrid[y0:y1 + 1, x0:x1 + 1]
                xx, yy = xx + 0.5, yy + 0.5
                ax, ay = tri[0]
                bx, by = tri[1]
                cx, cy = tri[2]
                det = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
                if abs(det) < 1e-9:
                    continue
                w0 = ((by - cy) * (xx - cx) + (cx - bx) * (yy - cy)) / det
                w1 = ((cy - ay) * (xx - cx) + (ax - cx) * (yy - cy)) / det
                w2 = 1 - w0 - w1
                z = w0 * depths[0] + w1 * depths[1] + w2 * depths[2]
                zb = zbuffer[y0:y1 + 1, x0:x1 + 1]
                take = (w0 >= -1e-8) & (w1 >= -1e-8) & (w2 >= -1e-8) & (z >= zb)
                rgba[y0:y1 + 1, x0:x1 + 1][take] = colors[kind]
                zb[take] = z[take]
        overlay = Image.fromarray(rgba)
        od = ImageDraw.Draw(overlay)
        for xy, depths in projected_faces:
            for i in range(len(xy)):
                j = (i + 1) % len(xy)
                steps = max(2, int(np.linalg.norm(xy[j] - xy[i]) * 2))
                last = None
                for fraction in np.linspace(0, 1, steps):
                    point = xy[i] + fraction * (xy[j] - xy[i])
                    x, y = np.rint(point).astype(int)
                    z = depths[i] + fraction * (depths[j] - depths[i])
                    if 0 <= x < SIZE and 0 <= y < SIZE and z >= float(zbuffer[y, x]) - 0.025:
                        if last is not None:
                            od.line([last, tuple(point)], fill='#536573', width=3)
                        last = tuple(point)
                    else:
                        last = None
        im.alpha_composite(overlay)

    def mark_ground(draw, project, corners, anchor):
        ground = [project(q) for q in corners]
        for i in range(4):
            dashed(draw, ground[i], ground[(i + 1) % 4], '#d28223')
        for name, point in zip('ABCD', ground):
            x, y = point
            draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill='#ed9f3a', outline='#6b4514', width=2)
            draw.text((x + 10, y - 26), name, font=font(25), fill='#a75e11')
        x, y = anchor
        draw.line((x - 15, y, x + 15, y), fill='#bf3c99', width=4)
        draw.line((x, y - 15, x, y + 15), fill='#bf3c99', width=4)
        return ground

    source_paths = {selection_path, brief_path, constraint_path, constraint_script, layout_path}
    original_style = ROOT / 'docs/art/2026-11-03-whole-region-map/references/2026-11-03-user-building-variety.png'
    accepted_b01 = KIT / 'revision-003/B01-road-aligned-native-v1.png'
    accepted_t01 = KIT / 'pilot/T01-v1.png'
    source_paths.update([original_style, accepted_b01, accepted_t01])
    source_paths.update(ROOT / selection[asset]['source'] for asset in IDS)
    source_before = {rel(path): sha(path) for path in source_paths}
    crops, records, checks = {}, [], []
    for asset in IDS:
        selected, candidate = selection[asset], candidates[asset]
        dims = tuple(candidate[k] for k in ('frontage', 'depth', 'height'))
        assert dims == EXPECTED[asset], 'Canonical production dimensions changed; review before generating'
        source = ROOT / selected['source']
        actual_sha = sha(source)
        assert actual_sha == selected['sourceSHA256'], 'Original source hash mismatch: ' + asset
        with Image.open(source) as raw:
            selected_box = selected['selectionBoxPixels']
            assert len(selected_box) == 4 and all(isinstance(v, int) for v in selected_box)
            x0, y0, x1, y1 = selected_box
            assert 0 <= x0 < x1 <= raw.width and 0 <= y0 < y1 <= raw.height
            crop_box = (max(0, x0 - 8), max(0, y0 - 8), min(raw.width, x1 + 8), min(raw.height, y1 + 8))
            crop = raw.crop(crop_box)
            crop_path = output(asset + '-appearance.png')
            crop.save(crop_path)
            source_size = list(raw.size)
            assert crop.tobytes() == raw.crop(crop_box).tobytes()
        crops[asset] = {'source': rel(source), 'sourceSHA256': actual_sha,
                        'sourceSHA256MatchesSelection': True, 'sourceSizeActual': source_size,
                        'selectionBoxPixelsExact': selected_box, 'contextMarginPixels': 8,
                        'cropBoxPixels': crop_box, 'cropConvention': 'Pillow half-open left,top,right,bottom; unscaled/unfiltered/unmasked',
                        'selectedBoxInCropPixels': [x0 - crop_box[0], y0 - crop_box[1], x1 - crop_box[0], y1 - crop_box[1]],
                        'appearanceFile': crop_path.name, 'appearanceSizeActual': list(crop.size),
                        'appearanceSHA256': sha(crop_path), 'sourceAppearanceNotes': APPEARANCE[asset],
                        'approval': selected['selectionStatus'],
                        'nativeGenerationReadiness': 'blocked-pending-parent-source-identity-review' if asset == 'B05' else 'prepared-awaiting-parent-visual-review',
                        'sourceFramingComplete': asset != 'B05'}
        solids, faces, verticals, roofs = model(asset)
        ground_local = rect_vertices([-dims[0] / 2, dims[0] / 2, -dims[1] / 2, dims[1] / 2], 0)
        all_points = [q for _, _, vertices in faces for q in vertices] + ground_local
        ppu, anchor, project = fit(all_points)
        im, draw = base_image(asset, '%g frontage x %g depth x %g total height' % dims)
        draw_proxy_faces(im, faces, project)
        draw = ImageDraw.Draw(im)
        if asset == 'B03':
            # Plain structural reference lines, not procedural facade art.
            for s in (-2.5, -0.5, 1.5, 2.8):
                draw.line([tuple(project((s, 3, 0.5))), tuple(project((s, 3, 16.7)))], fill='#527d93', width=5)
        planes: list = [planes_for_box(b0) for b0 in solids]
        if asset == 'B05':
            k = 2 / 2.8
            planes.append([((1, 0, 0), 3.75), ((-1, 0, 0), 3.75),
                           ((0, 1, 0), 2.8), ((0, -1, 0), 2.8), ((0, 0, -1), -5.5),
                           ((0, k, 1), 7.5), ((0, -k, 1), 7.5)])
        visible = lambda q: not any(ray_hits(q, polyhedron) for polyhedron in planes)
        roof_records = []
        visible_roof_unique = {}
        for roof in roofs:
            vertices = roof['vertices']
            vr = []
            for i, q in enumerate(vertices):
                if visible(q):
                    point = project(q)
                    key = tuple(q)
                    visible_roof_unique[key] = point
                    vr.append(i)
                    x, y = point
                    draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill='#0c7f9f')
            roof_records.append({'name': roof['name'], 'localVertices': vertices,
                                 'projectedCorners': [project(q) for q in vertices],
                                 'visibleCornerIndicesInProxy': vr})
        ground = mark_ground(draw, project, ground_local, anchor)
        geo_path = output(asset + '-geometry.png')
        im.save(geo_path)
        xy = [project(q) for q in all_points]
        bounds = [min(q[0] for q in xy), min(q[1] for q in xy), max(q[0] for q in xy), max(q[1] for q in xy)]
        assert bounds[0] >= MARGIN and bounds[1] >= MARGIN and bounds[2] <= SIZE - MARGIN and bounds[3] <= SIZE - MARGIN
        vertical_error = max(abs(project(v[0])[0] - project(v[1])[0]) for v in verticals)
        assert vertical_error == 0
        with Image.open(geo_path) as reopened:
            assert reopened.size == (SIZE, SIZE) and reopened.mode == 'RGBA'
        dims_record: dict = dict(zip(('frontage', 'depth', 'height'), dims))
        if asset == 'B05':
            dims_record.update(wallHeight=5.5, roofRise=2.0, roofOverhangFrontage=0.25, roofOverhangDepth=0.30)
        record = {'id': asset, 'status': 'geometry-reference-only-not-native-art-or-acceptance',
                  'dimensionsCandidate': dims_record, 'dimensionAuthority': rel(brief_path),
                  'geometryFile': geo_path.name, 'guideSizeActual': [SIZE, SIZE], 'safetyMarginPixels': MARGIN,
                  'uniformNativeGuidePixelsPerUnit': ppu, 'anchorPixel': anchor,
                  'anchorMeaning': 'footprint ground centre (s=0,t=0,z=0); no map placement authority',
                  'projectedGroundCornersABCD': ground,
                  'projectedVisibleGroundCorners': {name: point for name, q, point in zip('ABCD', ground_local, ground) if visible(q)},
                  'projectedRoofSurfaces': roof_records,
                  'projectedVisibleRoofCorners': [{'local': q, 'pixel': point} for q, point in visible_roof_unique.items()],
                  'visibilityMeaning': 'Exact orthographic ray/convex-volume corner check on THIS proxy only, not on generated native art. Orange hidden ground constraints remain drawn dashed.',
                  'geometryBoundsPixelsIncludingRoofFeatures': bounds, 'fitsSafetyMargin': True,
                  'wallVerticalPairsPixels': [[project(q) for q in pair] for pair in verticals],
                  'wallVerticalMaxHorizontalErrorPixels': vertical_error,
                  'solidsCandidateLocal': solids, 'architectureCandidate': DESIGN[asset],
                  'imageRolesInOrder': [geo_path.name, crop_path.name, rel(original_style), rel(accepted_b01)],
                  'appearanceCrop': crops[asset]}
        if asset == 'B05':
            record['projectedRoofRidgeEndpoints'] = [project((-3.75, 0, 7.5)), project((3.75, 0, 7.5))]
            record['projectedWallEaveCornersABCD'] = [project(q) for q in rect_vertices([-3.5, 3.5, -2.5, 2.5], 5.5)]
        records.append(record)
        checks.append({'id': asset, 'cropPixelsExact': True, 'sourceHashMatchesSelection': True,
                       'geometrySizeActual': [SIZE, SIZE], 'geometryBoundsPixels': bounds,
                       'margin100Fits': True, 'wallVerticalErrorPixels': vertical_error, 'uniformPPU': ppu})
        prompt = '\n'.join([
            ('HOLD: the canonical B05 source box is incomplete; parent must resolve source identity before using this prompt. Candidate instructions below are NOT evidence of source roof identity.\n' if asset == 'B05' else '') +
            'Create exactly ONE new native game-sprite PNG for ' + asset + '. Do not output a sheet or multiple variants.',
            'IMAGE ROLES, in order: (1) ' + geo_path.name + ' = hard geometry/camera and footprint/roof constraints ONLY, NOT final art. '
            '(2) ' + crop_path.name + ' = identity/material source ONLY, ignore its old camera and all context. '
            '(3) user original 2026-11-03-user-building-variety.png = painting/material/diversity style ONLY, never copy its roads/layout/camera. '
            '(4, optional) accepted B01-road-aligned-native-v1.png = qualitative lighting/finish consistency ONLY, never copy its shop/cuboid design.',
            'Orthographic source-road projection, elevation 62.5 deg / azimuth 45 deg; use exact drawn guide, NOT generic 30-degree isometric. '
            'Frontage edges screen -28.486362689 deg, depth edges +55.405984491 deg. All wall verticals exactly screen-vertical. '
            'Ground corners A,B,C,D are ordered rear-left, rear-right, front-right, front-left; road-facing long side is D-C. '
            'Preserve guide chirality, corner relationships and roof massing. No mirror, rotation, shear, warp or editing old sprite pixels.',
            'CANDIDATE ARCHITECTURE (PM dimensions, not surveyed source): ' + DESIGN[asset],
            'SOURCE IDENTITY: ' + APPEARANCE[asset],
            'FINISH: neutral-daylight thick-painted Japanese/anime contemporary urban sprite, restrained clear edges and believable stone, glass and roofing. ' + LIGHT,
            'Whole single building fully inside frame with clear safe margin. Request 1536x1536, true transparent RGBA PNG outside building; '
            'actual returned dimensions and alpha must be checked, not assumed. No opaque backdrop, checkerboard pixels, floor plane, ground patch or baked broad ground shadow. '
            'No text, labels, guide marks, roads, sidewalks, trees, people, vehicles, neighboring buildings, logos, UI, sculpture or rooftop trees. '
            'Do not paste/enlarge the crop as final art; do not copy the flat proxy shading. Exactly one native output.'
        ]) + '\n'
        output('prompts/' + asset + '.txt').write_text(prompt)

    # One contrasting T02 only: wire reference, never procedural tree art.
    tree_dims = {'pitFrontage': 1.8, 'pitDepth': 1.8, 'curbHeight': 0.18,
                 'height': 6.2, 'canopyDiameter': 2.2, 'canopyBottomHeight': 3.4,
                 'canopyTopHeight': 6.2, 'trunkVisibleDesignIntentFromHeight': 0.18,
                 'trunkVisibleDesignIntentToHeight': 3.4}
    pit = rect_vertices([-0.9, 0.9, -0.9, 0.9], 0)
    crown = []
    for axis in ('s', 't'):
        crown.append([(1.1 * math.cos(i * math.pi / 60) if axis == 's' else 0,
                       1.1 * math.cos(i * math.pi / 60) if axis == 't' else 0,
                       4.8 + 1.4 * math.sin(i * math.pi / 60)) for i in range(121)])
    crown.append([(1.1 * math.cos(i * math.pi / 60), 1.1 * math.sin(i * math.pi / 60), 4.8) for i in range(121)])
    tree_points = pit + rect_vertices([-0.9, 0.9, -0.9, 0.9], 0.18) + [q for ring in crown for q in ring]
    tppu, tanchor, tproject = fit(tree_points)
    tim, td = base_image('T02', '1.8 x 1.8 complete pit | height 6.2 | crown spread 2.2')
    low, high = [tproject(q) for q in pit], [tproject(q) for q in rect_vertices([-0.9, 0.9, -0.9, 0.9], 0.18)]
    td.polygon([tuple(q) for q in high], fill='#d8dfe2', outline='#536573', width=4)
    for i, j in [(0, 3), (3, 2)]:
        td.polygon([tuple(low[i]), tuple(low[j]), tuple(high[j]), tuple(high[i])], fill='#bfc6ca', outline='#536573', width=3)
    td.line([tuple(tproject((0, 0, 0.18))), tuple(tproject((0, 0, 4.1)))], fill='#785f88', width=15)
    for ring in crown:
        td.line([tuple(tproject(q)) for q in ring], fill='#557f94', width=4)
    td.text(tuple(tproject((0, 0, 2.1))), ' visible trunk', font=font(26), fill='#785f88')
    td.text(tuple(tproject((0, 0, 6.2))), ' narrow crown envelope', font=font(24), fill='#23455d')
    mark_ground(td, tproject, pit, tanchor)
    tree_path = output('T02-geometry.png')
    tim.save(tree_path)
    txy = [tproject(q) for q in tree_points]
    tbounds = [min(q[0] for q in txy), min(q[1] for q in txy), max(q[0] for q in txy), max(q[1] for q in txy)]
    assert tbounds[0] >= MARGIN and tbounds[1] >= MARGIN and tbounds[2] <= SIZE - MARGIN and tbounds[3] <= SIZE - MARGIN
    tree_spec = {'id': 'T02', 'status': 'one-contrasting-tree-brief-and-geometry-only-not-native-art',
                 'T01': 'Keep accepted T01 unchanged; silhouette/size contrast only, no 10+ variant authorization.',
                 'identity': 'narrow upright/columnar deciduous street tree with smaller canopy, visible slim branching trunk; not conifer, not top-only crown',
                 'dimensionsCandidate': tree_dims, 'candidateOnly': True,
                 'geometryFile': tree_path.name, 'guideSizeActual': [SIZE, SIZE],
                 'uniformNativeGuidePixelsPerUnit': tppu, 'anchorPixel': tanchor,
                 'projectedGroundPitCornersABCD': [tproject(q) for q in pit],
                 'projectedPitRimCornersABCD': high,
                 'projectedTrunkBase': tproject((0, 0, 0.18)), 'projectedCanopyBottomCentre': tproject((0, 0, 3.4)),
                 'projectedTreeTop': tproject((0, 0, 6.2)), 'geometryBoundsPixels': tbounds,
                 'fitsSafetyMargin': True,
                 'note': 'Crown wire ellipsoid is an envelope only, never leaves/native tree art; visible trunk must be checked on generated PNG.',
                 'imageRolesInOrder': [tree_path.name, rel(accepted_t01), rel(original_style), rel(accepted_b01)]}
    output('prompts/T02.txt').write_text(
        'Create exactly ONE native T02 street-tree sprite, not a tree sheet. IMAGE ROLES: '
        '(1) T02-geometry.png = pit projection/height/trunk-clearance geometry ONLY, never copy wireframe or labels; '
        '(2) accepted pilot/T01-v1.png = existing tree finish and complete-pit construction ONLY; deliberately make T02 narrower with smaller crown, do not duplicate T01; '
        '(3) user original 2026-11-03-user-building-variety.png = neutral daylight thick-painted anime urban style ONLY; '
        '(4, optional) accepted B01 = qualitative light consistency ONLY. '
        'One slender upright/columnar DECIDUOUS tree, small irregular oval crown, visible fine trunk from complete pit into branching crown, '
        'not a conifer, ball-on-stick or top-only canopy. Complete low pale-stone tree pit with soil/low groundcover, all rim corners included, no surrounding ground patch. '
        'Candidate pit1.8x1.8, curb0.18, height6.2, canopy spread2.2 with lowest canopy near3.4; these are PM candidates not user measurements. '
        'Same accepted orthographic camera as B01: elevation62.5/azimuth45; pit frontage -28.486362689deg and depth+55.405984491deg, trunk vertical, not frontal view. '
        + LIGHT + ' Whole tree AND pit inside margin. Request1536-square true transparent RGBA PNG; check actual size/alpha. '
        'No text, labels, wires, roads, people, other trees, forest strip or opaque background. T01 remains unchanged; only this one contrasting T02 is authorized.\n')
    save_json('T02-spec.json', tree_spec)
    save_json('appearance-sources.json', crops)
    save_json('guides.json', {
        'status': 'reference-package-only-no-native-generation-no-integration-no-acceptance',
        'sourceConstraint': rel(constraint_path), 'projection': p, 'roadId': constraint['roadId'],
        'sourceNodeIds': constraint['sourceNodeIds'], 'segmentMap': constraint['segmentMap'],
        'frontageBasisMap': u, 'depthBasisMap': n,
        'depthSignWarning': 'depthBasisMap = -constraint.outwardPerpendicularMap = left-normal of streetTangentMap, exactly matching B01 script; using outward as +depth would flip the guide.',
        'groundEdgeAnglesScreenDeg': angles,
        'localCoordinates': 's frontage along street tangent; t depth along left-normal; z vertical up. Ground origin is footprint centre. D-C is road-facing frontage.',
        'dimensionStatus': 'Canonical PM production candidates, not measured source geometry or user hard dimensions.',
        'guideScalePolicy': 'One uniform scalar PPU per asset, fitted with all rooftop/roof-overhang features. No image stretch/shear/mirror; asset PPU values intentionally differ.',
        'acceptedB01BasisReconstructionMaxErrorPixels': max(b01_error),
        'qualitativeLighting': LIGHT,
        'buildings': records, 'tree': tree_spec})

    # Contact sheet is review-only; crop enlargement provides no new native detail.
    sheet = Image.new('RGB', (1600, 2240), '#f2f3f1')
    sd = ImageDraw.Draw(sheet)
    sd.text((30, 16), 'REV-005 REFERENCES | NOT NATIVE ASSETS', font=font(32), fill='#213b4c')
    sd.text((30, 58), 'Original-box identity crops (left) + exact shared-road geometry proxies (right)', font=font(24), fill='#425664')
    def thumb(path, region, checker=False, nearest=False):
        image = Image.open(path).convert('RGBA')
        if checker:
            backdrop = Image.new('RGBA', image.size, '#e7e9eb')
            bd = ImageDraw.Draw(backdrop)
            for y in range(0, image.height, 48):
                for x in range(0, image.width, 48):
                    if (x // 48 + y // 48) % 2:
                        bd.rectangle((x, y, x + 47, y + 47), fill='#fafafa')
            backdrop.alpha_composite(image)
            image = backdrop
        image.thumbnail((region[2] - region[0], region[3] - region[1]), Image.Resampling.NEAREST if nearest else Image.Resampling.LANCZOS)
        # Enlarge the tiny appearance crop for review ONLY, never change its saved original pixels.
        if nearest:
            factor = min((region[2] - region[0]) / image.width, (region[3] - region[1]) / image.height)
            image = image.resize((int(image.width * factor), int(image.height * factor)), Image.Resampling.NEAREST)
        sheet.paste(image.convert('RGB'), (int((region[0] + region[2] - image.width) / 2), int((region[1] + region[3] - image.height) / 2)))
    for idx, asset in enumerate(IDS):
        y = 104 + idx * 340
        sd.line((28, y, 1572, y), fill='#a3b0b8', width=2)
        sd.text((30, y + 10), asset + ' | ' + str(EXPECTED[asset]) + ' candidate', font=font(25), fill='#213b4c')
        sd.text((30, y + 46), 'Identity crop %sx%s, +8px context' % tuple(crops[asset]['appearanceSizeActual']), font=font(20), fill='#455967')
        sd.text((30, y + 73), 'WARNING: incomplete selected source; HOLD B05.' if asset == 'B05' else 'Enlarged here ONLY; saved crop is exact native pixels.', font=font(18), fill='#a64f20' if asset == 'B05' else '#455967')
        thumb(HERE / (asset + '-appearance.png'), (40, y + 105, 530, y + 325), nearest=True)
        thumb(HERE / (asset + '-geometry.png'), (560, y + 5, 1110, y + 330), checker=True)
        rec = records[idx]
        notes = [asset + ' GEOMETRY ONLY', '1536 x 1536 RGBA', 'Uniform PPU: %.3f' % rec['uniformNativeGuidePixelsPerUnit'],
                 '100px geometry margin: fits', 'Wall vertical error: 0 px', 'Roof forms differ deliberately', 'No geometry from old art']
        for line, text in enumerate(notes):
            sd.text((1150, y + 55 + line * 31), text, font=font(20), fill='#334d5d')
    y = 1470
    sd.line((28, y, 1572, y), fill='#a3b0b8', width=2)
    sd.text((30, y + 10), 'T02: one narrow tree + pit', font=font(25), fill='#213b4c')
    sd.text((1150, y + 10), 'T01 stays unchanged', font=font(21), fill='#213b4c')
    thumb(accepted_t01, (40, y + 55, 530, y + 325), checker=True)
    thumb(tree_path, (560, y + 5, 1110, y + 330), checker=True)
    sd.text((1150, y + 80), 'T01: contrast reference ONLY', font=font(19), fill='#334d5d')
    sd.text((1150, y + 120), 'T02: wire geometry, NOT ART', font=font(19), fill='#334d5d')
    sd.text((1150, y + 160), 'Visible trunk is required', font=font(20), fill='#334d5d')
    sd.text((1150, y + 200), 'One tree, not 10+ variants', font=font(20), fill='#334d5d')
    sd.line((28, 1810, 1572, 1810), fill='#a3b0b8', width=2)
    sd.text((30, 1824), 'User original: STYLE ONLY (not source roads/camera)', font=font(22), fill='#213b4c')
    sd.text((850, 1824), 'Accepted B01: LIGHT/FINISH ONLY, not building identity', font=font(22), fill='#213b4c')
    thumb(original_style, (30, 1860, 790, 2180))
    thumb(accepted_b01, (870, 1860, 1500, 2180), checker=True)
    sd.text((30, 2200), 'Use per-asset crops, never full TR-22/TR-33 regions as image-generation inputs. No final art generated.', font=font(22), fill='#455967')
    sheet_path = output('contact-sheet.png')
    sheet.save(sheet_path)

    with Image.open(accepted_b01) as b01_image:
        b01_actual = {'size': list(b01_image.size), 'mode': b01_image.mode}
        assert b01_image.size == (1254, 1254) and b01_image.mode == 'RGBA'
    sources = []
    for source in sorted(source_paths):
        assert sha(source) == source_before[rel(source)], 'Read-only source changed during preparation'
        rec = {'path': rel(source), 'sha256': source_before[rel(source)], 'unchangedDuringRun': True}
        if source.suffix.lower() == '.png':
            with Image.open(source) as image:
                rec.update(actualSize=list(image.size), mode=image.mode)
        sources.append(rec)
    save_json('source-hashes.json', {'sha256Algorithm': 'SHA-256 raw file bytes',
                                   'selectionSourceHashesVerified': True, 'sources': sources,
                                   'acceptedB01Actual': b01_actual})
    save_json('verification.json', {
        'scope': 'Generator output/crop/projection/canvas integrity only; NOT game tests, native art verification or user acceptance.',
        'expectedBuildingIds': IDS, 'actualBuildingIds': [r['id'] for r in records],
        'appearanceCropCount': len(crops), 'buildingGeometryCount': len(records), 'treeGeometryCount': 1,
        'promptCount': 5, 'guideGroundAnglesActualDeg': angles,
        'maxB01ReferenceCornerReconstructionErrorPixels': max(b01_error),
        'readOnlyInputHashesUnchanged': True, 'assets': checks,
        'treeGeometrySizeActual': [SIZE, SIZE], 'treeGeometryBoundsPixels': tbounds,
        'treeMargin100Fits': True, 'nativeImageGenerationCalled': False,
        'sourceFramingCaveatB05': 'Exact canonical box is incomplete; B05 native generation held for parent source-identity review. No re-selection or fabricated source roof.',
        'contactSheetActualSize': list(sheet.size)})
    output('README.md').write_text('''# revision-005 / references

仅供父线程目视审查与顺序原生生图；**本目录没有最终素材**。本脚本只写本目录，不动已认可 B01/T01、旧 PNG、路网、玩法或存档。

- `contact-sheet.png`：四栋来源裁图/几何代理、T02 与原 T01 对照、用户原参考及 B01 光照对照。联系表放大仅便于看，不增加细节。
- `B02/B03/B04/B05-appearance.png`：严格读取 building-selection.json 原 source/SHA/selectionBoxPixels，四边只加 8px 上下文，原像素不缩放/滤色/抠图。框与哈希见 `appearance-sources.json`。来源选框不是单栋素材已获用户验收。
- `B02/B03/B04/B05-geometry.png`：1536² RGBA **几何代理，不是原生美术**。区别为三段退台、竖向窄高楼、低翼公共馆、两层坡屋顶；墙线竖直。不同资产各用一个统一 PPU，所有屋顶/挑檐参与自动适配，几何均留至少 100px。
- `guides.json`：每栋 dimensionsCandidate、anchorPixel、原路投影轴、地面/屋顶角点、代理内可见角点、各层体块/实际 PPU/边界。anchor 是楼脚中心，不是地图摆放授权；接入按实际原生输出重新量锚点。
- `T02-geometry.png` / `T02-spec.json` / `prompts/T02.txt`：只新增一款窄冠落叶行道树+完整树池的候选。要露树干，T01 不改；线框冠形不是树美术，不代表获准十几款。
- `prompts/B02.txt` 等：每栋独立可用提示词，附件顺序 **几何第一 → 该栋来源裁图第二 → 用户原参考第三 → B01 可选仅光照**。不附完整 TR-22/TR-33 邻区；不把程序体块当最终素材。自然日光/厚涂都市动漫，真透明，一次一张。
- `source-hashes.json` / `verification.json` / `artifact-manifest.json`：原输入与输出完整性证据，不是游戏测试/原生图已几何通过。

## 运行

`python3 docs/art/2026-11-05-modular-map-kit/revision-005/references/make_references.py`

需要 Python 3.9+ / Pillow / NumPy。默认不覆盖输出；只刷新此脚本自己产物可加 `--refresh`。不调用生图、不启动服务、不跑游戏 tests/typecheck/回归。

## 几何关键点

沿 revision-003 原路 roadId 149397380-0、原节点对与 B01 脚本。正 frontage=streetTangent；正 depth=左法线，**等于 road-constraint.outwardPerpendicularMap 的负值**。若直接把 outward 用作正 depth，会翻向。原路正交投影为 62.5°/45°，屏幕长轴 -28.486362688849802°、短轴 +55.40598449120886°，不是通用 30°等距。AB 为后长边，DC 为临路长边。独立重建 B01 原 guide 地面/屋顶八角并记录误差，再生成新代理。

可见角点只针对代理体块做正交射线/凸体检查，不是对新原生 PNG 的测量。B05 5.5墙+2屋脊，7.5总高；坡面到屋脊的斜边本就不等于水平道路角度。所有尺寸/退台比例/屋檐是 PM 候选而非来源测绘。B01 原生实际1254² RGBA；本目录1536²是约束图，不承诺后端也返回1536或保证透明。

## 后续门禁

**B05 来源框存在真实问题，先 HOLD：** 严格原框 `[677,1019,759,1094]` 加 8px 后主要是局部楼脚/绿化与边界空白，未完整包含预期房屋及屋顶。保留原裁图，不擅自改 box 或借旁边房屋伪造来源。B05 7x5、5.5墙+2屋脊仍按 production-brief 做了候选约束图与提示词，但原生生图前由父线程决定如何补齐来源身份；不能声称已从此框看见完整坡屋顶。

父线程先看本目录图像，再逐张原生生成。逐张核实际尺寸、alpha、立面/屋顶/临路方向、建筑身份、树干/完整树池与接入后的观感；不得从提示词/本完整性记录推导美术已验收。低像素来源里的窗格/屋顶细节并非精确测绘，少量裁图背景不应转成最终资源内容。光照仅按 B01 观感定性，不伪造精确光向数据。
''')
    manifest = [{'path': str(path.relative_to(HERE)), 'sha256': sha(path), 'bytes': path.stat().st_size} for path in [Path(__file__).resolve()] + outputs]
    save_json('artifact-manifest.json', {'status': 'prepared-references-only', 'files': manifest,
                                         'manifestExcludesItself': True, 'listedFileCount': len(manifest)})
    print(json.dumps(rounded({'status': 'prepared-references-only', 'buildingCount': len(records),
                              'treeCount': 1, 'sourceHashChecks': 'matched selection and unchanged',
                              'B01BasisCornerMaxErrorPixels': max(b01_error), 'angles': angles,
                              'buildingChecks': checks, 'treeBounds': tbounds,
                              'outputDirectory': str(HERE), 'outputFiles': len(outputs)}), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
