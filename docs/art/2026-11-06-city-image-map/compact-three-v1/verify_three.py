#!/usr/bin/env python3
"""Verify actual new C artwork, immutable A/B, official render and fresh C-A-B movement."""
import datetime
import hashlib
import json
import math
from pathlib import Path
from PIL import Image, ImageChops

HERE = Path(__file__).resolve().parent
CITY = HERE.parent
BASE = CITY / 'compact-pair-v2-density/integration'
CROOT = CITY / 'regions/C-001'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text())


def main():
    output = HERE / 'delivery-verification.json'
    if output.exists():
        raise SystemExit('Verification exists; do not overwrite subsequent work.')
    checks = []
    def ck(name, value):
        checks.append({'check': name, 'passed': bool(value)})
    graph = read(HERE / 'navigation/graph.json')
    static = read(HERE / 'static-record.json')
    provenance = read(CROOT / 'provenance.json')
    request = read(CROOT / 'request-started.json')
    browser = read(HERE / 'preview/browser-walkthrough.json')
    movement = json.loads(browser['text'])
    final, samples = movement['final'], movement['samples']
    ck('one_actual_C_request', request['n'] == 1 and request['maxRetries'] == 0 and (CROOT / 'native.png').is_file())
    ck('C_returned_native_SHA', sha(CROOT / 'native.png') == provenance['nativeSHA256'])
    ck('all_real_submitted_inputs_unchanged', all(sha(Path(i['path'])) == i['sha256'] for i in provenance['inputs']))
    c = Image.open(CROOT / 'native.png').convert('RGB')
    core = Image.open(HERE / 'tiled/C-core.png').convert('RGB')
    ck('C_native_1536x1024_and_lossless_core', c.size == (1536, 1024) and ImageChops.difference(c.crop((0, 64, 1536, 1024)), core).getbbox() is None)
    ck('A2_B1_core_bytes_unchanged', all((HERE / 'tiled' / p).read_bytes() == (BASE / 'tiled' / p).read_bytes() for p in ['A2-core.png', 'B1-core.png']))
    old_graph = read(BASE / 'navigation/graph.json')
    ck('A2_B1_road_data_unchanged', graph['edges'][:len(old_graph['edges'])] == old_graph['edges'])
    ck('C_join_merged_at_actual_old_exit', len([n for n in graph['nodes'] if n['pixel'] == [679.5, 1024]]) == 1)
    ck('new_graph_connected_no_duplicate_or_unmerged_crossing', len(graph['connectedComponents']) == 1 and not graph['duplicateEdges'] and not graph['unmergedCrossings'])
    pair = Image.open(HERE / 'preview/three-native-pixels.png').convert('RGB')
    render = Image.open(HERE / 'preview/tiled-cli-three.png').convert('RGBA')
    exact_render = render.size == pair.size and ImageChops.difference(render.convert('RGB'), pair).getbbox() is None
    ck('official_Tiled_render_pixel_exact', exact_render and render.getchannel('A').getextrema() == (255, 255))
    ck('browser_binds_final_new_TMJ', final['graphSourceSHA256'] == graph['sourceTiledSHA256'] == sha(HERE / 'tiled/compact-three.tmj'))
    specs = {i['elementId']: i for i in graph['images']}
    ck('actual_images_loaded_and_SHA_checked', len(final['loadedImages']) == len(specs) and all(i['displayed'] and i['sha256'] == specs[i['elementId']]['sha256'] and i['nativeSourceSHA256'] == specs[i['elementId']]['nativeSourceSHA256'] for i in final['loadedImages']))
    ck('new_C_is_loaded_not_old_two_region_replay', any(i['elementId'] == 'cityC' and i['nativeSourceSHA256'] == provenance['nativeSHA256'] for i in final['loadedImages']))
    sequence = []
    for sample in samples:
        x, y = sample['position']
        region = 'C' if y >= 1024 and x < 1536 else ('A2' if y < 1024 and x < 1504 else ('B1' if y < 1024 else 'unproduced-D'))
        if not sequence or sequence[-1] != region:
            sequence.append(region)
    ck('actual_continuous_C_A2_B1_order', sequence == ['C', 'A2', 'B1'] and len(samples) > 15)
    ck('actual_new_arrival', browser['exitCode'] == 0 and final['ready'] and not final['playing'] and final['message'].startswith('已沿路线到达 B') and math.dist(final['position'], final['end']['point']) < 1e-6)
    def segment_gap(p, a, b):
        d = [b[k] - a[k] for k in (0, 1)]; length = sum(x*x for x in d)
        t = max(0, min(1, sum((p[k]-a[k])*d[k] for k in (0, 1))/length)) if length else 0
        return math.dist(p, [a[k]+t*d[k] for k in (0, 1)])
    max_gap = max(min(segment_gap(s['position'], a, b) for e in graph['edges'] for a, b in zip(e['points'], e['points'][1:])) for s in samples)
    ck('samples_follow_new_vector_geometry', max_gap < 1e-6 and all(a['traveled'] <= b['traveled'] for a,b in zip(samples,samples[1:])))
    protected = read(HERE / 'protected-inputs.json')
    changed = [{'path': p, 'beforeSHA256': value, 'currentSHA256': sha(Path(p))} for p,value in protected.items() if sha(Path(p)) != value]
    shared_path = str(CITY / 'planning/progress-current.json')
    immutable_changes = [i for i in changed if i['path'] != shared_path]
    ck('immutable_old_inputs_unchanged', not immutable_changes)
    rows = []
    for spec in graph['images']:
        p = (HERE / 'navigation' / spec['file']).resolve()
        rows.append({**spec, 'bytes': p.stat().st_size, 'actualSHA256': sha(p)})
    art_rows = [r for r in rows if r['role'] == 'region-art']
    ck('exactly_three_region_images_plus_explicit_D_status', len(art_rows) == 3 and len(rows) == 4 and not graph['DProduced'])
    record = {
        'schemaVersion': 1, 'recordedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'three-regions-admitted-official-render-and-fresh-C-A2-B1-navigation-demonstrated' if all(c['passed'] for c in checks) else 'blocked-verification-failed',
        'independentNativeRegionsProduced': 3, 'actualAdmittedRegions': ['A2', 'B1', 'C-001'],
        'artAcceptance': {'A2DensityAndDirectionApproved': True, 'CUserAccepted': False, 'wholeCityAccepted': False},
        'CNative': {'path': '../regions/C-001/native.png', 'sha256': sha(CROOT / 'native.png'), 'bytes': (CROOT / 'native.png').stat().st_size,
                    'actualSize': list(c.size), 'provenance': '../regions/C-001/provenance.json',
                    'actualRequestCommand': '../regions/C-001/execution-commands.json', 'ImagesRequests': 1, 'automaticRetries': 0,
                    'qualityRequested': provenance['qualityRequested'], 'qualityReturned': provenance['qualityReturned'],
                    'originalReturnedBytesPreserved': True, 'inputReferenceCount': len(provenance['inputs'])},
        'geometry': {'offsets': {'A2': [0, 0], 'B1': [1472, 0], 'C': [0, 960]}, 'CNativeCropBox': [0, 64, 1536, 1024],
                     'CVisibleCoreStartsAtGlobalY': 1024, 'sharedPortalGlobal': [679.5, 1024],
                     'CObservedNorthAsphaltIntervalAtY64': [653, 705], 'CObservedNorthCenterX': (653+705)/2,
                     'A2ObservedLastRowAsphaltInterval': [653,706], 'referenceCenterDifferencePixels': abs((653+705)/2-679.5),
                     'boundaryWidthDifferencePixels': (706-653+1)-(705-653+1),
                     'wholeBuildingsNotClippedAtCoreLineObserved': True, 'roadJoinVisuallyContinuousAtOneToOne': True,
                     'nativeWarpRotateRecolorOrRoadPainting': False, 'geometryUnits': 'pixels-not-metres'},
        'map': {'path': 'tiled/compact-three.tmj', 'sha256': sha(HERE / 'tiled/compact-three.tmj'),
                'officialRender': 'preview/tiled-cli-three.png', 'officialRenderSHA256': sha(HERE / 'preview/tiled-cli-three.png'),
                'actualRenderSize': list(render.size), 'RGBPixelEqualToNativeCoreComposition': exact_render,
                'explicitOpacityOneOnVisibleLayers': True, 'TiledGUIVerified': False,
                'renderCommand': "QT_QPA_PLATFORM=cocoa /Applications/Tiled.app/Contents/MacOS/tmxrasterizer --hide-object-layers --no-smoothing --scale 1 '" + str(HERE / 'tiled/compact-three.tmj') + "' '" + str(HERE / 'preview/tiled-cli-three.png') + "'"},
        'graph': {'path': 'navigation/graph.json', 'sha256': sha(HERE / 'navigation/graph.json'), 'nodes': len(graph['nodes']),
                  'edges': len(graph['edges']), 'components': len(graph['connectedComponents']), 'duplicateEdges': graph['duplicateEdges'],
                  'unmergedCrossings': graph['unmergedCrossings'], 'offsetAppliedOnce': True, 'newBusinessBindings': 0},
        'runtimeImages': {'regionPNGCount': len(art_rows), 'regionPNGBytes': sum(r['bytes'] for r in art_rows),
                          'allReferencedPNGIncludingUIStatusPlate': len(rows), 'allReferencedPNGBytes': sum(r['bytes'] for r in rows),
                          'files': rows, 'DStatusPlateIsNotNativeRegionOrGeneratedArtwork': True},
        'newNavigation': {'page': 'navigation/offline.html', 'pageSHA256': sha(HERE / 'navigation/offline.html'),
                          'rawEvidence': 'preview/browser-walkthrough.json', 'rawEvidenceSHA256': sha(HERE / 'preview/browser-walkthrough.json'),
                          'screenshot': 'preview/navigation-C-A2-B1-arrival.jpg', 'screenshotSHA256': sha(HERE / 'preview/navigation-C-A2-B1-arrival.jpg'),
                          'sampleCount': len(samples), 'actualRegionOrder': sequence, 'start': samples[0]['position'], 'end': final['position'],
                          'traveledPixels': final['traveled'], 'routeEdgeIds': final['route']['edgeIds'], 'maximumGapFromExportedRoadPixels': max_gap,
                          'arrivalMessage': final['message'], 'loadedImages': final['loadedImages'], 'oldTwoRegionEvidenceReusedAsNew': False,
                          'markerABMeaning': 'A/B labels are generic start/end markers; actual region sequence is C->A2->B1.'},
        'protection': {'snapshot': 'protected-inputs.json', 'immutableChanged': immutable_changes,
                       'liveParentProgressChangesObservedSeparately': [i for i in changed if i['path'] == shared_path],
                       'parentProgressIndexWrittenOrRestoredByThisThread': False, 'oldA2B1MapOrRoadsWritten': False},
        'notProducedOrPerformed': ['D or another region native', 'A/B regeneration', 'new engine/service/port', 'GUI repaint matrix',
                                   'formal game tests/typecheck/regression/FPS', 'orders/save/purchase operations', 'commit/push'],
        'DUnproducedAreaExplicitlyMarked': True, 'newWorldMetresCalibrated': False, 'finalGridFrozen': False,
        'checks': checks, 'failedChecks': [c['check'] for c in checks if not c['passed']],
        'handoff': 'Bounded C-only production/integration lease returned; parent restores default. No D production.'}
    output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': record['status'], 'failedChecks': record['failedChecks'], 'nativeRegions': 3,
                      'admittedRegions': 3, 'nodes': len(graph['nodes']), 'edges': len(graph['edges']),
                      'sampleCount': len(samples), 'actualRegionOrder': sequence, 'officialRenderPixelsEqual': exact_render,
                      'regionPNGBytes': record['runtimeImages']['regionPNGBytes'],
                      'allPNGBytesIncludingDStatus': record['runtimeImages']['allReferencedPNGBytes'],
                      'immutableChanged': immutable_changes, 'CNativeSHA256': provenance['nativeSHA256'],
                      'newMapSHA256': record['map']['sha256'], 'newGraphSHA256': record['graph']['sha256']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
