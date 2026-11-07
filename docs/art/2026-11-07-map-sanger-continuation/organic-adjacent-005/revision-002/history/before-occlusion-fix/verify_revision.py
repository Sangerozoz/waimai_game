"""Read-only mathematical checks by default; --write-report records this revision only."""
import argparse
import hashlib
import importlib.util
import json
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
    stats = verifier.geometry(graph, '005-r2')
    need('26 original edges untouched', graph['edges'][:len(previous['edges'])] == previous['edges'])
    need('22 original node coordinates untouched', all(graph['nodes'][key] == value for key, value in previous['nodes'].items()))
    need('exact four added nodes', {key: value for key, value in graph['nodes'].items() if key not in previous['nodes']} == inputs['newNodes'])
    need('five added edges explicitly single-native only', len(graph['edges']) == 31 and all(edge['pairAdmissionAllowed'] is False for edge in graph['edges'][26:]))
    faces = graph['boundedFaceGeometry']
    need('five building enclosures and one excluded island', len(faces) == 6 and sum(face['countedAsStreetBlock'] for face in faces) == 5
         and sum(not face['countedAsStreetBlock'] for face in faces) == 1)
    shared = [face for face in faces if face['sharedBand']]
    need('fifth enclosure shared and not counted as exclusive', len(shared) == 1 and set(shared[0]['nodeCycle']) == set(inputs['sharedEnclosureNodeSet'])
         and min(p[0] for p in shared[0]['polygon']) < 1520 < max(p[0] for p in shared[0]['polygon'])
         and graph['sharedEnclosureExclusiveNewCount'] == 0 and all(face.get('exclusiveNewBlockCountAllowed') is False for face in faces if face['countedAsStreetBlock']))
    need('four nonshared enclosure geometries west of overlap', sum(face['countedAsStreetBlock'] and max(p[0] for p in face['polygon']) <= 1520 for face in faces) == 4)
    need('island node set exact', set(next(face for face in faces if not face['countedAsStreetBlock'])['nodeCycle']) == set(inputs['channelizingIslandNodeSet']))
    need('retained unresolved scope', graph['fullStreetInventoryComplete'] is False and graph['metreCalibration'] is None
         and graph['trafficVerified'] is False and graph['wholeSeamRegistrationComplete'] is False and graph['pairAdmissionAllowed'] is False)
    for name, route in graph['routes'].items():
        verifier.verify_route(graph, route, 'single-native-' + name)
    need('single-native detour excludes named edge', graph['routes']['alternative']['excludedEdge'] == 'M1--ML')

    tiled = read(HERE / 'tiled/native005.tmj')
    groups = {layer['name']: layer for layer in tiled['layers'] if layer['type'] == 'objectgroup'}
    need('exact TMJ groups', set(groups) == {'visible-asphalt-trace', 'main-route', 'alternative-route', 'design-only-hidden-not-navigation', 'observed-enclosures-not-land-parcels'})
    images = [layer for layer in tiled['layers'] if layer['type'] == 'imagelayer']
    need('one unchanged native image layer', len(images) == 1 and images[0]['image'] == '../../native.png'
         and (HERE / 'tiled' / images[0]['image']).resolve() == (OLD / 'native.png').resolve()
         and (images[0]['offsetx'], images[0]['offsety'], images[0]['imagewidth'], images[0]['imageheight']) == (0, 0, 1671, 941)
         and images[0]['visible'] is True and images[0]['locked'] is True and images[0]['opacity'] == 1)
    need('TMJ dimensions and no scaling', (tiled['width'], tiled['height'], tiled['tilewidth'], tiled['tileheight']) == (1671, 941, 1, 1))
    roads = groups['visible-asphalt-trace']['objects']
    need('full road name coverage without duplicates', len(roads) == 31 and len({o['name'] for o in roads}) == 31 and {o['name'] for o in roads} == {e['id'] for e in graph['edges']})
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
        need('enclosure typed semantics ' + face['id'], verifier.properties(obj) == verifier.typed({key: face[key] for key in ['classification', 'countedAsStreetBlock', 'sharedBand']}))
    all_objects = [obj for layer in groups.values() for obj in layer['objects']]
    need('TMJ unique contiguous object and layer IDs', sorted(o['id'] for o in all_objects) == list(range(1, tiled['nextobjectid']))
         and sorted(layer['id'] for layer in tiled['layers']) == list(range(1, tiled['nextlayerid'])))
    properties = tiled['properties']
    need('map properties unique and int values correctly typed', len({p['name'] for p in properties}) == len(properties)
         and all((p['type'] == 'int' and type(p['value']) is int) or (p['type'] == 'bool' and type(p['value']) is bool) or (p['type'] == 'string' and type(p['value']) is str) for p in properties))
    values = {p['name']: p['value'] for p in properties}
    need('TMJ map scope', values == {'unit': 'native pixels', 'metreCalibration': 'unestablished', 'fullStreetInventoryComplete': False,
         'trafficVerified': False, 'formalGameTests': False, 'ordinaryRegionAdmitted': False, 'evidenceScope': graph['scope'],
         'wholeSeamRegistrationComplete': False, 'pairAdmissionAllowed': False, 'observedBuildingBearingEnclosures': 5, 'sharedEnclosuresNotExclusiveNew': 1})
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
              'checkCount': len(verifier.CHECKS), 'checks': verifier.CHECKS, 'statistics': stats,
              'protectedFilesMatched': len(protected['files']), 'priorFilesAudited': len(snapshot['priorManifest']['files']),
              'actual005BuildingEnclosuresTraced': 5, 'sharedEnclosuresExcludedFromExclusiveCount': 1,
              'wholeSeamRegistrationComplete': False, 'objectOwnershipResolved': False, 'formalGameTestsPerformed': False,
              'visualAsphaltCertifiedByScript': False}
    if args.write_report:
        destination = HERE / 'verification/static-checks.json'
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({key: value for key, value in report.items() if key != 'checks'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
