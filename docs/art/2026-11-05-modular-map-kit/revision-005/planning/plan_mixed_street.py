#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deterministic geometry-only planner. Writes only beside this script.
Run: python3 docs/art/2026-11-05-modular-map-kit/revision-005/planning/plan_mixed_street.py
No engine, browser, network, image generation, gameplay or test-suite access.
Geometry previews require Pillow; JSON planning uses Python stdlib only.
"""
from __future__ import annotations
import copy
import hashlib
import html
import itertools
import json
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent
KIT = OUT.parent.parent
ROOT = KIT.parents[2]
MID = [-1588.072, 60.45]
U = [0.23417355683909316, -0.9721948082958105]
N = [0.9721948082958105, 0.23417355683909316]
LOCKED_B01 = [-1596.5787045725883, 58.400981377657935]
SAFETY = 2.0
EPS = 1e-8


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return str(path.relative_to(ROOT))


def point(t, n):
    return [MID[i] + t * U[i] + n * N[i] for i in (0, 1)]


def local(p):
    d = [p[i] - MID[i] for i in (0, 1)]
    return [sum(d[i] * axis[i] for i in (0, 1)) for axis in (U, N)]


def rectangle(box):
    t0, t1, n0, n1 = box
    return [point(t0, n0), point(t1, n0), point(t1, n1), point(t0, n1)]


def sub(a, b):
    return [a[i] - b[i] for i in (0, 1)]


def dot(a, b):
    return sum(a[i] * b[i] for i in (0, 1))


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def norm(a):
    return math.hypot(*a)


def nearest_on_segment(p, a, b):
    ab = sub(b, a)
    q = max(0.0, min(1.0, dot(sub(p, a), ab) / dot(ab, ab))) if dot(ab, ab) else 0.0
    return [a[i] + q * ab[i] for i in (0, 1)]


def segment_distance(a, b, c, d):
    """Exact straight-edge distance, including crossings and collinear overlap."""
    r, s = sub(b, a), sub(d, c)
    den = cross(r, s)
    if abs(den) > 1e-12:
        ac = sub(c, a)
        t, v = cross(ac, s) / den, cross(ac, r) / den
        if -1e-12 <= t <= 1 + 1e-12 and -1e-12 <= v <= 1 + 1e-12:
            p = [a[i] + t * r[i] for i in (0, 1)]
            return 0.0, p, p
    options = []
    for p in (a, b):
        q = nearest_on_segment(p, c, d)
        options.append((norm(sub(p, q)), p, q))
    for q in (c, d):
        p = nearest_on_segment(q, a, b)
        options.append((norm(sub(p, q)), p, q))
    return min(options, key=lambda x: x[0])


def edges(poly):
    return list(zip(poly, poly[1:] + poly[:1]))


def inside(p, poly):
    hit = False
    for a, b in edges(poly):
        if norm(sub(p, nearest_on_segment(p, a, b))) < 1e-10:
            return True
        if (a[1] > p[1]) != (b[1] > p[1]):
            at = a[0] + (p[1] - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
            if p[0] < at:
                hit = not hit
    return hit


def polygon_segment_distance(poly, a, b):
    if inside(a, poly) or inside(b, poly):
        p = a if inside(a, poly) else b
        return 0.0, p, p, None
    found = [(segment_distance(c, d, a, b), i) for i, (c, d) in enumerate(edges(poly))]
    best, edge = min(found, key=lambda x: x[0][0])
    return (*best, edge)


def polygon_distance(p, q):
    if inside(p[0], q) or inside(q[0], p):
        return 0.0, p[0], q[0], None, None
    choices = [(*segment_distance(a, b, c, d), i, j)
               for i, (a, b) in enumerate(edges(p)) for j, (c, d) in enumerate(edges(q))]
    return min(choices, key=lambda x: x[0])


def road_clearances(poly, roads, safety=SAFETY):
    records = []
    for road in roads:
        best = min(((*polygon_segment_distance(poly, a, b), i)
                    for i, (a, b) in enumerate(zip(road['nodes'], road['nodes'][1:]))), key=lambda x: x[0])
        distance, p, q, edge, seg = best
        carriageway = distance - road['width'] / 2
        remaining = carriageway - safety
        records.append({
            'roadId': road['id'], 'roadHalfWidth': road['width'] / 2,
            'sidewalkSafetyMargin': safety, 'centerlineDistance': distance,
            'carriagewayEdgeClearance': carriageway,
            'clearanceBeyondHalfWidthAndSafety': 0.0 if abs(remaining) < EPS else remaining,
            'footprintEdgeIndex': edge, 'roadSegmentIndex': seg,
            'roadSegmentNodeIds': road['sourceNodeIds'][seg:seg + 2],
            'witnessFootprintMap': p, 'witnessRoadCenterlineMap': q,
        })
    return records


def summarize(buildings, roads):
    per_road = [dict(buildingId=b['id'], **r) for b in buildings
                for r in road_clearances(b['footprintPolygonMap'], roads)]
    pairs = []
    for b, c in itertools.combinations(buildings, 2):
        dist, p, q, edge_b, edge_c = polygon_distance(b['footprintPolygonMap'], c['footprintPolygonMap'])
        pairs.append({'buildingIds': [b['id'], c['id']], 'footprintEdgeClearance': dist,
                      'edgeIndices': [edge_b, edge_c], 'witnessMap': [p, q]})
    return {
        'method': 'Minimum Euclidean distance over every polygon edge and every original road polyline segment, with intersection/containment checks; no center-point shortcut.',
        'units': 'source map units, treated as nominal metres by the PM brief; not surveyed/calibrated native sprite geometry',
        'roadEnvelope': 'Union of original centerline segments buffered by each road width/2, with round caps/joints. Safety clearance subtracts an additional 2.0.',
        'candidateFootprintOnly': True, 'nativeOpaqueFootprintsMeasured': False,
        'minimumRoadCenterlineDistance': min(x['centerlineDistance'] for x in per_road),
        'minimumRoadCarriagewayEdgeClearance': min(x['carriagewayEdgeClearance'] for x in per_road),
        'minimumClearanceBeyondRoadHalfWidthAndSafety': min(x['clearanceBeyondHalfWidthAndSafety'] for x in per_road),
        'minimumInterBuildingFootprintClearance': min(x['footprintEdgeClearance'] for x in pairs),
        'perBuildingPerRoad': per_road, 'allBuildingPairs': pairs,
    }


def sort_hint(anchor, projection, polygon=None):
    origin = projection['originMap']
    def depth(p):
        return sum((p[i] - origin[i]) * projection[['axisX', 'axisY'][i]][1] for i in (0, 1))
    return {'strategy': 'ground-contact-depth-candidate-not-runtime-occlusion-proof',
            'sortMap': anchor, 'projectedGroundDepth': depth(anchor),
            'footprintProjectedDepthRange': [min(map(depth, polygon)), max(map(depth, polygon))] if polygon else None,
            'layer': 'world-depth', 'nativeSpriteMustUseMeasuredGroundContact': True}


def make_buildings(brief, selections, projection, setbacks):
    result = []
    for candidate in brief['buildings']:
        bid = candidate['id']
        f, d, h = (candidate[k] for k in ('frontage', 'depth', 'height'))
        t = candidate['tangentOffsetCandidate']
        setback = setbacks.get(bid, 2.0)
        anchor = copy.deepcopy(LOCKED_B01) if bid == 'B01' else point(t, -(4 + setback + d / 2))
        actual_t, actual_n = local(anchor)
        box = [actual_t - f / 2, actual_t + f / 2, actual_n - d / 2, actual_n + d / 2]
        polygon = rectangle(box)
        result.append({
            'id': bid, 'persistentId': 'mixed-building-' + bid, 'sourceSelectionId': bid,
            'sourceSelection': copy.deepcopy(selections[bid]),
            'assetKey': 'B01-road-aligned-native-v1' if bid == 'B01' else bid + '-v1',
            'nativeStatus': 'accepted-existing-do-not-redesign' if bid == 'B01' else 'planned-native-pending-inspection',
            'identity': candidate.get('identity', selections[bid]['title']),
            'anchorMap': anchor, 'anchorLocked': bid == 'B01',
            'footprintPolygonMap': polygon, 'footprintVertexConvention': 'rear-left, rear-right, front-right, front-left; unclosed ring',
            'footprintLocalTN': box,
            'frontageTangent': copy.deepcopy(U), 'entryFacingNormal': copy.deepcopy(N),
            'entryAnchorMap': point(actual_t, actual_n + d / 2),
            'dimensionsCandidate': {'frontage': f, 'depth': d, 'height': h,
                                    'status': 'PM-production-candidate-not-source-measurement-or-native-sprite-footprint'},
            'tangentOffsetCandidate': candidate['tangentOffsetCandidate'], 'tangentOffsetApplied': actual_t,
            'setbackFromRoadEdge': setback, 'roadId': '149397380-0', 'roadSide': 'n-negative',
            'entrySurfaceIds': [], 'sortingHint': sort_hint(anchor, projection, polygon),
        })
    return result


def in_box(t, n, box):
    return box[0] < t < box[1] and box[2] < n < box[3]


def make_surfaces(buildings):
    """Partition each explicit planning domain. No overlaps, gaps or paving under buildings."""
    domains = [(-33.0, 24.0, -25.0, -4.0), (-28.0, 24.0, 4.0, 12.0)]
    specs = []
    def add(sid, mat, box, purpose):
        specs.append({'name': sid, 'materialId': mat, 'box': box, 'purpose': purpose})
    # First applicable specification wins; entry aprons are walkable sidewalk accents.
    for b in buildings:
        t0, t1, _, front = b['footprintLocalTN']
        width = {'B01': 6.0, 'B02': 8.0, 'B03': 5.0, 'B04': 10.0, 'B05': 4.0}[b['id']]
        t = b['tangentOffsetApplied']
        add(b['id'] + '-entry-patio', 'S01-paving', [t - width / 2, t + width / 2, front, -4.0],
            b['id'] + ' paved doorway connection / patio; flush, continuously walkable sidewalk, no invented driveway')
    add('sidewalk-near', 'S01-paving', [-33, 24, -6, -4], 'Continuous 2m nominal near-side walk')
    add('sidewalk-far', 'S01-paving', [-28, 24, 4, 6.2], 'Far-side sidewalk, not a second urban block')
    add('exhibition-shared-passage', 'S01-paving', [-18, -16, -19, -6], '2m pedestrian connection to rear shared garden; not a road')
    add('residential-shared-passage', 'S01-paving', [4, 6, -19, -6], '2m pedestrian connection beside shop and house; not a road')
    add('rear-shared-walk', 'S01-paving', [-31, 23, -19, -17], 'Shared pedestrian promenade linking garden and exhibition terrace')
    b2 = next(b for b in buildings if b['id'] == 'B02')
    add('office-rear-terrace', 'S01-paving', [-16, -6, -17, b2['footprintLocalTN'][2]], 'Compact office courtyard, not blank rear parcel')
    add('exhibition-rear-border', 'G02-planting', [-30, -18, -17, -16.5], 'Low planting border behind low pavilion')
    add('shared-pocket-garden', 'G01-lawn', [-4, 13, -17, -11.5], 'Designed pocket lawn with an informal three-tree T02 group')
    add('tower-rain-garden', 'G02-planting', [15, 22, -17, -13], 'Permeable rain-garden behind narrow mid-rise')
    add('rear-informal-grove', 'G03-meadow', [-33, 24, -25, -19], 'Natural T02 grove in continuous meadow/soil, explicitly no square tree pits')
    add('opposite-planting-strip', 'G02-planting', [-28, 24, 6.2, 12], 'Intentional one-strip landscape with accepted single T01 tree pits, not a second block')
    add('near-interstitial-planting', 'G02-planting', domains[0], 'Deliberate low shrubs, boundary planting and small residual garden strips')
    result, coverage = [], []
    for index, domain in enumerate(domains):
        tx = sorted({domain[0], domain[1]} | {max(domain[0], min(domain[1], x)) for b in buildings for x in b['footprintLocalTN'][:2]} |
                    {max(domain[0], min(domain[1], x)) for s in specs for x in s['box'][:2]})
        ny = sorted({domain[2], domain[3]} | {max(domain[2], min(domain[3], x)) for b in buildings for x in b['footprintLocalTN'][2:]} |
                    {max(domain[2], min(domain[3], x)) for s in specs for x in s['box'][2:]})
        # Avoid tiny roundoff slivers from exact locked B01 local coordinates.
        def dedupe(values):
            values = sorted(values)
            return [v for i, v in enumerate(values) if i == 0 or abs(v - values[i - 1]) > EPS]
        tx, ny = dedupe(tx), dedupe(ny)
        bands = []
        built_area = total_area = 0.0
        for lo_n, hi_n in zip(ny, ny[1:]):
            row = []
            for lo_t, hi_t in zip(tx, tx[1:]):
                t, n = (lo_t + hi_t) / 2, (lo_n + hi_n) / 2
                area = (hi_t - lo_t) * (hi_n - lo_n)
                total_area += area
                if any(in_box(t, n, b['footprintLocalTN']) for b in buildings):
                    built_area += area
                    choice = None
                else:
                    choice = next((s for s in specs if in_box(t, n, s['box'])), None)
                    if choice is None:
                        raise ValueError('Unplanned domain cell: ' + repr([lo_t, hi_t, lo_n, hi_n]))
                if row and choice is not None and row[-1][0] == choice['name']:
                    row[-1][1][1] = hi_t
                elif choice:
                    row.append([choice['name'], [lo_t, hi_t, lo_n, hi_n]])
                else:
                    row.append([None, [lo_t, hi_t, lo_n, hi_n]])
            bands.extend(x for x in row if x[0] is not None)
        # Merge vertically adjacent equal-width strips to keep usable polygons compact.
        merged = []
        for name, box in bands:
            earlier = next((x for x in reversed(merged) if x[0] == name and
                            abs(x[1][0] - box[0]) < EPS and abs(x[1][1] - box[1]) < EPS and abs(x[1][3] - box[2]) < EPS), None)
            if earlier:
                earlier[1][3] = box[3]
            else:
                merged.append([name, box[:]])
        for name, box in merged:
            spec = next(s for s in specs if s['name'] == name)
            serial = 1 + sum(x['groupId'] == name for x in result)
            result.append({'id': name + '-' + str(serial).zfill(2), 'groupId': name,
                           'materialId': spec['materialId'], 'polygonMap': rectangle(box),
                           'localTNBounds': box, 'areaCandidate': (box[1] - box[0]) * (box[3] - box[2]),
                           'purpose': spec['purpose'], 'renderLayer': 'ground-before-roads-and-fixtures'})
        surface_area = sum(x['areaCandidate'] for x in result if
                           domain[2] - EPS <= x['localTNBounds'][2] and x['localTNBounds'][3] <= domain[3] + EPS)
        coverage.append({'id': ['complete-one-sided-mixed-frontage', 'intentional-opposite-planting-strip'][index],
                         'polygonMap': rectangle(domain), 'localTNBounds': domain, 'domainAreaCandidate': total_area,
                         'buildingFootprintAreaCandidate': built_area, 'groundSurfaceAreaCandidate': surface_area,
                         'unassignedAreaCandidate': 0.0 if abs(total_area - built_area - surface_area) < EPS else max(0.0, total_area - built_area - surface_area),
                         'secondUrbanBlockClaimed': False})
    for b in buildings:
        b['entrySurfaceIds'] = [s['id'] for s in result if s['groupId'] == b['id'] + '-entry-patio']
    return result, coverage


def make_fixtures(projection, roads, buildings):
    fixtures, arrangements = [], []
    def add(pid, asset, t, n, facing, arrangement, radius, status, ground_treatment):
        anchor = point(t, n)
        polygon = [point(t + radius * math.cos(i * math.tau / 24), n + radius * math.sin(i * math.tau / 24)) for i in range(24)]
        fixtures.append({'persistentId': pid, 'assetKey': asset, 'anchorMap': anchor, 'localTN': [t, n],
                         'facing': facing, 'arrangementId': arrangement, 'nativeStatus': status,
                         'groundTreatment': ground_treatment, 'groundEnvelopeRadiusCandidate': radius,
                         'groundEnvelopePolygonMapCandidate': polygon,
                         'roadClearanceCarriagewayMinimumCandidate': min(r['carriagewayEdgeClearance'] for r in road_clearances(polygon, roads, 0)),
                         'buildingClearanceMinimumCandidate': min(polygon_distance(polygon, b['footprintPolygonMap'])[0] for b in buildings),
                         'sortingHint': sort_hint(anchor, projection)})
    lamp_members = []
    for side, sign, offsets in [('near', -1, [-27.0, -8.0, 11.0]), ('far', 1, [-21.0, 0.0, 20.0])]:
        for i, t in enumerate(offsets, 1):
            pid = 'mixed-lamp-' + side + '-' + str(i).zfill(2)
            arm = [(-sign) * v for v in N]
            add(pid, 'L01-road-' + side + '-v1', t, sign * 5.2,
                {'roadSide': 'n-negative' if sign < 0 else 'n-positive', 'armDirectionMap': arm,
                 'poleAxis': [0, 0, 1], 'opticalDirection': [0, 0, -1], 'towardRoad': True,
                 'requiredNativeVariant': side, 'spriteMirrorOrRotationAllowed': False},
                'two-sided-inward-lamps', 0.16, 'planned-native-orientation-variant', 'sidewalk pole; no tree pit')
            lamp_members.append(pid)
    arrangements.append({'id': 'two-sided-inward-lamps', 'type': 'street-fixture-alternating-stagger', 'members': lamp_members})
    tree_plans = [
        ('street-pit-singles', 'single-street-tree-pits', 'T01-v1', [(-20, 8.6), (0, 8.6), (18, 8.6)], 1.35,
         'accepted-existing', 'individual integrated tree-pit asset on deliberate urban planting strip'),
        ('pocket-garden-trio', 'informal-three-tree-group', 'T02-v1', [(-0.8, -14.7), (2.1, -15.3), (9.0, -14.6)], 1.1,
         'planned-native-pending-inspection', 'continuous lawn / planting soil; no square tree pit'),
        ('rear-natural-grove', 'irregular-small-grove', 'T02-v1', [(-28, -22.4), (-23.7, -23.4), (-15.5, -21.8), (-10.8, -23.1), (17.8, -22.0)], 1.35,
         'planned-native-pending-inspection', 'continuous meadow / natural soil; no square tree pit'),
    ]
    for aid, kind, asset, positions, radius, status, treatment in tree_plans:
        members = []
        for i, (t, n) in enumerate(positions, 1):
            pid = 'mixed-tree-' + aid + '-' + str(i).zfill(2)
            add(pid, asset, t, n, {'orientation': 'fixed-accepted-camera-no-sprite-transform',
                                 'roadFacingNotApplicable': True}, aid, radius, status, treatment)
            members.append(pid)
        arrangements.append({'id': aid, 'type': kind, 'members': members,
                             'squareTreePits': kind == 'single-street-tree-pits'})
    return fixtures, arrangements


def camera_suggestions(buildings, projection):
    points = []
    for b in buildings:
        for p in b['footprintPolygonMap']:
            for height in (0, b['dimensionsCandidate']['height']):
                points.append([sum((p[i] - projection['originMap'][i]) * projection[['axisX', 'axisY'][i]][j] for i in (0, 1)) + height * projection['axisZ'][j] for j in (0, 1)])
    bx = [min(p[0] for p in points), max(p[0] for p in points)]
    by = [min(p[1] for p in points), max(p[1] for p in points)]
    screen_center = [(bx[0] + bx[1]) / 2, (by[0] + by[1]) / 2]
    a, b = projection['axisX'], projection['axisY']
    det = a[0] * b[1] - b[0] * a[1]
    focus = [projection['originMap'][0] + (screen_center[0] * b[1] - screen_center[1] * b[0]) / det,
             projection['originMap'][1] + (a[0] * screen_center[1] - a[1] * screen_center[0]) / det]
    return [{'id': 'all-five-frontage', 'focusMap': focus, 'viewWidthUnits': math.ceil((bx[1] - bx[0]) * 1.22),
             'referenceWidth': 720, 'referenceHeight': 1280, 'screenOffset': [0, 0],
             'candidateProjectedBuildingBounds': {'x': bx, 'y': by},
             'note': 'Framing suggestion includes nominal building heights. Native silhouettes/occlusion still require parent visual inspection; no runtime proof.'},
            {'id': 'accepted-B01-detail', 'focusMap': copy.deepcopy(LOCKED_B01), 'viewWidthUnits': 15,
             'referenceWidth': 720, 'referenceHeight': 1280, 'screenOffset': [0, 0],
             'note': 'Preserve accepted revision-004 close-up as a separate detail, not the all-five-block framing.'}]


def preview(layout):
    """SVG and PNG share drawing commands; never substitute a native image render."""
    from PIL import Image, ImageDraw, ImageFont
    width, height = 1440, 1040
    image = Image.new('RGB', (width, height), '#f5f4ef')
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 15)
        small = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 12)
        title = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 22)
    except OSError:
        font = small = title = ImageFont.load_default()
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<rect width="100%" height="100%" fill="#f5f4ef"/>']
    def text(x, y, value, fill='#26333b', size=15):
        draw.text((x, y), value, fill=fill, font=title if size > 18 else small if size < 14 else font)
        svg.append(f'<text x="{x:.2f}" y="{y + size:.2f}" font-family="Arial,sans-serif" font-size="{size}" fill="{fill}">{html.escape(str(value))}</text>')
    def polygon(points, fill, stroke=None, line_width=1):
        draw.polygon(points, fill=fill, outline=stroke)
        coords = ' '.join(f'{x:.2f},{y:.2f}' for x, y in points)
        svg.append(f'<polygon points="{coords}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="{line_width}"/>')
    def line(points, fill, line_width=1):
        draw.line(points, fill=fill, width=max(1, round(line_width)), joint='curve')
        coords = ' '.join(f'{x:.2f},{y:.2f}' for x, y in points)
        svg.append(f'<polyline points="{coords}" fill="none" stroke="{fill}" stroke-width="{line_width:.2f}" stroke-linejoin="round" stroke-linecap="round"/>')
    def circle(x, y, r, fill, stroke=None):
        draw.ellipse([x-r, y-r, x+r, y+r], fill=fill, outline=stroke)
        svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{fill}" stroke="{stroke or "none"}"/>')
    # Detail panel: tangent right, positive road normal up. Preserve true dimensions.
    scale, tx0, n_top = 14.0, -48.0, 23.0
    ox, oy = 40.0, 100.0
    def xy(p):
        t, n = local(p)
        return (ox + (t - tx0) * scale, oy + (n_top - n) * scale)
    text(34, 20, 'REVISION 005 / GEOMETRY ONLY - not native sprites, not visual acceptance', size=22)
    text(34, 55, 'Original road nodes / widths / directions retained. Detail cropped; full source geometry in inset + JSON.')
    # Raster and SVG clip are both provided by final panel masking.
    for s in layout['groundSurfaces']:
        colors = {'S01-paving': '#ded9cb', 'G01-lawn': '#a6bd8a', 'G02-planting': '#8da17d', 'G03-meadow': '#b6bf92'}
        polygon([xy(p) for p in s['polygonMap']], colors[s['materialId']], '#75816c')
    for r in layout['roads']:
        line([xy(p) for p in r['nodes']], '#d0ccb9', (r['width'] + 4) * scale)
        line([xy(p) for p in r['nodes']], '#687078', r['width'] * scale)
        line([xy(p) for p in r['nodes']], '#aeb5b8', 1)
    colors = {'B01': '#bd8257', 'B02': '#709db6', 'B03': '#6584aa', 'B04': '#bc9b74', 'B05': '#b07d85'}
    for b in layout['buildings']:
        polygon([xy(p) for p in b['footprintPolygonMap']], colors[b['id']], '#243d4c', 2)
        x, y = xy(b['anchorMap'])
        text(x-15, y-16, b['id'])
        text(x-22, y+3, str(b['dimensionsCandidate']['height']) + 'm H', size=12)
        front = xy(b['entryAnchorMap'])
        line([front, (front[0], front[1]-19)], '#fff4cc', 3)
    for f in layout['fixtures']:
        x, y = xy(f['anchorMap'])
        if f['assetKey'].startswith('L01'):
            arm = f['facing']['armDirectionMap']
            tip = xy([f['anchorMap'][i] + arm[i]*1.7 for i in (0, 1)])
            line([(x,y), tip], '#e7ad34', 4)
            polygon([tip, (tip[0]-4, tip[1]+(7 if tip[1]<y else -7)), (tip[0]+4, tip[1]+(7 if tip[1]<y else -7))], '#e7ad34')
            circle(x, y, 3, '#182736')
        else:
            if f['assetKey'] == 'T01-v1':
                radius = f['groundEnvelopeRadiusCandidate']
                t, n = f['localTN']
                polygon([xy(p) for p in rectangle([t-radius,t+radius,n-radius,n+radius])], '#6d7969', '#435b43')
            circle(x, y, f['groundEnvelopeRadiusCandidate']*scale, '#476b49', '#284931')
    # Road-node witnesses and important sample labels.
    for nid, p in zip(layout['referenceFrame']['sourceNodeIds'], layout['referenceFrame']['segmentMap']):
        x,y = xy(p)
        circle(x,y,4,'#e9dc8e')
        text(x-75,y+13,nid,size=12)
    # Cover out-of-detail source paths; source inset below preserves all nodes.
    for pts in [[(0,0),(1440,0),(1440,100),(0,100)], [(0,806),(1440,806),(1440,1040),(0,1040)],
                [(0,80),(40,80),(40,806),(0,806)], [(1190,80),(1440,80),(1440,806),(1190,806)]]:
        polygon(pts, '#f5f4ef')
    text(34, 20, 'REVISION 005 / GEOMETRY ONLY - not native sprites, not visual acceptance', size=22)
    text(34, 55, 'Original road nodes / widths / directions retained. Detail cropped; full source geometry in inset + JSON.')
    # Inset shows every node, including long main-road tails and two original branches.
    inset_x, inset_y, inset_w, inset_h = 1210, 140, 200, 540
    all_nodes = [local(p) for r in layout['roads'] for p in r['nodes']]
    tmin,tmax = min(p[0] for p in all_nodes),max(p[0] for p in all_nodes)
    nmin,nmax = min(p[1] for p in all_nodes),max(p[1] for p in all_nodes)
    s = min(inset_w/(nmax-nmin),inset_h/(tmax-tmin))
    def inset(p):
        t,n=local(p)
        return (inset_x+(n-nmin)*s, inset_y+(t-tmin)*s)
    text(1210,100,'ALL ORIGINAL NODES',size=12)
    for r in layout['roads']:
        line([inset(p) for p in r['nodes']], '#67737c', max(1,r['width']*s))
        for p in r['nodes']:
            circle(*inset(p),2,'#bd7b45')
    rectangle_points = [inset(p) for p in rectangle([-33,24,-25,12])]
    polygon(rectangle_points,'#eadfbc','#ab7848')
    # Repaint source roads above the local sample rectangle in inset.
    for r in layout['roads']:
        line([inset(p) for p in r['nodes']], '#67737c', max(1,r['width']*s))
    text(1210,700,'Amber = sample area',size=12)
    text(1210,721,f"{len(layout['roads'])} roads / {sum(len(r['nodes']) for r in layout['roads'])} nodes",size=12)
    text(1210,742,'No invented roads',size=12)
    text(1210,763,'No bridge source',size=12)
    text(40,815,'Tangent +u ->     +n is above road. Buildings face +n. Gold lamp arms point inward from BOTH sides.',size=15)
    text(40,844,'B04 low pavilion | B02 terraced office | B01 accepted shop | B05 pitched-roof house | B03 narrow mid-rise',size=15)
    text(40,874,'Ground: warm grey = entries / walks; light green = shared lawn; olive = planting; rear meadow = natural grove.',size=15)
    text(40,904,'Trees: T01 individual street pits + T02 informal trio + T02 irregular grove. Natural trees have NO square pits.',size=15)
    m=layout['clearanceAnalysis']
    text(40,938,f"Candidate min road edge clearance {m['minimumRoadCarriagewayEdgeClearance']:.3f}; extra after 2m safety {m['minimumClearanceBeyondRoadHalfWidthAndSafety']:.3f}; between buildings {m['minimumInterBuildingFootprintClearance']:.3f}.")
    text(40,967,'All dimensions nominal PM candidates. Native footprints, silhouettes, scale and occlusion remain unmeasured.',size=15)
    text(40,997,'Geometry preview only. No game tests / typecheck / regression / browser / deployment performed.',size=15)
    svg.append('</svg>')
    (OUT/'mixed-street-geometry.svg').write_text('\n'.join(svg),encoding='utf-8')
    image.save(OUT/'mixed-street-geometry.png')


def main():
    if OUT.name != 'planning' or OUT.parent.name != 'revision-005':
        raise ValueError('Planner may write only revision-005/planning')
    paths = {
        'productionBrief': OUT.parent/'production-brief.json',
        'roadConstraint': KIT/'revision-003/road-constraint.json',
        'sceneLayout': KIT/'revision-004/viewer/assets/scene-layout.json',
        'tiledStreet': KIT/'revision-004/integration/street.tmj',
        'bridgeMeta': KIT/'revision-004/integration/bridge-meta.json',
        'buildingSelection': KIT/'building-selection.json',
    }
    brief, constraint, scene, meta = (load(paths[k]) for k in ['productionBrief','roadConstraint','sceneLayout','bridgeMeta'])
    selections = {x['id']: x for x in load(paths['buildingSelection'])}
    roads, projection = copy.deepcopy(scene['roads']), copy.deepcopy(scene['projection'])
    if projection != constraint['projection'] or projection != meta['projection']:
        raise ValueError('Projection conflict in shared source documents')
    main_road = next(r for r in roads if r['id'] == brief['roadId'])
    i = main_road['sourceNodeIds'].index('1623821577')
    if main_road['sourceNodeIds'][i:i+2] != ['1623821577','1623821431'] or main_road['nodes'][i:i+2] != constraint['segmentMap']:
        raise ValueError('Source reference segment changed')
    initial = make_buildings(brief,selections,projection,{})
    initial_analysis = summarize(initial,roads)
    # All original PM tangent candidates fit. Vary NEW setbacks for deliberate patios;
    # do not move accepted B01 or invent another street / rear-facing building row.
    buildings = make_buildings(brief,selections,projection,{'B02':2.75,'B03':3.0,'B04':3.5,'B05':2.5})
    analysis = summarize(buildings,roads)
    if analysis['minimumClearanceBeyondRoadHalfWidthAndSafety'] < -EPS or analysis['minimumInterBuildingFootprintClearance'] < 2-EPS:
        raise ValueError('Candidate block violates road safety or building gap requirement')
    surfaces, coverage = make_surfaces(buildings)
    fixtures, arrangements = make_fixtures(projection,roads,buildings)
    if min(f['roadClearanceCarriagewayMinimumCandidate'] for f in fixtures) <= 0:
        raise ValueError('Fixture candidate obstructs original road envelope')
    if min(f['buildingClearanceMinimumCandidate'] for f in fixtures) <= EPS:
        raise ValueError('Fixture candidate collides with building footprint')
    if any(c['unassignedAreaCandidate'] > EPS for c in coverage):
        raise ValueError('Unplanned blank area remains')
    layout = {
        'schemaVersion':1, 'id':'revision-005-original-road-mixed-street',
        'status':'geometry-planning-candidate-native-integration-pending',
        'scope':'Complete one-sided five-type art block plus intentional opposite planting strip, not a second urban block. No bridge source in this local sample.',
        'source':copy.deepcopy(scene['source']), 'projection':projection, 'roads':roads,
        'sourceSceneLayoutSHA256':sha(paths['sceneLayout']),
        'sourceTiledStreetSHA256':sha(paths['tiledStreet']),
        'sourceEvidence':{k:{'path':rel(p),'sha256':sha(p)} for k,p in paths.items()},
        'sourceIntegrity':{'allRoadsCopiedUnchanged':roads==scene['roads'],
                           'projectionCopiedUnchanged':projection==scene['projection'],
                           'originalCitySHAIsReportedBySceneNotResurveyed':True,
                           'roadCount':len(roads),'roadNodeCount':sum(len(r['nodes']) for r in roads),
                           'mainRoadNodeCount':len(main_road['nodes']), 'originalRoadDirectionsUnchanged':True,
                           'sourceGeometrySurveyCalibrationClaimed':False},
        'referenceFrame':{'roadId':main_road['id'],'sourceNodeIds':['1623821577','1623821431'],
                          'segmentMap':copy.deepcopy(constraint['segmentMap']), 'roadReferenceMap':MID,
                          'frontageTangent':U,'positiveRoadNormal':N,'buildingSide':'n-negative',
                          'anchorFormula':'roadReference + tangentOffset*u - (roadHalfWidth + setback + depth/2)*n',
                          'lockedB01AnchorMap':LOCKED_B01,'sidewalkSafetyMargin':SAFETY},
        'placementDecision':{'initialPMCandidatesFitWithoutRoadEdits':initial_analysis['minimumClearanceBeyondRoadHalfWidthAndSafety']>=-EPS,
                             'initialMinimumRoadEdgeClearance':initial_analysis['minimumRoadCarriagewayEdgeClearance'],
                             'initialMinimumInterBuildingClearance':initial_analysis['minimumInterBuildingFootprintClearance'],
                             'allTangentOffsetsPreserved':True,
                             'newBuildingSetbackAdjustments':{'B02':[2,2.75],'B03':[2,3.0],'B04':[2,3.5],'B05':[2,2.5]},
                             'reason':'Initial edge/segment analysis finds all five fit. Only new-building setbacks increase modestly for office patio, public forecourt, house apron and tower entry; accepted B01 stays exactly locked.'},
        'buildings':buildings, 'groundSurfaces':surfaces, 'plannedDomains':coverage,
        'materialCatalog':[
            {'id':'S01-paving','status':'existing-paving-family-reference; exact texture integration owned by parent'},
            {'id':'G01-lawn','status':'planned-ground-material; not a newly generated native asset'},
            {'id':'G02-planting','status':'planned-ground-material; low planting / permeable soil'},
            {'id':'G03-meadow','status':'planned-ground-material; natural continuous soil, no tree-pit grid'}],
        'fixtures':fixtures,'arrangements':arrangements,'clearanceAnalysis':analysis,
        'cameraSuggestions':camera_suggestions(buildings,projection),
        'integrationNotes':[
            'Polygons are unclosed map-space rings; source roads/projection/source metadata are copied, never clipped or edited in the JSON.',
            'Ground surfaces exactly partition the explicit planning domains except building footprints. Outside these domains is outside this local sample, not an unfinished promised second block.',
            'Buildings are five different source selections and candidate massing identities; actual native distinctness is still parent-owned inspection.',
            'Near lamps at n=-5.2 extend +n; far lamps at n=+5.2 extend -n. Use actual native variants, never rotate/mirror an accepted PNG.',
            'Fixture envelope radii are PM planning candidates, not native sprite measurements. T01 includes its urban pit; T02 must be standalone/no square pit for informal lawn and natural grove.',
            '2m road safety is consumed exactly by locked B01. Any future native overhang requires parent to inspect/measure, not claim calibrated clearance from this planner.',
            'Camera uses nominal candidate heights only. Five clear ground footprints do not prove final native silhouette occlusion or full-county readiness.',
            'Only planner execution/data geometry calculation performed; no game suite/typecheck/regression/browser/server/save/deployment/commit/push.'
        ],
    }
    out_path=OUT/'mixed-street-layout.json'
    out_path.write_text(json.dumps(layout,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    preview(layout)
    summary={
        'outputs':[str(out_path),str(OUT/'mixed-street-geometry.svg'),str(OUT/'mixed-street-geometry.png')],
        'buildings':len(buildings),'groundSurfaces':len(surfaces),'fixtures':len(fixtures),
        'roadsPreserved':len(roads),'roadNodesPreserved':sum(len(r['nodes']) for r in roads),
        'B01AnchorExactlyLocked':buildings[0]['anchorMap']==LOCKED_B01,
        'minRoadEdgeClearance':analysis['minimumRoadCarriagewayEdgeClearance'],
        'minBeyondRoadHalfwidthAnd2mSafety':analysis['minimumClearanceBeyondRoadHalfWidthAndSafety'],
        'minBuildingEdgeClearance':analysis['minimumInterBuildingFootprintClearance'],
        'unassignedArea':sum(c['unassignedAreaCandidate'] for c in coverage),
        'sourceSceneSHA256':sha(paths['sceneLayout']),
    }
    by_road={r['id']:min(x['carriagewayEdgeClearance'] for x in analysis['perBuildingPerRoad'] if x['roadId']==r['id']) for r in roads}
    report = f"""# revision-005 原路混合街段几何交付

