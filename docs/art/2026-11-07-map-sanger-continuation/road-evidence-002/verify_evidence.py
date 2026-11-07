#!/usr/bin/env python3
"""Check only this standalone map evidence; no game runtime or save access."""
import hashlib
import itertools
import json
import math
from copy import deepcopy
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'AGENTS.md').is_file())
EPS = 1e-6
CHECKS = []


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check(label, result):
    assert result, label
    CHECKS.append(label)


def close(a, b):
    return math.isclose(a, b, abs_tol=EPS, rel_tol=1e-10)


def same(a, b):
    return all(close(x, y) for x, y in zip(a, b))


def cross(a, b):
    return a[0]*b[1]-a[1]*b[0]


def sub(a, b):
    return [a[0]-b[0], a[1]-b[1]]


def area(poly):
    return abs(sum(cross(a, b) for a, b in zip(poly, poly[1:]+poly[:1])))/2


def on_segment(p, a, b):
    return abs(cross(sub(b, a), sub(p, a))) < EPS and all(
        min(a[k], b[k])-EPS <= p[k] <= max(a[k], b[k])+EPS for k in (0, 1))


def intersection(a, b, c, d):
    r, s = sub(b, a), sub(d, c)
    den = cross(r, s)
    if abs(den) < EPS:
        points = []
        for p in [a, b, c, d]:
            if on_segment(p, a, b) and on_segment(p, c, d) and not any(same(p, q) for q in points):
                points.append(p)
        return points
    t, u = cross(sub(c, a), s)/den, cross(sub(c, a), r)/den
    return [[a[k]+t*r[k] for k in (0, 1)]] if -EPS <= t <= 1+EPS and -EPS <= u <= 1+EPS else []


def connected(nodes, edges, excluded=None):
    adj = {n['id']: set() for n in nodes}
    for e in edges:
        if e['id'] != excluded:
            adj[e['from']].add(e['to'])
            adj[e['to']].add(e['from'])
    seen, todo = set(), [next(iter(adj))]
    while todo:
        n = todo.pop()
        if n not in seen:
            seen.add(n)
            todo.extend(adj[n]-seen)
    return len(seen) == len(nodes)


def absolute_points(obj, key):
    return [[obj['x']+p['x'], obj['y']+p['y']] for p in obj[key]]


def layer(doc, name):
    return next(l for l in doc['layers'] if l['name'] == name)


def properties(obj):
    return {p['name']: p['value'] for p in obj.get('properties', [])}


def planning_edge_matches(obj, edge, node_by, height):
    expected_properties = {
        'from': edge['from'], 'to': edge['to'], 'corridor_id': edge['corridorId'],
        'tier': edge['tier'], 'asphalt_width_design_metres': edge['proposedAsphaltWidthMetres'],
        'length_design_metres': edge['lengthMetres'], 'traced_from_actual_art': False,
    }
    return len(obj.get('polyline', [])) == 2 and properties(obj) == expected_properties and all(
        same(p, [node_by[n][0], height-node_by[n][1]])
        for p, n in zip(absolute_points(obj, 'polyline'), [edge['from'], edge['to']]))


def offset_by_line_intersections(poly, widths, extra):
    lines = []
    for a, b, width in zip(poly, poly[1:]+poly[:1], widths):
        dx, dy = sub(b, a); length = math.hypot(dx, dy)
        normal = [-dy/length, dx/length]
        lines.append((normal, sum(normal[k]*a[k] for k in (0, 1))+width/2+extra))
    corners = []
    for (a, ac), (b, bc) in zip(lines[-1:]+lines[:-1], lines):
        determinant = cross(a, b)
        assert abs(determinant) > EPS
        corners.append([(ac*b[1]-a[1]*bc)/determinant, (a[0]*bc-ac*b[0])/determinant])
    return corners


def same_polygon(actual, expected):
    return len(actual) == len(expected) and close(area(actual), area(expected)) and all(
        any(same(p, q) for q in expected) for p in actual) and all(
        any(same(p, q) for p in actual) for q in expected)


