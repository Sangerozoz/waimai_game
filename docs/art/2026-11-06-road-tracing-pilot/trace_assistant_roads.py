#!/usr/bin/env python3
"""Assistant visual centerline tracing, then read the actual vectors into a small graph."""
import copy
import hashlib
import heapq
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
A = (320, 553)
C = (1083, 343)
J = (990, 601)
# Original image pixel coordinates, inspected from the new native artwork.
# These are assistant-drawn lines, NOT a claim of automatic semantic image recognition.
ROADS = [
    ('主路西', [(0, 521), (100, 538), (200, 548), (260, 548), A]),
    ('主路中', [A, (400, 571), (600, 591), (800, 601), J]),
    ('主路东', [J, (1200, 595), (1400, 583), (1535, 576)]),
    ('主路北', [(1223, 0), (1182, 100), (1143, 200), C]),
    ('中段', [C, (1052, 400), (1022, 500), J]),
    ('主路南', [J, (956, 700), (922, 800), (889, 900), (849, 1023)]),
    ('上方环路', [A, (322, 515), (328, 482), (345, 448), (368, 409),
                  (397, 368), (431, 338), (473, 316), (530, 307),
                  (600, 303), (750, 304), (900, 307), (1000, 317), (1043, 334), C]),
    ('左下独立车道', [(91, 784), (120, 782), (150, 782), (190, 780),
                        (270, 795), (350, 808), (430, 820)]),
]


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def graph_from_tiled(doc):
    nodes = []
    edges = []
    lookup = {}

    def node(p):
        key = tuple(round(v, 6) for v in p)
        if key not in lookup:
            lookup[key] = len(nodes)
            nodes.append({'id': len(nodes), 'pixel': list(p)})
        return lookup[key]

    for layer in doc['layers']:
        if layer.get('name') != '助手描线（可编辑）':
            continue
        for o in layer['objects']:
            pts = [[o['x'] + p['x'], o['y'] + p['y']] for p in o['polyline']]
            edges.append({'id': len(edges), 'name': o['name'], 'from': node(pts[0]),
                          'to': node(pts[-1]), 'points': pts, 'bidirectional': True,
                          'lengthPixels': sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))})
    adjacency = {n['id']: [] for n in nodes}
    for e in edges:
        adjacency[e['from']].append((e['to'], e['lengthPixels'], e['id']))
        adjacency[e['to']].append((e['from'], e['lengthPixels'], e['id']))
    components = []
    unseen = set(adjacency)
    while unseen:
        todo = [min(unseen)]
        component = []
        while todo:
            u = todo.pop()
            if u not in unseen:
                continue
            unseen.remove(u)
            component.append(u)
            todo.extend(v for v, _, _ in adjacency[u])
        components.append(sorted(component))
    start = lookup[(1223, 0)]
    goal = lookup[(0, 521)]
    queue = [(0, start, [])]
    visited = set()
    example = None
    while queue:
        distance, u, route = heapq.heappop(queue)
        if u in visited:
            continue
        visited.add(u)
        if u == goal:
            example = {'startNode': start, 'endNode': goal, 'edgeIds': route,
                       'lengthPixels': distance, 'algorithm': 'Dijkstra-on-drawn-vectors'}
            break
        for v, length, edge_id in adjacency[u]:
            heapq.heappush(queue, (distance + length, v, route + [edge_id]))
    if example is not None:
        current = start
        points = []
        for edge_id in example['edgeIds']:
            edge = edges[edge_id]
            assert current in (edge['from'], edge['to'])
            forward = current == edge['from']
            oriented = edge['points'] if forward else list(reversed(edge['points']))
            points.extend(oriented if not points else oriented[1:])
            current = edge['to'] if forward else edge['from']
        assert current == goal
        example['points'] = points
    return {'coordinateSpace': 'native-image-pixels', 'unitsAreNotMetres': True,
            'source': 'assistant-drawn Tiled polylines; not inferred city semantics',
            'nodes': nodes, 'edges': edges, 'connectedComponents': components,
            'exampleRoute': example, 'integratedIntoGame': False}


