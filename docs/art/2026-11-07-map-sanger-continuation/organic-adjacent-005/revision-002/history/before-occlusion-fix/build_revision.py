"""Supplement the single-native trace. Original artwork and v1 evidence are read-only."""
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
OLD = HERE.parent
BASE = OLD.parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def load_graph():
    data = json.loads((HERE / 'trace-input.json').read_text())
    assert sha(OLD / 'native.png') == data['sourceSHA256']
    assert sha(OLD / 'actual-005-graph.json') == '28192e3989e08913d3ee97dc7f94b68ce6580d927d9dfe9c94c9921332887ac9'
    spec = importlib.util.spec_from_file_location('original_evidence_builder', OLD / 'build_actual_evidence.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    graph = json.loads((OLD / 'actual-005-graph.json').read_text())
    assert not set(data['newNodes']).intersection(graph['nodes'])
    graph['nodes'].update(data['newNodes'])
    for edge in data['newEdges']:
        u, v = edge['from'], edge['to']
        points = [graph['nodes'][u], *edge['mids'], graph['nodes'][v]]
        graph['edges'].append({
            'id': u + '--' + v, 'from': u, 'to': v, 'points': points,
            'lengthPixels': sum(math.dist(a, b) for a, b in zip(points, points[1:])),
            'navigationAllowed': True, 'surfaceObservation': 'visible-asphalt-manual-trace',
            'bidirectionalAssumption': True, 'trafficVerified': False,
            'revision': '002', 'pairAdmissionAllowed': False,
        })
    graph['source'] = '../native.png'
    graph['sourceSHA256'] = data['sourceSHA256']
    graph['scope'] = '005 single-native visible-road evidence; all five observed building-bearing enclosures traced; shared enclosure is not an exclusive addition'
    graph['statistics'], faces = helper.analyse(graph)
    block_number = 0
    for face in faces:
        node_set = set(face['nodeCycle'])
        island = node_set == set(data['channelizingIslandNodeSet'])
        shared = node_set == set(data['sharedEnclosureNodeSet'])
        if island:
            face.update(id='ISLAND-1', classification='channelizing-island-no-buildings', countedAsStreetBlock=False, sharedBand=False)
        else:
            block_number += 1
            face.update(id='005-B' + str(block_number), classification='visible-street-block-enclosure', countedAsStreetBlock=True,
                        sharedBand=shared, outsideSharedBandGeometry=not shared, exclusiveNewBlockCountAllowed=False,
                        ownershipScope='overlaps004; not an exclusive005 addition' if shared else 'enclosure centreline entirely west of the1520 shared-band boundary; whole-object seam ownership is separate')
    graph['boundedFaceGeometry'] = faces
    graph['demonstratedStreetBlockEnclosures'] = 5
    graph['visualInventory'].update(fullyTracedBuildingBearingEnclosures=5, northeastSharedEnclosureOmittedFromTrace=False,
                                    nonSharedCentrelineEnclosures=4, sharedCentrelineEnclosures=1,
                                    source='revision-002/RESULT.md', exclusiveNewBlockOwnershipResolved=False)
    graph['fullStreetInventoryComplete'] = False
    graph['sharedEnclosureExclusiveNewCount'] = 0
    graph['wholeSeamRegistrationComplete'] = False
    graph['pairAdmissionAllowed'] = False
    graph['pairContext'] = data['navigationContext']
    graph['routes'] = {
        'main': helper.route(graph, 'MW', 'MP'),
        'alternative': helper.route(graph, 'MW', 'MP', 'M1--ML'),
    }
    assert graph['statistics']['boundedFaces'] == 6
    assert sum(f['countedAsStreetBlock'] for f in faces) == 5
    assert sum(f['sharedBand'] for f in faces) == 1
    tmj = helper.tmj(graph, [('005 unchanged native', '../../native.png', 1671, 941, 0, 0)], include_design=True)
    tmj['properties'] = helper.props({
        'unit': 'native pixels', 'metreCalibration': 'unestablished', 'fullStreetInventoryComplete': False,
        'trafficVerified': False, 'formalGameTests': False, 'ordinaryRegionAdmitted': False,
        'evidenceScope': graph['scope'], 'wholeSeamRegistrationComplete': False, 'pairAdmissionAllowed': False,
        'observedBuildingBearingEnclosures': 5, 'sharedEnclosuresNotExclusiveNew': 1,
    })
    for prop in tmj['properties']:
        if isinstance(prop['value'], int) and not isinstance(prop['value'], bool):
            prop['type'] = 'int'
    # The original design is archival only, hidden and explicitly non-navigable.
    face_objects = []
    next_id = tmj['nextobjectid']
    for face in faces:
        x, y = face['polygon'][0]
        face_objects.append({
            'id': next_id, 'name': face['id'], 'type': 'observed-enclosure', 'x': x, 'y': y,
            'width': 0, 'height': 0, 'rotation': 0, 'visible': True,
            'polygon': [{'x': px - x, 'y': py - y} for px, py in face['polygon']],
            'properties': helper.props({k: face[k] for k in ['classification', 'countedAsStreetBlock', 'sharedBand']}),
        })
        next_id += 1
    tmj['layers'].append({'id': tmj['nextlayerid'], 'type': 'objectgroup', 'name': 'observed-enclosures-not-land-parcels',
                          'visible': False, 'opacity': 0.6, 'draworder': 'index', 'objects': face_objects})
    tmj['nextobjectid'] = next_id
    tmj['nextlayerid'] += 1
    return graph, tmj


def write_owned(outputs):
    manifest_path = HERE / 'generated-files.json'
    previous = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    # Preflight the entire write set before the first mutation.
    for relative in outputs:
        path = HERE / relative
        assert path.resolve().is_relative_to(HERE.resolve())
        if path.exists():
            assert relative in previous and sha(path) == previous[relative]['sha256'], relative
    for relative, raw in outputs.items():
        path = HERE / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    manifest_path.write_bytes(encoded({name: {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
                                       for name, raw in sorted(outputs.items())}))


def main():
    graph, tmj = load_graph()
    image = Image.open(OLD / 'native.png').convert('RGB')
    draw = ImageDraw.Draw(image)
    new_ids = {edge['from'] + '--' + edge['to'] for edge in json.loads((HERE / 'trace-input.json').read_text())['newEdges']}
    for edge in graph['edges']:
        draw.line([tuple(p) for p in edge['points']], fill='#00bfe0' if edge['id'] in new_ids else '#e3369f', width=2)
    for face in graph['boundedFaceGeometry']:
        xs, ys = zip(*face['polygon'])
        x, y = sum(xs) / len(xs), sum(ys) / len(ys)
        label = face['id'] + (' SHARED' if face['sharedBand'] else '')
        draw.rectangle((x - 3, y - 2, x + len(label) * 6 + 4, y + 14), fill='white')
        draw.text((x, y), label, fill='#002c60' if face['countedAsStreetBlock'] else '#af2500')
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    viewer = {'graph': graph, 'newEdgeIds': sorted(new_ids)}
    template = (HERE / 'viewer-template.html').read_text()
    assert template.count('__REVISION_DATA__') == 1
    write_owned({
        'actual-005-graph.json': encoded(graph), 'tiled/native005.tmj': encoded(tmj),
        'trace-overlay.png': buffer.getvalue(), 'viewer-data.json': encoded(viewer),
        'index.html': template.replace('__REVISION_DATA__', json.dumps(viewer, ensure_ascii=False)).encode(),
    })
    print(json.dumps({'statistics': graph['statistics'], 'buildingBearingEnclosures': 5, 'sharedEnclosures': 1,
                      'routes': {key: route['lengthPixels'] for key, route in graph['routes'].items()},
                      'pairGraphUpdated': False, 'nativeArtworkModified': False}))


if __name__ == '__main__':
    main()