def main():
    actual = read(HERE/'actual-graph.json')
    plan = read(HERE/'planning-graph.json')
    net = read(HERE/'planning-land-ledger.json')
    native = HERE.parent/'builtin-capacity-002/native.png'
    check('native returned bytes SHA unchanged', sha(native) == actual['nativeSHA256'])
    with Image.open(native) as image:
        check('native RGB 1672x941', image.mode == 'RGB' and list(image.size) == actual['nativeSize'] == [1672, 941])
    check('generated files match author manifest', all(sha(HERE/p) == digest for p, digest in read(HERE/'generated-files.json').items()))
    check('all recorded inputs still match', all(sha(ROOT/p) == digest for p, digest in read(HERE/'input-fingerprints.json').items()))
    protected = read(ROOT/'docs/team/handoffs/2026-11-07-map-codex-sanger/map-protected-snapshot.json')['files']
    check('91 protected sources unchanged', len(protected) == 91 and all(sha(ROOT/p) == v['sha256'] for p, v in protected.items()))

    nodes = {n['id']: n['pixel'] for n in actual['nodes']}
    edges = {e['id']: e for e in actual['edges']}
    check('unique node ids and coordinates', len(nodes) == len(actual['nodes']) == len({tuple(p) for p in nodes.values()}) == 31)
    check('unique edge ids and undirected pairs', len(edges) == len(actual['edges']) == len({tuple(sorted((e['from'], e['to']))) for e in edges.values()}) == 38)
    check('actual connected graph with eight bounded faces', connected(actual['nodes'], actual['edges']) and len(edges)-len(nodes)+1 == 8)
    segments = []
    for e in edges.values():
        check(e['id']+' shared endpoint and measured polyline', e['points'][0] == nodes[e['from']] and e['points'][-1] == nodes[e['to']] and close(e['lengthPixels'], sum(math.dist(a, b) for a, b in zip(e['points'], e['points'][1:]))))
        for i, (a, b) in enumerate(zip(e['points'], e['points'][1:])):
            check(e['id']+f' segment {i} positive', math.dist(a, b) > 0)
            segments.append((e, i, a, b))
    crossing_count = 0
    for (e, i, a, b), (f, j, c, d) in itertools.combinations(segments, 2):
        hits = intersection(a, b, c, d)
        if not hits:
            continue
        crossing_count += 1
        allowed = [p for p in [a, b] if any(same(p, q) for q in [c, d])] if e['id'] == f['id'] and abs(i-j) == 1 else [nodes[n] for n in {e['from'], e['to']}.intersection({f['from'], f['to']})] if e['id'] != f['id'] else []
        assert len(hits) == 1 and any(same(hits[0], p) for p in allowed), ('unmerged crossing or overlapping segment', e['id'], f['id'], hits)
    CHECKS.append('all segment intersections are exact merged junctions or adjacent polyline vertices')
    for key in ['mainRoute', 'alternativeRoute']:
        choice = actual[key]
        cursor, distance = choice['from'], 0
        for eid in choice['edgeIds']:
            e = edges[eid]
            assert cursor in [e['from'], e['to']], (key, eid, cursor)
            cursor = e['to'] if cursor == e['from'] else e['from']
            distance += e['lengthPixels']
        check(key+' contiguous route and exact sum', cursor == choice['to'] and close(distance, choice['length']))
    check('alternative excludes chosen internal edge', actual['excludedEdgeForAlternative'] in actual['mainRoute']['edgeIds'] and actual['excludedEdgeForAlternative'] not in actual['alternativeRoute']['edgeIds'])
    check('all 22 actual internal edge removals keep graph connected', sum(e['role'] == 'internal' for e in edges.values()) == 22 and all(connected(actual['nodes'], actual['edges'], e['id']) for e in edges.values() if e['role'] == 'internal'))

    tmj = read(HERE/'tiled/actual-eight.tmj')
    check('actual Tiled canvas has native pixel units', [tmj['width'], tmj['height'], tmj['tilewidth'], tmj['tileheight']] == [1672, 941, 1, 1] and not properties(tmj)['metre_calibrated'])
    objects = layer(tmj, 'actual-road-centrelines')['objects']
    check('all 38 actual Tiled edges round trip', len(objects) == 38 and all(absolute_points(o, 'polyline') == edges[o['name']]['points'] and properties(o)['from'] == edges[o['name']]['from'] and properties(o)['to'] == edges[o['name']]['to'] for o in objects))
    junctions = layer(tmj, 'actual-junctions-and-edge-ports')['objects']
    check('all 31 actual Tiled nodes round trip', len(junctions) == 31 and all([o['x'], o['y']] == nodes[o['name']] for o in junctions))
    image_layer = layer(tmj, 'native-art')
    check('Tiled references exact original image', sha((HERE/'tiled'/image_layer['image']).resolve()) == actual['nativeSHA256'] and [image_layer['imagewidth'], image_layer['imageheight']] == [1672, 941])

    plan_tmj = read(HERE/'tiled/whole-city-planning.tmj')
    source = read(ROOT/'docs/art/2026-11-06-city-image-map/planning/scope-recovery-v1/scope-plan.json')
    check('planning geometry and uses inherited unchanged', plan['nodes'] == source['nodes'] and plan['edges'] == source['edges'] and [b['programme'] for b in net['blocks']] == [b['programme'] for b in source['blocks']])
    check('planning all 144 edge removals independently connected', len(plan['edges']) == 144 and all(connected(plan['nodes'], plan['edges'], e['id']) for e in plan['edges']))
    node_by = {n['id']: n['designMetres'] for n in plan['nodes']}
    height = plan['targetDesignSizeMetres'][1]
    plan_edges = {e['id']: e for e in plan['edges']}
    objects = layer(plan_tmj, 'planned-full-road-network')['objects']
    check('all 144 planning Tiled names, exact vertices and properties round trip', len(objects) == 144 and {o['name'] for o in objects} == set(plan_edges) and all(planning_edge_matches(o, plan_edges[o['name']], node_by, height) for o in objects))
    altered = deepcopy(objects[0]); altered['polyline'].append({'x': 99999, 'y': 99999})
    check('planning check rejects appended third vertex', not planning_edge_matches(altered, plan_edges[altered['name']], node_by, height))
    altered = deepcopy(objects[0]); altered['properties'][0]['value'] = 'wrong-node'
    check('planning check rejects changed property', not planning_edge_matches(altered, plan_edges[altered['name']], node_by, height))
    totals = defaultdict(float)
    for b in net['blocks']:
        gross, asphalt, sidewalk = b['centrelinePolygon'], b['netAsphaltOnlyPolygon'], b['netWith2mSidewalkHypothesisPolygon']
        assert 0 < area(sidewalk) < area(asphalt) < area(gross)
        assert close(area(asphalt), b['netAsphaltOnlyMetres2']) and close(area(sidewalk), b['netWith2mSidewalkHypothesisMetres2'])
        for extra, poly in [(0, asphalt), (2, sidewalk)]:
            assert same_polygon(poly, offset_by_line_intersections(gross, b['boundaryAsphaltWidthsMetres'], extra)), ('not the exact specified offset', b['id'], extra)
            for a, c, width in zip(gross, gross[1:]+gross[:1], b['boundaryAsphaltWidthsMetres']):
                vector = sub(c, a)
                assert all(cross(vector, sub(p, a))/math.dist(a, c) >= width/2+extra-EPS for p in poly), b['id']
        totals[b['programme']] += area(asphalt)
    check('64 convex plot areas and exact shifted-line offsets consistent', len(net['blocks']) == 64)
    first = net['blocks'][0]
    check('offset check rejects excessive 1m deduction', not same_polygon(first['netAsphaltOnlyPolygon'], offset_by_line_intersections(first['centrelinePolygon'], first['boundaryAsphaltWidthsMetres'], 1)))
    check('land subtotals and residential assigned denominator', all(close(v, net['programmeTotals'][k]['netAsphaltOnlyMetres2']) for k, v in totals.items()) and close(totals['residential']/sum(totals.values()), net['residentialShareOfAssignedBlockNetAsphaltOnly']))
    check('incomplete blue denominator explicitly not accepted', not net['completeBlueNetDevelopableDenominatorKnown'] and not net['finalResidentialAboutHalfAccepted'] and net['sidewalk2mIsSensitivityNotAdopted'])
    check('no ordinary region admission, metre claim or game test', actual['metreCalibration'] is None and actual['wholeCityCoverageFraction'] is None and not actual['trafficValidated'] and not actual['admittedAsOrdinaryCityRegion'] and not actual['formalGameTestsPerformed'])
    report = {'recordedAt': datetime.now(timezone.utc).isoformat(), 'status': 'passed', 'checks': CHECKS, 'checkCount': len(CHECKS), 'segmentPairsExamined': len(segments)*(len(segments)-1)//2, 'expectedIntersectionsExamined': crossing_count, 'protectedFilesMatched': 91, 'formalGameTestsPerformed': False}
    destination = HERE/'verification/static-artifact-checks.json'
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'checks'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
