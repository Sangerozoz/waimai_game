#!/usr/bin/env python3
"""Bind final Tiled, actual loaded A2/B1 images and fresh movement evidence."""
import datetime
import hashlib
import json
import math
from pathlib import Path
from PIL import Image, ImageChops

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    target = HERE / 'delivery-verification.json'
    if target.exists():
        raise SystemExit('Verification already exists; preserve subsequent user work.')
    checks = []
    def ck(name, passed):
        checks.append({'check': name, 'passed': bool(passed)})
    static = read(HERE / 'static-record.json')
    graph = read(HERE / 'navigation/graph.json')
    raw = read(HERE / 'preview/browser-walkthrough.json')
    run = json.loads(raw['text'])
    state, samples = run['final'], run['samples']
    protected = read(HERE / 'protected-inputs.json')
    changed = [p for p, value in protected.items() if sha(Path(p)) != value]
    ck('all_old_inputs_unchanged', not changed)
    ck('approved_A2_and_B1_source_SHA', sha(Path(static['A2Source']['path'])) == static['A2Source']['sha256'] and sha(Path(static['B1Source']['path'])) == static['B1Source']['sha256'])
    ck('native_byte_copies_exact', (HERE / 'sources/A2-native.png').read_bytes() == Path(static['A2Source']['path']).read_bytes() and (HERE / 'sources/B1-native.png').read_bytes() == Path(static['B1Source']['path']).read_bytes())
    a = Image.open(HERE / 'sources/A2-native.png').convert('RGB')
    b = Image.open(HERE / 'sources/B1-native.png').convert('RGB')
    core_a = Image.open(HERE / 'tiled/A2-core.png').convert('RGB')
    core_b = Image.open(HERE / 'tiled/B1-core.png').convert('RGB')
    pair = Image.open(HERE / 'preview/pair-native-pixels.png').convert('RGB')
    rendered = Image.open(HERE / 'preview/tiled-cli-render-final.png').convert('RGBA')
    ck('actual_native_sizes', a.size == b.size == (1536, 1024))
    ck('lossless_pixel_core_crops', ImageChops.difference(a.crop((0, 0, 1504, 1024)), core_a).getbbox() is None and ImageChops.difference(b.crop((32, 0, 1536, 1024)), core_b).getbbox() is None)
    ck('no_double_offset_in_composite', ImageChops.difference(core_a, pair.crop((0, 0, 1504, 1024))).getbbox() is None and ImageChops.difference(core_b, pair.crop((1504, 0, 3008, 1024))).getbbox() is None)
    # RGB comparison avoids alpha-only bounding-box semantics hiding RGB differences.
    rgb_equal = rendered.size == pair.size and ImageChops.difference(rendered.convert('RGB'), pair).getbbox() is None
    ck('official_Tiled_render_exact_native_pixels', rgb_equal and rendered.getchannel('A').getextrema() == (255, 255))
    ck('runtime_bound_to_final_TMJSON', state['graphSourceSHA256'] == graph['sourceTiledSHA256'] == sha(HERE / 'tiled/compact-pair-a2-b1.tmj'))
    ck('graph_connectivity_explicit', len(graph['connectedComponents']) == 1 and not graph['duplicateEdges'] and not graph['unmergedCrossings'])
    image_proofs = state['loadedImages']
    expected = {i['elementId']: i for i in graph['images']}
    ck('runtime_really_loaded_two_correct_image_files', len(image_proofs) == len(expected) == 2 and all(p['displayed'] and p['sha256'] == expected[p['elementId']]['sha256'] and p['nativeSourceSHA256'] == expected[p['elementId']]['nativeSourceSHA256'] for p in image_proofs))
    ck('actual_arrival', raw['exitCode'] == 0 and state['ready'] and not state['playing'] and state['message'].startswith('已沿路线到达 B') and math.dist(state['position'], state['end']['point']) < 1e-6)
    ck('fresh_continuous_cross_region_samples', len(samples) > 10 and any(s['position'][0] < 1504 for s in samples) and any(s['position'][0] > 1504 for s in samples) and all(x['traveled'] <= y['traveled'] for x, y in zip(samples, samples[1:])))
    def distance_to_segment(point, start, end):
        delta = [end[k] - start[k] for k in (0, 1)]
        squared = sum(v * v for v in delta)
        t = max(0, min(1, sum((point[k] - start[k]) * delta[k] for k in (0, 1)) / squared)) if squared else 0
        return math.dist(point, [start[k] + t * delta[k] for k in (0, 1)])
    max_gap = max(min(distance_to_segment(s['position'], x, y) for e in graph['edges'] for x, y in zip(e['points'], e['points'][1:])) for s in samples)
    ck('all_samples_follow_exported_geometry', max_gap < 1e-6)
    sampled_pixels = [{'position': s['position'], 'nativeRGB': pair.getpixel((round(s['position'][0]), round(s['position'][1])))} for s in samples]
    contract = read(HERE / 'next-C/identity-and-edge-contract.json')
    ck('next_C_only_contract_and_reference_exists', not contract['nativeGenerated'] and contract['ImagesRequestsThisRound'] == 0 and (HERE / 'next-C' / contract['source']).resolve().is_file() and (HERE / 'next-C' / contract['actualNorthernBand']).is_file())
    ck('C_exit_width_interval_count', contract['portal']['asphaltWidthObservedNearBoundaryPixels'] == 706 - 653 + 1)
    runtime_images = [{'elementId': spec['elementId'], 'path': spec['file'], 'bytes': (HERE / 'navigation' / spec['file']).stat().st_size,
                       'sha256': sha(HERE / 'navigation' / spec['file']), 'nativeSourceSHA256': spec['nativeSourceSHA256'],
                       'size': spec['size'], 'globalOffset': spec['offset']} for spec in graph['images']]
    command = "QT_QPA_PLATFORM=cocoa /Applications/Tiled.app/Contents/MacOS/tmxrasterizer --hide-object-layers --no-smoothing --scale 1 '" + str(HERE / 'tiled/compact-pair-a2-b1.tmj') + "' '" + str(HERE / 'preview/tiled-cli-render-final.png') + "'"
    record = {
        'schemaVersion': 1, 'recordedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'approved-art-A2-B1-new-map-CLI-render-and-fresh-cross-region-navigation-demonstrated' if all(c['passed'] for c in checks) else 'blocked-verification-failed',
        'scope': 'Integration directory only. No Images request or other region generated. No game/business/save operations.',
        'artAcceptance': {'sourceReview': '../user-review-002.json', 'A2DensityAndDirectionAcceptedByUser': True, 'priorStyleColorsClarityProportionsBaseline': True, 'BIndependentCoreDensityAccepted': False, 'wholeCityAccepted': False},
        'sourceNatives': [static['A2Source'], static['B1Source']],
        'nativeArchiveCopiesByteForByte': True,
        'geometry': {'worldOffsets': static['imageOffsets'], 'coreBoundaryX': 1504, 'BLocalCropLeft': 32, 'overlapPixels': 64, 'nativeWarpMirrorRecolor': False,
                     'wholeBuildingCoreChoiceObserved': static['coreChoice'], 'visibleRoadJoinObservedAtOneToOne': True,
                     'groundTextureSeamNotClaimedPixelPerfect': True, 'roadsCorrectedOnlyInNewCopy': 'road-adjustments.json'},
        'tiled': {'path': 'tiled/compact-pair-a2-b1.tmj', 'sha256': sha(HERE / 'tiled/compact-pair-a2-b1.tmj'),
                  'officialCliRender': 'preview/tiled-cli-render-final.png', 'officialCliRenderSHA256': sha(HERE / 'preview/tiled-cli-render-final.png'),
                  'actualRasterSize': list(rendered.size), 'pixelIdenticalToLosslessCoreComposition': rgb_equal,
                  'actualCommand': command, 'renderExitCode': 0,
                  'nativeGUIWindowVerified': False, 'nativeGUIRepaintAttemptsThisRound': 0,
                  'initialTransparentOutputAndFix': 'tiled-metadata-fix.json',
                  'rootCause': 'Installed Tiled reader interprets omitted layer/group opacity as0; explicit opacity1 corrected only the new map.',
                  'offscreenPluginUnavailable': 'Installed build exposes cocoa only; official CLI rasterization used cocoa without GUI window takeover.'},
        'graph': {'path': 'navigation/graph.json', 'sha256': sha(HERE / 'navigation/graph.json'), 'sourceTiledSHA256': graph['sourceTiledSHA256'],
                  'nodeCount': len(graph['nodes']), 'edgeCount': len(graph['edges']), 'components': len(graph['connectedComponents']),
                  'duplicateEdges': graph['duplicateEdges'], 'unmergedCrossings': graph['unmergedCrossings'], 'offsetAppliedOnce': True, 'newBusinessBindings': 0},
        'runtimeImageReferences': {'uniquePNG': len(runtime_images), 'PNGBytes': sum(i['bytes'] for i in runtime_images), 'images': runtime_images,
                                   'nativeArchiveBytes': sum(i['bytes'] for i in [static['A2Source'], static['B1Source']]),
                                   'wholeRegionImagesNotSubjectToSprite280Limit': True},
        'freshNavigation': {'page': 'navigation/offline.html', 'pageSHA256': sha(HERE / 'navigation/offline.html'),
                            'browserBackend': 'BB local isolated headless', 'rawReadback': 'preview/browser-walkthrough.json',
                            'rawReadbackSHA256': sha(HERE / 'preview/browser-walkthrough.json'),
                            'screenshot': 'preview/navigation-arrival-A2-B1.jpg', 'screenshotSHA256': sha(HERE / 'preview/navigation-arrival-A2-B1.jpg'),
                            'sampleCount': len(samples), 'start': samples[0]['position'], 'end': state['position'],
                            'arrived': state['message'], 'traveledPixels': state['traveled'], 'routeEdgeIds': state['route']['edgeIds'],
                            'maxGapFromExportedPolylinePixels': max_gap, 'actualLoadedImageProof': image_proofs,
                            'sampledNativePixelsDiagnosticNotSemanticClassifier': sampled_pixels,
                            'beforeMetadataFixRunPreservedButNotUsedAsFinal': 'preview/browser-walkthrough-before-metadata-fix.json',
                            'usesOldScreenshotOrArrivalResult': False},
        'serving': {'existing4186RootDoesNotCoverThisDirectory': True, 'newServiceOrPortStarted': False, 'workingFallback': 'self-contained local navigation/offline.html'},
        'nextC': {'contract': 'next-C/identity-and-edge-contract.json', 'referenceBand': 'next-C/actual-north-edge-64.png', 'ImagesRequests': 0, 'metresEstablished': False, 'finalGridFrozen': False},
        'protection': {'snapshot': 'protected-inputs.json', 'count': len(protected), 'changedInputs': changed, 'oldInputsRestoredOrWritten': False},
        'checks': checks, 'failedChecks': [c['check'] for c in checks if not c['passed']],
        'notClaimed': ['native Tiled GUI window rendering', 'formal game integration or stage tests', 'orders/save operations', 'whole city completion', 'C artwork generated', 'precise world-metre calibration'],
        'lease': 'Returned at handoff; parent restores default. No continuation without a new bounded lease.'}
    target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': record['status'], 'failedChecks': record['failedChecks'], 'TiledSHA256': record['tiled']['sha256'],
                      'graphSHA256': record['graph']['sha256'], 'runtimeUniquePNG': len(runtime_images),
                      'runtimePNGBytes': record['runtimeImageReferences']['PNGBytes'], 'actualSampleCount': len(samples),
                      'arrived': record['freshNavigation']['arrived'], 'TiledPixelsEqual': rgb_equal, 'changedOldInputs': changed,
                      'ImagesRequests': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
