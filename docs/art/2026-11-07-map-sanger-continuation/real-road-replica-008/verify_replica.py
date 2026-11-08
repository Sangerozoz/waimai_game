#!/usr/bin/env python3
"""Read-only unless --write-report; independently reconstruct from retained XML."""
import argparse
import collections
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'AGENTS.md').exists())


def cohen_sutherland(a, b, box):
    x0, y0 = a; x1, y1 = b
    def code(x, y):
        return (1 if x < box[0] else 2 if x > box[2] else 0) | (4 if y < box[1] else 8 if y > box[3] else 0)
    for _ in range(12):
        c0, c1 = code(x0, y0), code(x1, y1)
        if not (c0 | c1):
            return [(x0, y0), (x1, y1)] if math.dist((x0, y0), (x1, y1)) > 1e-8 else None
        if c0 & c1:
            return None
        c = c0 or c1
        if c & 8:
            x, y = x0+(x1-x0)*(box[3]-y0)/(y1-y0), box[3]
        elif c & 4:
            x, y = x0+(x1-x0)*(box[1]-y0)/(y1-y0), box[1]
        elif c & 2:
            x, y = box[2], y0+(y1-y0)*(box[2]-x0)/(x1-x0)
        else:
            x, y = box[0], y0+(y1-y0)*(box[0]-x0)/(x1-x0)
        if c == c0:
            x0, y0 = x, y
        else:
            x1, y1 = x, y
    raise AssertionError('Clipping failed to converge')