def main():
    output = HERE / '画路试验_助手描线.tmj'
    if output.exists():
        raise SystemExit('Preserve existing assistant route edits; refusing to overwrite')
    source = HERE / '画路试验.tmj'
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    doc = copy.deepcopy(json.loads(source.read_text()))
    image_layer = next(l for l in doc['layers'] if l['type'] == 'imagelayer')
    assert image_layer.get('x', 0) == 0 and image_layer.get('y', 0) == 0
    image = Image.open(HERE / image_layer['image']).convert('RGB')
    assert image.size == (1536, 1024)
    draw = ImageDraw.Draw(image)
    objects = []
    oid = max([doc.get('nextobjectid', 1)] +
              [o['id'] + 1 for l in doc['layers'] for o in l.get('objects', [])])
    heuristic = []
    native = Image.open(HERE / image_layer['image']).convert('RGB')
    for index, (name, points) in enumerate(ROADS):
        x, y = points[0]
        objects.append({'id': oid + index, 'name': name, 'type': 'road', 'x': x, 'y': y,
                        'width': 0, 'height': 0, 'rotation': 0, 'visible': True,
                        'polyline': [{'x': p[0] - x, 'y': p[1] - y} for p in points],
                        'properties': [
                            {'name': 'traceMethod', 'type': 'string', 'value': 'assistant-visual-trace'},
                            {'name': 'connectivity', 'type': 'string',
                             'value': 'independent-lane' if index == 7 else 'main-network'}]})
        color = '#ff28b8' if index < 7 else '#ffaa00'
        draw.line(points, fill=color, width=5, joint='curve')
        for p in points:
            draw.ellipse((p[0]-3, p[1]-3, p[0]+3, p[1]+3), fill=color)
        samples = []
        for a, b in zip(points, points[1:]):
            steps = max(1, math.ceil(math.dist(a, b)))
            for i in range(steps + 1):
                q = [round(a[k] + (b[k] - a[k]) * i / steps) for k in (0, 1)]
                rgb = native.getpixel(tuple(q))
                assert isinstance(rgb, tuple)
                samples.append(max(rgb)-min(rgb) < 24 and 65 < sum(rgb)/3 < 182)
        heuristic.append({'road': name, 'sampleCount': len(samples),
                          'grayAsphaltColorSupport': sum(samples)/len(samples),
                          'caveat': 'color-only diagnostic; not proof of semantic road correctness'})
    layer_id = max(l['id'] for l in doc['layers']) + 1
    doc['layers'].append({'id': layer_id, 'type': 'objectgroup', 'name': '助手描线（可编辑）',
                          'draworder': 'index', 'x': 0, 'y': 0, 'opacity': 1,
                          'visible': True, 'locked': False, 'color': '#ff28b8', 'objects': objects})
    doc['nextobjectid'] = oid + len(objects)
    doc['nextlayerid'] = layer_id + 1
    save(output, doc)
    # Re-read the exact Tiled file, rather than constructing graph results from an unrelated list.
    actual = json.loads(output.read_text())
    graph = graph_from_tiled(actual)
    assert graph['exampleRoute'] is not None
    assert len(graph['connectedComponents']) == 2, 'Do not silently join isolated lane'
    save(HERE / 'assistant-road-network.json', graph)
    image.save(HERE / 'assistant-centerlines.png')
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    report = {'originalUserMapUnchanged': True, 'originalUserMapSHA256': before,
              'assistantMap': output.name, 'polylineCount': len(objects),
              'nodes': len(graph['nodes']), 'edges': len(graph['edges']),
              'componentCount': len(graph['connectedComponents']),
              'exampleRoute': graph['exampleRoute'], 'roadPixelDiagnostics': heuristic,
              'traceIsAssistantAuthoredNotAutomaticImageRecognition': True,
              'noGameOrSaveOrOriginalRoadChanges': True}
    save(HERE / 'assistant-trace-report.json', report)
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
