#!/usr/bin/env python3
"""Copy a source OSM window without designing, snapping or simplifying roads."""
import collections
import hashlib
import html
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'AGENTS.md').exists())
SOURCE = ROOT / 'delivery-game/data/map-sample'
LAT, LON = 36.235, 137.985
SX, SY = 111320 * math.cos(math.radians(LAT)), 111320
TAG_KEYS = {'highway', 'bridge', 'tunnel', 'layer', 'oneway', 'oneway:bicycle',
            'junction', 'access', 'vehicle', 'motor_vehicle', 'motorcar', 'bicycle',
            'foot', 'service', 'width', 'lanes', 'area', 'covered', 'level',
            'oneway:conditional', 'access:conditional', 'motor_vehicle:conditional'}
MAJOR = {'motorway', 'trunk', 'primary', 'secondary', 'motorway_link', 'trunk_link',
         'primary_link', 'secondary_link'}
STREET = {'tertiary', 'tertiary_link', 'residential', 'unclassified', 'living_street', 'road'}


def digest(p):
    return {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}


def dump(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def category(kind):
    return 'major' if kind in MAJOR else 'street' if kind in STREET else 'service' if kind == 'service' else 'nonvehicle'


def clip(a, b, box):
    """Liang–Barsky, preserving the source segment's parameter."""
    dx, dy = b[0]-a[0], b[1]-a[1]
    lo, hi = 0., 1.
    for p, q in [(-dx, a[0]-box[0]), (dx, box[2]-a[0]),
                 (-dy, a[1]-box[1]), (dy, box[3]-a[1])]:
        if p == 0:
            if q < 0:
                return None
        else:
            r = q/p
            if p < 0:
                lo = max(lo, r)
            else:
                hi = min(hi, r)
            if lo > hi:
                return None
    return (lo, hi) if hi-lo > 1e-12 else None


def main():
    previous = HERE / 'generated-files.json'
    if previous.exists():
        for name, ref in json.loads(previous.read_text())['files'].items():
            if digest(HERE/name) != ref:
                raise RuntimeError('Owned output changed; archive/review before rebuilding: '+name)
    outputs = ['selection.json', 'source-provenance.json', 'source-extract.osm', 'network.json',
               'roads.geojson', 'context.json', 'roads.svg', 'index.html', 'statistics.json']
    if not previous.exists():
        assert not any((HERE/n).exists() for n in outputs), 'Unowned output already exists'
    meta = json.loads((SOURCE/'source.json').read_text())
    expected = {'source.osm': meta['sha256'], 'city-roads.osm': meta['additionalSources'][0]['sha256']}
    nodes, ways = {}, {}
    for name, sha in expected.items():
        assert digest(SOURCE/name)['sha256'] == sha, name
        root = ET.parse(SOURCE/name).getroot()
        nodes.update({n.get('id'): {'lon': n.get('lon'), 'lat': n.get('lat')} for n in root.findall('node')})
        ways.update({w.get('id'): {'refs': [n.get('ref') for n in w.findall('nd')],
                                 'tags': {t.get('k'): t.get('v') for t in w.findall('tag')}}
                     for w in root.findall('way')})
    xy = {n: [(float(p['lon'])-LON)*SX, (float(p['lat'])-LAT)*SY] for n, p in nodes.items()}
    zoning_path = ROOT/'docs/art/2026-11-02-county-zoning/selection.json'
    old = json.loads(zoning_path.read_text())['regions']['map']['worldBoundsMetresApprox']
    cx, cy = (old['minX']+old['maxX'])/2, (old['minY']+old['maxY'])/2
    width, height = (old['maxX']-old['minX'])/2, (old['maxY']-old['minY'])/2
    box = [cx-width/2, cy-height/2, cx+width/2, cy+height/2]
    selection = {'role': 'source-reference-window-only-not-new-game-boundary', 'region': 'Central Matsumoto, Japan',
                 'oldApproxRedBounds': old, 'sourceProjectedBounds': box, 'sourceProjectedSize': [width, height],
                 'sourceApproxAreaKm2': width*height/1e6, 'areaRatioToOldApproxRedRectangle': .25,
                 'osmBboxWestSouthEastNorth': [LON+box[0]/SX, LAT+box[1]/SY, LON+box[2]/SX, LAT+box[3]/SY],
                 'projection': {'kind': 'inherited local equirectangular approximation', 'originLat': LAT, 'originLon': LON,
                                'xMetresPerDegree': SX, 'yMetresPerDegree': SY,
                                'screenTransform': 'x = sourceX - minX; y = maxY - sourceY; no road rearrangement'},
                 'newArtworkMetreCalibration': None, 'newCityPartitionFrozen': False, 'formalGameTests': False}
    graph_nodes, edges, road_parts, used_ways = {}, [], [], {}
    for wid, way in sorted(ways.items(), key=lambda item: int(item[0])):
        tags = way['tags']
        if 'highway' not in tags:
            continue
        if any(n not in xy for n in way['refs']):
            raise ValueError('Missing source node in highway '+wid)
        parts = []
        for i, (na, nb) in enumerate(zip(way['refs'], way['refs'][1:])):
            a, b = xy[na], xy[nb]
            if a == b:
                continue
            interval = clip(a, b, box)
            if interval is None:
                continue
            lo, hi = interval
            ids = []
            for end, t in enumerate(interval):
                key = 'osm:'+na if t == 0 else 'osm:'+nb if t == 1 else f'cut:{wid}:{i}:{end}'
                point = [a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1])]
                geo = [LON+point[0]/SX, LAT+point[1]/SY]
                entry = {'xy': point, 'lonLat': geo, 'sourceNodeId': key[4:] if key.startswith('osm:') else None,
                         'boundaryCut': key.startswith('cut:')}
                if key in graph_nodes:
                    assert math.dist(graph_nodes[key]['xy'], point) < 1e-7
                graph_nodes[key] = entry
                ids.append(key)
            edge = {'wayId': wid, 'sourceSegmentIndex': i, 'sourceNodeIds': [na, nb],
                    'a': ids[0], 'b': ids[1], 'sourceParameterInterval': [lo, hi]}
            edges.append(edge)
            if parts and parts[-1][-1] == ids[0]:
                parts[-1].append(ids[1])
            else:
                parts.append(ids)
        if parts:
            kept_tags = {k: v for k, v in tags.items() if k in TAG_KEYS}
            used_ways[wid] = {'sourceNodeIds': way['refs'], 'tags': kept_tags, 'category': category(tags['highway'])}
            for j, part in enumerate(parts):
                road_parts.append({'wayId': wid, 'partIndex': j, 'nodes': part})
    graph = {'kind': 'source-geometry-evidence-not-routing-profile', 'selection': selection,
             'nodes': graph_nodes, 'segments': edges, 'ways': used_ways, 'parts': road_parts,
             'geometricCrossingsMerged': False, 'turnRestrictionsImported': False,
             'sourceTagWhitelist': sorted(TAG_KEYS), 'navigationCertified': False,
             'allIntersectingHighwayWaysKept': True, 'simplificationTolerance': 0}
    features = []
    for part in road_parts:
        way = used_ways[part['wayId']]
        features.append({'type': 'Feature', 'id': part['wayId']+':'+str(part['partIndex']),
                         'properties': {'osmWayId': part['wayId'], 'partIndex': part['partIndex'],
                                        'pointKeys': part['nodes'], 'category': way['category'], **way['tags']},
                         'geometry': {'type': 'LineString', 'coordinates': [graph_nodes[n]['lonLat'] for n in part['nodes']]}})
    geojson = {'type': 'FeatureCollection', 'name': 'Matsumoto source road window',
               'licence': 'ODbL-1.0', 'attribution': '© OpenStreetMap contributors', 'features': features}
    extract = ET.Element('osm', {'version': '0.6', 'generator': 'offline-source-window-evidence',
                                'copyright': 'OpenStreetMap and contributors', 'license': 'https://opendatacommons.org/licenses/odbl/1-0/'})
    ET.SubElement(extract, 'note').text = 'Reconstructed XML subset preserving selected complete way node sequences and original coordinates, including exterior points, plus whitelisted way tags only. Node tags (including barriers), other way tags, relations, versions, users and changeset metadata are omitted. No synthetic boundary nodes in this XML. The full original source XML remains at the recorded project source paths. See selection.json for clipping window.'
    for nid in sorted({n for w in used_ways.values() for n in w['sourceNodeIds']}, key=int):
        ET.SubElement(extract, 'node', {'id': nid, **nodes[nid]})
    for wid, way in used_ways.items():
        w = ET.SubElement(extract, 'way', {'id': wid})
        for nid in way['sourceNodeIds']:
            ET.SubElement(w, 'nd', {'ref': nid})
        for k, v in sorted(way['tags'].items()):
            ET.SubElement(w, 'tag', {'k': k, 'v': v})
    ET.indent(extract)
    (HERE/'source-extract.osm').write_bytes(ET.tostring(extract, encoding='utf-8', xml_declaration=True))
    city_path = ROOT/'delivery-game/assets/resources/map-sample/city.json'
    city = json.loads(city_path.read_text())
    def overlaps(ps):
        return min(p[0] for p in ps) <= box[2] and max(p[0] for p in ps) >= box[0] and min(p[1] for p in ps) <= box[3] and max(p[1] for p in ps) >= box[1]
    context = {'buildings': [ps for ps in city['buildings'] if overlaps(ps)],
               'areas': [a for a in city['areas'] if overlaps(a['points'])],
               'waterways': [ps for ps in city['waterways'] if overlaps(ps)],
               'buildingCoverageComplete': False, 'source': str(city_path.relative_to(ROOT))}
    adjacency = collections.defaultdict(set)
    for e in edges:
        if used_ways[e['wayId']]['category'] == 'nonvehicle':
            continue
        adjacency[e['a']].add(e['b']); adjacency[e['b']].add(e['a'])
    stats = {'sourceHighwayWays': len(used_ways), 'clippedPolylineParts': len(road_parts),
             'preservedSourceSegments': len(edges), 'geometricNodesIncludingBoundaryCuts': len(graph_nodes),
             'sourceNodeIdentities': sum(not n['boundaryCut'] for n in graph_nodes.values()),
             'boundaryCutPoints': sum(n['boundaryCut'] for n in graph_nodes.values()),
             'wayCountsByHighway': dict(collections.Counter(w['tags']['highway'] for w in used_ways.values())),
             'wayCountsByDisplayCategory': dict(collections.Counter(w['category'] for w in used_ways.values())),
             'sourceNodeDegreeHistogramMotorGeometryOnly': dict(collections.Counter(len(v) for k, v in adjacency.items() if not graph_nodes[k]['boundaryCut'])),
             'retainedBuildingFootprints': len(context['buildings']), 'navigationOrActualBlockCountClaimed': False}
    provenance = {'region': 'Central Matsumoto, Japan', 'dataOrigin': 'locally retained OpenStreetMap XML',
                  'retrievedDatesFromExistingRecord': ['2026-10-27', '2026-10-28'], 'networkDownloadsThisIncrement': 0,
                  'sourceFiles': {str((SOURCE/n).relative_to(ROOT)): digest(SOURCE/n) for n in ['source.osm', 'city-roads.osm', 'source.json', 'README.md']},
                  'importerReadOnly': {'path': 'delivery-game/scripts/import-map-sample.py', **digest(ROOT/'delivery-game/scripts/import-map-sample.py')},
                  'contextSource': {'path': str(city_path.relative_to(ROOT)), **digest(city_path)},
                  'approxZoningSource': {'path': str(zoning_path.relative_to(ROOT)), **digest(zoning_path)},
                  'attribution': '© OpenStreetMap contributors', 'licence': 'ODbL 1.0',
                  'licenceURL': 'https://opendatacommons.org/licenses/odbl/1-0/',
                  'copyrightURL': 'https://www.openstreetmap.org/copyright',
                  'osmReferenceURL': f'https://www.openstreetmap.org/#map=16/{LAT+cy/SY:.7f}/{LON+cx/SX:.7f}',
                  'widthsAreDisplayClassesNotMeasuredMetres': True, 'imageryGenerated': False,
                  'xmlSubsetNature': 'reconstructed subset preserving original geometry and whitelisted way tags; not a full original OSM copy',
                  'xmlSubsetOmissions': ['all node tags including barriers/gates', 'non-whitelisted way tags including road names', 'relations including turn restrictions', 'versions/users/changeset metadata'],
                  'preserved': ['source way IDs', 'source node IDs', 'all intermediate vertices', 'original adjacency by node identity', 'whitelisted access/oneway/bridge/layer tags'],
                  'notCertified': ['source completeness or current field conditions', 'turn restrictions', 'vehicle access', 'new artwork metre scale', 'new-city zoning', 'navigation', 'game acceptance']}
    dump('selection.json', selection); dump('source-provenance.json', provenance)
    dump('network.json', graph); dump('roads.geojson', geojson); dump('context.json', context); dump('statistics.json', stats)
    sw = {'major': 8, 'street': 4.6, 'service': 2.8, 'nonvehicle': 1.4}
    colors = {'major': '#ab6648', 'street': '#687478', 'service': '#9da6a5', 'nonvehicle': '#a9aaa3'}
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="松本市真实道路原形选区">',
           '<rect width="100%" height="100%" fill="#f3f1e9"/>']
    for cat in ['nonvehicle', 'service', 'street', 'major']:
        for part in road_parts:
            if used_ways[part['wayId']]['category'] != cat:
                continue
            ps = [graph_nodes[n]['xy'] for n in part['nodes']]
            pts = ' '.join(f'{x-box[0]:.7f},{box[3]-y:.7f}' for x, y in ps)
            dash = ' stroke-dasharray="3 3"' if cat == 'nonvehicle' else ''
            svg.append(f'<polyline points="{pts}" fill="none" stroke="{colors[cat]}" stroke-width="{sw[cat]}" stroke-linecap="round" stroke-linejoin="round"{dash}><title>OSM way {html.escape(part["wayId"])}</title></polyline>')
    svg.append(f'<text x="20" y="{height-20}" font-size="17" fill="#4e595a">© OpenStreetMap contributors · ODbL 1.0 · 线宽仅示意</text></svg>')
    (HERE/'roads.svg').write_text('\n'.join(svg)+'\n')
    payload = {'network': graph, 'context': context, 'statistics': stats, 'provenance': provenance}
    template = (HERE/'viewer-template.html').read_text()
    (HERE/'index.html').write_text(template.replace('/*__DATA__*/null', json.dumps(payload, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')))
    dump('generated-files.json', {'scope': 'owned generated evidence outputs only', 'files': {n: digest(HERE/n) for n in outputs}})
    print(json.dumps(stats, ensure_ascii=False))


if __name__ == '__main__':
    main()