- 已实际执行当前规划脚本，仅写 revision-005/planning；未运行游戏测试/typecheck/回归/浏览器/服务器，未生图或提交。
- 保留 {len(roads)} 条原路和 {summary['roadNodesPreserved']} 个原顺序节点、全部宽度/方向/投影/source；主路 {main_road['id']} 的 {len(main_road['nodes'])} 个节点不变。
- 源 scene SHA256：`{sha(paths['sceneLayout'])}`。全部来源路径及 SHA 在 JSON 的 sourceEvidence。
- 五种楼型沿 n 负侧完整组织，入口朝 +n；B01 精确锁定 `{LOCKED_B01}`。所有原切向候选均可放入。
- 仅新楼退距调整为 B02 2.75、B03 3、B04 3.5、B05 2.5；B01 退距 2 不动。
- 建筑距原道路车行边缘最小 **{analysis['minimumRoadCarriagewayEdgeClearance']:.6f}**；扣各路半宽及 2m 安全距后余量最小 **{analysis['minimumClearanceBeyondRoadHalfWidthAndSafety']:.6f}**。
- 两楼足迹最小间隙 **{analysis['minimumInterBuildingFootprintClearance']:.6f}**。每楼×每路及全部楼对均计算实际边/段，附最近边/路段节点/见证坐标，不以中心点近似。
- 各路最小边缘净距：`{json.dumps(by_road,ensure_ascii=False)}`。
- 共 {len(surfaces)} 个地面多边形；各楼有铺装入口/小院，另有连贯人行道、公共后院步道、办公露台、口袋草坪、雨水花园、后方片林及对侧种植带。
- 两个明确规划域未分配面积合计 **{summary['unassignedArea']:.6f}**；对侧仅为有意种植带，不宣称第二完整街区。
- 共 {len(fixtures)} 个持久 fixture；6 灯仅引用 L01-road-near-v1 / L01-road-far-v1，不使用方向未通过的 L02。
- 灯位 n=±5.2，近侧挑臂 +n、远侧 -n；T01 单株树池 / T02 自然三树组 / T02 不规则片林三种组合，自然组不带方树池。
- 没有桥源，未添桥。SVG/PNG 标注仅几何，不是原生画面。
- 文件：mixed-street-layout.json、plan_mixed_street.py、mixed-street-geometry.svg、mixed-street-geometry.png。
- 限制：米数/高度/树冠包络均为 PM 候选，不是源实测或已校准原生足迹；新楼/树/灯及排序遮挡仍待主代理实图检查。B01 的 2m 安全距没有额外富余。
"""
    (OUT/'REPORT.md').write_text(report,encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