def main(write_report=False):
    count = 0
    def need(ok, message):
        nonlocal count
        count += 1
        if not ok:
            raise AssertionError(message)
    read = lambda n: json.loads((HERE/n).read_text())
    net, sel, prov = read('network.json'), read('selection.json'), read('source-provenance.json')
    source_nodes, source_ways = {}, {}
    for file in ['source.osm', 'city-roads.osm']:
        root = ET.parse(ROOT/'delivery-game/data/map-sample'/file).getroot()
        source_nodes.update({n.get('id'): (float(n.get('lon')), float(n.get('lat'))) for n in root.findall('node')})
        source_ways.update({w.get('id'): ([n.get('ref') for n in w.findall('nd')], {t.get('k'): t.get('v') for t in w.findall('tag')}) for w in root.findall('way')})
    sx, sy = 111320*math.cos(math.radians(36.235)), 111320
    xy = {n: ((lon-137.985)*sx, (lat-36.235)*sy) for n, (lon, lat) in source_nodes.items()}
    box = sel['sourceProjectedBounds']; original = json.loads((ROOT/'docs/art/2026-11-02-county-zoning/selection.json').read_text())['regions']['map']['worldBoundsMetresApprox']
    w, h = sel['sourceProjectedSize']
    need(abs(w*h/((original['maxX']-original['minX'])*(original['maxY']-original['minY']))-.25) < 1e-12, 'Reference quarter area')
    expected = {}
    for wid, (refs, tags) in source_ways.items():
        if 'highway' not in tags:
            continue
        for i, (a, b) in enumerate(zip(refs, refs[1:])):
            if xy[a] == xy[b]:
                continue
            clipped = cohen_sutherland(xy[a], xy[b], box)
            if clipped:
                expected[(wid, i)] = clipped
    actual = {(e['wayId'], e['sourceSegmentIndex']): e for e in net['segments']}
    need(len(actual) == len(net['segments']), 'No duplicate source segment records')
    need(actual.keys() == expected.keys(), 'Complete intersecting source segment coverage')
    need(set(net['ways']) == {wid for wid, _ in expected}, 'Exact source way coverage')
    max_error = 0.
    for (wid, i), pair in expected.items():
        e = actual[(wid, i)]; refs, tags = source_ways[wid]
        need(e['sourceNodeIds'] == refs[i:i+2], 'Original source endpoints')
        for key, point in zip([e['a'], e['b']], pair):
            node = net['nodes'][key]; error = math.dist(node['xy'], point); max_error = max(max_error, error)
            need(error < 1e-7, 'Independent clip geometry')
            need(box[0]-1e-7 <= point[0] <= box[2]+1e-7 and box[1]-1e-7 <= point[1] <= box[3]+1e-7, 'Clipped endpoint inside window')
            if key.startswith('osm:'):
                need(node['sourceNodeId'] == key[4:] and math.dist(node['lonLat'], source_nodes[key[4:]]) < 1e-10, 'Unmoved source node identity')
            else:
                need(node['sourceNodeId'] is None and node['boundaryCut'] and min(abs(point[0]-box[0]), abs(point[0]-box[2]), abs(point[1]-box[1]), abs(point[1]-box[3])) < 1e-7, 'Only synthetic boundary cut points')
    for wid, way in net['ways'].items():
        refs, tags = source_ways[wid]
        need(way['sourceNodeIds'] == refs, 'Full source node sequence retained')
        need(way['tags'] == {k: v for k, v in tags.items() if k in net['sourceTagWhitelist']}, 'Exact retained tag values')
    used = {e[k] for e in net['segments'] for k in ['a', 'b']}
    need(set(net['nodes']) == used, 'No invented or unused graph nodes')
    parts = [(p['wayId'], a, b) for p in net['parts'] for a, b in zip(p['nodes'], p['nodes'][1:])]
    need(collections.Counter(parts) == collections.Counter((e['wayId'], e['a'], e['b']) for e in net['segments']), 'Polyline parts cover each source segment once')
    geo = read('roads.geojson')
    need(len(geo['features']) == len(net['parts']), 'GeoJSON complete part coverage')
    svg = ET.parse(HERE/'roads.svg').getroot(); rendered = svg.findall('{http://www.w3.org/2000/svg}polyline')
    need(len(rendered) == len(net['parts']), 'SVG complete part coverage')
    expected_svg = collections.Counter()
    for f, part in zip(geo['features'], net['parts']):
        need(f['id'] == part['wayId']+':'+str(part['partIndex']), 'GeoJSON feature identity/order')
        props = {'osmWayId': part['wayId'], 'partIndex': part['partIndex'], 'pointKeys': part['nodes'], 'category': net['ways'][part['wayId']]['category'], **net['ways'][part['wayId']]['tags']}
        need(f['properties'] == props, 'GeoJSON complete properties')
        need(f['geometry'] == {'type': 'LineString', 'coordinates': [net['nodes'][n]['lonLat'] for n in part['nodes']]}, 'GeoJSON all vertices')
        expected_svg[' '.join(f'{net["nodes"][n]["xy"][0]-box[0]:.7f},{box[3]-net["nodes"][n]["xy"][1]:.7f}' for n in part['nodes'])] += 1
    need(collections.Counter(p.get('points') for p in rendered) == expected_svg, 'SVG all vertices after translation/Y reflection only')
    subset = ET.parse(HERE/'source-extract.osm').getroot()
    need({w.get('id') for w in subset.findall('way')} == set(net['ways']), 'XML exact way coverage')
    for node in subset.findall('node'):
        need((float(node.get('lon')), float(node.get('lat'))) == source_nodes[node.get('id')], 'XML raw coordinates unchanged')
    for way in subset.findall('way'):
        original_way = net['ways'][way.get('id')]
        need([n.get('ref') for n in way.findall('nd')] == original_way['sourceNodeIds'], 'XML complete original nodes')
        need({t.get('k'): t.get('v') for t in way.findall('tag')} == original_way['tags'], 'XML all retained tags')
    for rel, ref in prov['sourceFiles'].items():
        p = ROOT/rel
        need(p.stat().st_size == ref['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest() == ref['sha256'], 'Recorded source hash')
    generated = read('generated-files.json')['files']
    for name, ref in generated.items():
        p = HERE/name
        need(p.stat().st_size == ref['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest() == ref['sha256'], 'Generated output fingerprint')
    template = (HERE/'viewer-template.html').read_text(); page = (HERE/'index.html').read_text()
    payload = {'network': net, 'context': read('context.json'), 'statistics': read('statistics.json'), 'provenance': prov}
    need(page == template.replace('/*__DATA__*/null', json.dumps(payload, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')), 'Viewer exactly generated from template/data')
    need(net['geometricCrossingsMerged'] is False and net['navigationCertified'] is False and net['simplificationTolerance'] == 0, 'No implicit navigation or simplification claim')
    report = {'status': 'passed', 'assertionCount': count, 'sourceWays': len(net['ways']), 'sourceSegments': len(expected),
              'independentClippingAlgorithm': 'Cohen–Sutherland (builder uses Liang–Barsky)', 'maxProjectedEndpointError': max_error,
              'allVerticesAndPropertiesChecked': True, 'navigationCertified': False, 'formalGameTests': False}
    if write_report:
        (HERE/'verification').mkdir(exist_ok=True)
        (HERE/'verification/integrity-check.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--write-report', action='store_true')
    main(parser.parse_args().write_report)
