"""Read-only mathematical checks by default; --write-report records this revision only."""
import argparse
import hashlib
import importlib.util
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
OLD = HERE.parent
BASE = OLD.parent
ROOT = BASE.parents[2]


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def structure_geometry(graph, need):
    """Check structure using exact integer cross products, without treating inference as asphalt."""
    nodes, edges = graph['nodes'], graph['edges']
    segments = []
    adjacent = defaultdict(list)
    directed = {}
    need('structure unique edge IDs', len({edge['id'] for edge in edges}) == len(edges))
    for edge in edges:
        u, v, points = edge['from'], edge['to'], edge['points']
        need('structure endpoints and weights ' + edge['id'], points[0] == nodes[u] and points[-1] == nodes[v]
             and math.isclose(edge['lengthPixels'], sum(math.dist(a,b) for a,b in zip(points,points[1:])), abs_tol=1e-9))
        for index, (a,b) in enumerate(zip(points, points[1:])):
            need('structure nonzero segment ' + edge['id'] + str(index), a != b)
            segments.append((edge['id'], index, tuple(a), tuple(b), {u,v}))
        for a,b,ps in [(u,v,points),(v,u,points[::-1])]:
            adjacent[a].append(b)
            directed[a,b] = ps
    cross = lambda a,b,c: (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    for i,(eid,idx,a,b,ends) in enumerate(segments):
        for fid,jdx,c,d,other in segments[i+1:]:
            if max(a[0],b[0]) < min(c[0],d[0]) or max(c[0],d[0]) < min(a[0],b[0]) or max(a[1],b[1]) < min(c[1],d[1]) or max(c[1],d[1]) < min(a[1],b[1]):
                continue
            orientations = [cross(a,b,c),cross(a,b,d),cross(c,d,a),cross(c,d,b)]
            if orientations[0]*orientations[1] <= 0 and orientations[2]*orientations[3] <= 0:
                common = {a,b} & {c,d}
                assert len(common) == 1, (eid,fid,'crossing')
                point = next(iter(common))
                assert (eid == fid and abs(idx-jdx) == 1) or point in {tuple(nodes[k]) for k in ends & other}, (eid,fid,'unmerged')
                if all(value == 0 for value in orientations):
                    aa,bb = next(p for p in (a,b) if p != point),next(p for p in (c,d) if p != point)
                    assert sum((aa[k]-point[k])*(bb[k]-point[k]) for k in (0,1)) <= 0, (eid,fid,'overlap')
    pending,components = set(nodes),0
    while pending:
        components += 1
        stack = [pending.pop()]
        while stack:
            for node in adjacent[stack.pop()]:
                if node in pending:
                    pending.remove(node)
                    stack.append(node)
    for u,neighbors in adjacent.items():
        neighbors.sort(key=lambda v: math.atan2(directed[u,v][1][1]-nodes[u][1], directed[u,v][1][0]-nodes[u][0]))
    seen,faces = set(),[]
    for start in directed:
        if start in seen:
            continue
        edge,cycle,polygon = start,[],[]
        while edge not in seen:
            seen.add(edge)
            u,v = edge
            cycle.append(u)
            polygon += directed[u,v][:-1]
            neighbors = adjacent[v]
            edge = v,neighbors[(neighbors.index(u)-1) % len(neighbors)]
        assert edge == start
        area = sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(polygon,polygon[1:]+polygon[:1])) / 2
        if area > 0:
            faces.append((cycle,polygon,area))
    canonical = lambda cycle: min(tuple(cycle[i:]+cycle[:i]) for i in range(len(cycle)))
    recorded = {canonical(face['nodeCycle']):face for face in graph['boundedFaceGeometry']}
    need('structure complete face coverage', len(recorded) == len(faces) == len(graph['boundedFaceGeometry'])
         and set(recorded) == {canonical(cycle) for cycle,_,_ in faces})
    for cycle,polygon,area in faces:
        recorded_face = recorded[canonical(cycle)]
        need('structure exact face vertices ' + ','.join(cycle), canonical(polygon) == canonical(recorded_face['polygon'])
             and area == recorded_face['centrelineEnclosedPixels2'])
    stats = {'nodes':len(nodes),'edges':len(edges),'components':components,'segments':len(segments),
             'segmentPairsExamined':len(segments)*(len(segments)-1)//2,'boundedFaces':len(faces),'unexpectedIntersections':[]}
    need('structure recorded statistics and Euler', stats == graph['statistics'] and len(faces) == len(edges)-len(nodes)+components and components == 1)
    return stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    # Reuse the already reviewed independent verifier, never its writing main().
    spec = importlib.util.spec_from_file_location('independent_v1_verifier', OLD / 'verify_005.py')
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    need = verifier.need
    graph = read(HERE / 'actual-005-graph.json')
    previous = read(OLD / 'actual-005-graph.json')
    inputs = read(HERE / 'trace-input.json')
    ownership = read(HERE / 'ownership.json')
    for source, path, size in [('005', OLD / 'native.png', (1671, 941)), ('004', BASE / 'organic-layout-004/native.png', (1672, 941))]:
        need(source + ' original bytes and dimensions', sha(path) == ownership['sourceSHA256'][source] and Image.open(path).size == size)
    stats = structure_geometry(graph, need)
    navigation = {**graph, 'edges': [edge for edge in graph['edges'] if edge['navigationAllowed']],
                  'statistics': graph['navigationStatistics'], 'boundedFaceGeometry': graph['navigationBoundedFaceGeometry']}
    nav_stats = verifier.geometry(navigation, '005-r2-navigation')
    need('26 original edges untouched', graph['edges'][:len(previous['edges'])] == previous['edges'])
    need('22 original node coordinates untouched', all(graph['nodes'][key] == value for key, value in previous['nodes'].items()))
    need('exact six added nodes', {key: value for key, value in graph['nodes'].items() if key not in previous['nodes']} == inputs['newNodes'])
    need('seven added edges explicitly single-native only', len(graph['edges']) == 33 and all(edge['pairAdmissionAllowed'] is False for edge in graph['edges'][26:]))
    forbidden = [edge for edge in graph['edges'] if not edge['navigationAllowed']]
    need('one explicit non-asphalt inference', len(forbidden) == 1 and forbidden[0]['id'] == 'OC1--OC2'
         and forbidden[0]['surfaceObservation'] == 'roof-occluded-inference-not-navigable'
         and nav_stats['edges'] == 32 and nav_stats['boundedFaces'] == 5)
    faces = graph['boundedFaceGeometry']
    need('five building enclosures and one excluded island', len(faces) == 6 and sum(face['countedAsStreetBlock'] for face in faces) == 5
         and sum(not face['countedAsStreetBlock'] for face in faces) == 1)
    shared = [face for face in faces if face['sharedBand']]
    need('fifth enclosure shared and not counted as exclusive', len(shared) == 1 and set(shared[0]['nodeCycle']) == set(inputs['sharedEnclosureNodeSet'])
         and min(p[0] for p in shared[0]['polygon']) < 1520 < max(p[0] for p in shared[0]['polygon'])
         and graph['sharedEnclosureExclusiveNewCount'] == 0 and all(face.get('exclusiveNewBlockCountAllowed') is False for face in faces if face['countedAsStreetBlock']))
    need('fifth enclosure inference disclosed and only four visible-road closures', shared[0]['includesOccludedInference'] is True
         and graph['demonstratedStreetBlockEnclosures'] == 4 and graph['structuralStreetBlockEnclosures'] == 5
         and graph['visualInventory']['fullyTracedBuildingBearingEnclosures'] == 4)
    need('four nonshared enclosure geometries west of overlap', sum(face['countedAsStreetBlock'] and max(p[0] for p in face['polygon']) <= 1520 for face in faces) == 4)
    need('island node set exact', set(next(face for face in faces if not face['countedAsStreetBlock'])['nodeCycle']) == set(inputs['channelizingIslandNodeSet']))
    need('retained unresolved scope', graph['fullStreetInventoryComplete'] is False and graph['metreCalibration'] is None
         and graph['trafficVerified'] is False and graph['wholeSeamRegistrationComplete'] is False and graph['pairAdmissionAllowed'] is False)
    for name, route in graph['routes'].items():
        verifier.verify_route(graph, route, 'single-native-' + name)
        need('route excludes inference ' + name, 'OC1--OC2' not in route['edgeIds'])
    checkpoint = len(verifier.CHECKS)
    rejected = False
    bad = forbidden[0]
    try:
        verifier.verify_route(graph, {'from':bad['from'],'to':bad['to'],'excludedEdge':None,
            'nodeSequence':[bad['from'],bad['to']],'edgeIds':[bad['id']],'points':bad['points'],
            'lengthPixels':bad['lengthPixels'],'metres':None,'geometricBidirectionalAssumption':True}, 'intentional-rejection')
    except AssertionError:
        rejected = True
    del verifier.CHECKS[checkpoint:]
    need('regression rejects route through inferred building projection', rejected)
    need('single-native detour excludes named edge', graph['routes']['alternative']['excludedEdge'] == 'M1--ML')

    tiled = read(HERE / 'tiled/native005.tmj')
    groups = {layer['name']: layer for layer in tiled['layers'] if layer['type'] == 'objectgroup'}
    need('exact TMJ groups', set(groups) == {'visible-asphalt-trace', 'occluded-inference-not-navigation', 'main-route', 'alternative-route', 'design-only-hidden-not-navigation', 'observed-enclosures-not-land-parcels'})
    images = [layer for layer in tiled['layers'] if layer['type'] == 'imagelayer']
    need('one unchanged native image layer', len(images) == 1 and images[0]['image'] == '../../native.png'
         and (HERE / 'tiled' / images[0]['image']).resolve() == (OLD / 'native.png').resolve()
         and (images[0]['offsetx'], images[0]['offsety'], images[0]['imagewidth'], images[0]['imageheight']) == (0, 0, 1671, 941)
         and images[0]['visible'] is True and images[0]['locked'] is True and images[0]['opacity'] == 1)
    need('TMJ dimensions and no scaling', (tiled['width'], tiled['height'], tiled['tilewidth'], tiled['tileheight']) == (1671, 941, 1, 1))
    roads = groups['visible-asphalt-trace']['objects'] + groups['occluded-inference-not-navigation']['objects']
    need('visible road layer excludes inference', len(groups['visible-asphalt-trace']['objects']) == 32
         and all(o['name'] != 'OC1--OC2' for o in groups['visible-asphalt-trace']['objects'])
         and groups['occluded-inference-not-navigation']['visible'] is False
         and [o['name'] for o in groups['occluded-inference-not-navigation']['objects']] == ['OC1--OC2'])
    need('full road name coverage without duplicates', len(roads) == 33 and len({o['name'] for o in roads}) == 33 and {o['name'] for o in roads} == {e['id'] for e in graph['edges']})
    by_name = {o['name']: o for o in roads}
    for edge in graph['edges']:
        values = {key: edge[key] for key in ['from', 'to', 'lengthPixels', 'navigationAllowed', 'surfaceObservation', 'bidirectionalAssumption', 'trafficVerified']}
        verifier.line_object(by_name[edge['id']], edge['points'], values, 'TMJ-' + edge['id'])
    for name, route in graph['routes'].items():
        layer = groups[name + '-route']
        need('route hidden ' + name, layer['visible'] is False and len(layer['objects']) == 1)
        verifier.line_object(layer['objects'][0], route['points'], {'lengthPixels': route['lengthPixels'], 'trafficVerified': False}, 'TMJ-' + name)
    design = groups['design-only-hidden-not-navigation']
    design_edges = read(OLD / 'structure-guide.json')['roads']
    need('hidden complete original design layer', design['visible'] is False and len(design['objects']) == len(design_edges)
         and len({o['name'] for o in design['objects']}) == len(design_edges) and {o['name'] for o in design['objects']} == {e['id'] for e in design_edges})
    for edge in design_edges:
        obj = next(o for o in design['objects'] if o['name'] == edge['id'])
        verifier.line_object(obj, edge['points'], {'designOnly': True, 'navigationAllowed': False, 'kind': edge['kind']}, 'TMJ-design-' + edge['id'])
    enclosure_layer = groups['observed-enclosures-not-land-parcels']
    need('six hidden enclosure objects', enclosure_layer['visible'] is False and len(enclosure_layer['objects']) == 6
         and {o['name'] for o in enclosure_layer['objects']} == {face['id'] for face in faces})
    for face in faces:
        obj = next(o for o in enclosure_layer['objects'] if o['name'] == face['id'])
        need('enclosure all polygon vertices ' + face['id'], len(obj['polygon']) == len(face['polygon'])
             and [[obj['x'] + p['x'], obj['y'] + p['y']] for p in obj['polygon']] == face['polygon'])
        need('enclosure typed semantics ' + face['id'], verifier.properties(obj) == verifier.typed({key: face[key] for key in ['classification', 'countedAsStreetBlock', 'sharedBand', 'includesOccludedInference']}))
    all_objects = [obj for layer in groups.values() for obj in layer['objects']]
    need('TMJ unique contiguous object and layer IDs', sorted(o['id'] for o in all_objects) == list(range(1, tiled['nextobjectid']))
         and sorted(layer['id'] for layer in tiled['layers']) == list(range(1, tiled['nextlayerid'])))
    properties = tiled['properties']
    need('map properties unique and int values correctly typed', len({p['name'] for p in properties}) == len(properties)
         and all((p['type'] == 'int' and type(p['value']) is int) or (p['type'] == 'bool' and type(p['value']) is bool) or (p['type'] == 'string' and type(p['value']) is str) for p in properties))
    values = {p['name']: p['value'] for p in properties}
    need('TMJ map scope', values == {'unit': 'native pixels', 'metreCalibration': 'unestablished', 'fullStreetInventoryComplete': False,
         'trafficVerified': False, 'formalGameTests': False, 'ordinaryRegionAdmitted': False, 'evidenceScope': graph['scope'],
         'wholeSeamRegistrationComplete': False, 'pairAdmissionAllowed': False, 'observedBuildingBearingEnclosures': 5, 'sharedEnclosuresNotExclusiveNew': 1,
         'fullyVisibleRoadEnclosures': 4, 'sharedEnclosureIncludesOccludedBoundary': True})
    need('expanded004 M-1 box covers visible right facade', next(o for o in ownership['objects'] if o['id'] == 'M-1')['sourceBounds']['004'][2] >= 40)
    need('ownership proposals honest and bounded', ownership['objectOwnershipResolved'] is False and ownership['silhouetteMasksProduced'] is False
         and ownership['sourceSelectionsAreProposalsOnly'] is True and ownership['wholeSeamRegistrationComplete'] is False and ownership['rectangularCutReady'] is False
         and len(ownership['objects']) == len({o['id'] for o in ownership['objects']}) == 8
         and sum(o['x1520CrossingObserved'] for o in ownership['objects']) == 3
         and all(o['selectionApprovedForAssembly'] is False for o in ownership['objects']))
    for obj in ownership['objects']:
        for source, (x0, y0, x1, y1) in obj['sourceBounds'].items():
            need('inspection box bounded ' + obj['id'] + source, 0 <= x0 < x1 <= (1671 if source == '005' else 1672) and 0 <= y0 < y1 <= 941)
    data = read(HERE / 'viewer-data.json')
    need('viewer graph and new edges exact', data['graph'] == graph and set(data['newEdgeIds']) == {e['id'] for e in graph['edges'][26:]})
    need('viewer generated from current data', (HERE / 'index.html').read_text() == (HERE / 'viewer-template.html').read_text().replace('__REVISION_DATA__', json.dumps(data, ensure_ascii=False)))
    for relative, item in read(HERE / 'generated-files.json').items():
        need('generated output ' + relative, sha(HERE / relative) == item['sha256'] and (HERE / relative).stat().st_size == item['bytes'])
    snapshot = read(HERE / 'start-record.json')
    for relative, item in snapshot['priorManifest']['files'].items():
        if relative not in snapshot['allowedExistingUpdates']:
            need('prior unchanged ' + relative, sha(BASE / relative) == item['sha256'])
        else:
            need('prior index archived ' + relative, sha(HERE / 'history/start' / relative) == item['sha256'])
    protected = read(ROOT / 'docs/team/handoffs/2026-11-07-map-codex-sanger/map-protected-snapshot.json')
    for relative, item in protected['files'].items():
        need('protected ' + relative, sha(ROOT / relative) == item['sha256'])
    report = {'recordedAt': datetime.now(timezone.utc).isoformat(), 'status': 'passed-bounded-evidence-only',
              'checkCount': len(verifier.CHECKS), 'checks': verifier.CHECKS, 'structuralStatistics': stats, 'navigationStatistics': nav_stats,
              'protectedFilesMatched': len(protected['files']), 'priorFilesAudited': len(snapshot['priorManifest']['files']),
              'structural005BuildingEnclosuresTraced': 5, 'fullyVisibleRoadEnclosures': 4, 'sharedEnclosureIncludesOccludedBoundary': True, 'sharedEnclosuresExcludedFromExclusiveCount': 1,
              'wholeSeamRegistrationComplete': False, 'objectOwnershipResolved': False, 'formalGameTestsPerformed': False,
              'visualAsphaltCertifiedByScript': False}
    if args.write_report:
        destination = HERE / 'verification/static-checks.json'
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({key: value for key, value in report.items() if key != 'checks'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
